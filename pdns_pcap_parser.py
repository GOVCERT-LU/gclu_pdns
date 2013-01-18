#!/usr/bin/env python

# Copyright (c) 2013 GOVCERT.LU / Georges Toth & Foetz Guy

import sys
import re
from optparse import OptionParser
import ConfigParser
import mmap
from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import and_
import sqlalchemy
from sqlalchemy.sql.expression import case, exists
from db_model import Base, Session, Domain, Entry, Parent_Domain, Sensor, Sensor_Domain, DNS_Server
from multiprocessing import Pool
import multiprocessing
import traceback


filter_rrtype = {'a' : 1, 'aaaa' : 28, 'cname' : 5, 'ns' : 2, 'mx' : 15, 'soa' : 6}
filter_res_lengths = [5, 6, 11]
filter_unwanted_rrtype = [15, 50, 46, 43, 47, 12]
sensor_name = ""
records = {}
cl_records = {}


class BaseEntry(object):
  def __init__(self, date):
    self.fs = date
    self.ls = date
    self.oid = None

class MParentDomain(BaseEntry):
  def __init__(self, name, date):
    super(MParentDomain, self).__init__(date)
    self.name = name
    self.domains = {}

  def update(self, srv, domain, rr, ttl, value, date):
    if date < self.fs:
      self.fs = date
    elif date > self.ls:
      self.ld = date

    if not domain in self.domains:
      d = MDomain(domain, date)
      self.domains[domain] = d

    self.domains[domain].update(srv, rr, ttl, value, date)

    return self.domains[domain]

  def __str__(self):
    ret = 'Parent: {0}'.format(self.name)
    for k, v in self.domains.items():
      ret += '{0}\n'.format(v)

    return ret

  def pushDB(self, db):
    q = db.query(Parent_Domain.parent_domain_id)
    q = q.filter(Parent_Domain.parent_domain_name == self.name)
    res = q.all()

    if len(res) == 0:
      o = Parent_Domain()
      o.parent_domain_name = self.name
      db.add(o)
      db.flush()

      self.oid = o.parent_domain_id
    else:
      self.oid = res[0][0]

    return self.oid

def db_add_parent(sensor_id, i, db_url):
  db = init_db(db_url)
  ids = {}
  dids = {}

  for pdomain, mpdomain in i.items():
    ids[pdomain] = mpdomain.pushDB(db)

    for domain, mdomain in mpdomain.domains.items():
      dids[domain] = mdomain.pushDB(db, sensor_id, ids[pdomain])

      for rr, rrs in mdomain.rrs.items():
        for value, entry in rrs.items():
          try:
            entry.pushDB(db, dids[domain], rr, value)
          except:
            traceback.print_exc(file=sys.stdout)
            raise

  return ids

class MDomain(BaseEntry):
  def __init__(self, name, date):
    super(MDomain, self).__init__(date)
    self.name = name
    self.rrs = {}

  def update(self, srv, rr, ttl, value, date):
    if date < self.fs:
      self.fs = date
    elif date > self.ls:
      self.ld = date

    if not rr in self.rrs:
      self.rrs[rr] = {}

    if value in self.rrs[rr]:
      self.rrs[rr][value].update(srv, ttl, date)
    else:
      v = MEntry(srv, ttl, date)
      self.rrs[rr][value] = v

  def __str__(self):
    ret = '  Domain: {0}'.format(self.name)
    for k in self.rrs:
      ret += '\n    {0}'.format(k)
      for l, v1 in self.rrs[k].items():
        ret += '\n    {0} {1}'.format(l, v1)

    return ret

  def pushDB(self, db, sensor_id, parent_domain_id):
    q = db.query(Domain.domain_id)
    q = q.filter(and_(Domain.parent_domain_id == parent_domain_id, Domain.domain_name == self.name))
    res = q.all()

    if len(res) == 0:
      o = Domain()
      o.domain_name = self.name
      o.parent_domain_id = parent_domain_id
      db.add(o)
      db.flush()

      self.oid = o.domain_id

      sd = Sensor_Domain()
      sd.domain_id  = self.oid
      sd.sensor_id  = sensor_id
      sd.first_seen = self.fs
      sd.last_seen  = self.ls

      db.add(sd)
      db.flush()
    else:
      self.oid = res[0][0]

      q = db.query(Sensor_Domain)
      q = q.filter(and_(Sensor_Domain.domain_id == self.oid, Sensor_Domain.sensor_id == sensor_id))
      q.update({Sensor_Domain.first_seen : case([(Sensor_Domain.first_seen > self.fs, self.fs)], else_=Sensor_Domain.first_seen),
                Sensor_Domain.last_seen : case([(Sensor_Domain.last_seen < self.ls, self.ls)], else_=Sensor_Domain.last_seen)}, synchronize_session=False)


    return self.oid


class MEntry(object):
  def __init__(self, srv, ttl, date):
    #                  0  1     2     3
    self.ttls = {ttl: [1, date, date, {srv: [1, date, date]}]}

  def update(self, srv, ttl, date):
    if ttl in self.ttls:
      o = self.ttls[ttl]
      # first-seen
      if date < o[1]:
        o[1] = date
      # last-seen
      elif date > o[2]:
        o[2] = date

      o[0] += 1

      if srv in o[3]:
        if date < o[3][srv][1]:
          o[3][srv][1] = date
        elif date > o[3][srv][2]:
          o[3][srv][2] = date

        o[3][srv][0] += 1
      else:
        o[3][srv] = [1, date, date]
    else:
      self.ttls[ttl] = [1, date, date, {srv: [1, date, date]}]

  def __str__(self):
    ret = '['
    for k in self.ttls:
      ret += ' {0}'.format(k)
    ret += ' ]'

    return ret

  def pushDB(self, db, domain_id, rr, value):
    rr = filter_rrtype[rr]

    for ttl, v in self.ttls.items():
      oid = None

      try:
        q = db.query(Entry)
        q = q.filter(and_(Entry.domain_id == domain_id, Entry.type == rr, Entry.ttl == ttl,  Entry.value == value))
        q.update({Entry.first_seen : case([(Entry.first_seen > v[1], v[1])], else_=Entry.first_seen),
                  Entry.last_seen : case([(Entry.last_seen < v[2], v[2])], else_=Entry.last_seen),
                  Entry.count : Entry.count + v[0]}, synchronize_session=False)

        q = db.query(Entry.entry_id)
        o = q.filter(and_(Entry.domain_id == domain_id, Entry.type == rr, Entry.ttl == ttl,  Entry.value == value)).one()

        oid = o[0]
      except NoResultFound:
        entry = Entry()
        entry.domain_id = domain_id
        entry.type = rr
        entry.ttl = ttl
        entry.value = value
        entry.first_seen = v[1]
        entry.last_seen = v[2]
        entry.count = v[0]
        db.add(entry)
        db.flush()

        oid = entry.entry_id

      for s, sv in v[3].items():
        try:
          q = db.query(exists().where((and_(DNS_Server.entry_id == oid, DNS_Server.ip == s)))).scalar()

          if not q:
            raise NoResultFound('')

          q = db.query(DNS_Server)
          q = q.filter(and_(DNS_Server.entry_id == oid, DNS_Server.ip == s))
          q.update({DNS_Server.first_seen : case([(DNS_Server.first_seen > sv[1], sv[1])], else_=DNS_Server.first_seen),
                    DNS_Server.last_seen : case([(DNS_Server.last_seen < sv[2], sv[2])], else_=DNS_Server.last_seen),
                    DNS_Server.count : DNS_Server.count + sv[0]}, synchronize_session=False)

        except NoResultFound:
          dns_server = DNS_Server()
          dns_server.entry_id = oid
          dns_server.ip = s
          dns_server.first_seen = sv[1]
          dns_server.last_seen = sv[2]
          dns_server.count = sv[0]
          db.add(dns_server)
          db.flush()

    db.flush()


def process_record(date, ans, serv):
  '''
  dict layout:
    records[ <second-level domain> ][ <domain> ][ <rr> ][ <value> ] = [ <entity> ]
  '''
  pref = 0

  if len(ans) == 5:
    domain, undef, rr, ttl, value = ans
  elif len(ans) == 6:
    domain, undef, rr, ttl, pref, value = ans
    value = pref + ',' + value
  else:
    return

  # Get the second-level domain
  try:
    p = domain.split('.')

    if len(p) > 2:
      parent = p[-2] + '.' + p[-1]
    else:
      parent = domain
  except:
    parent = domain


  if not parent in cl_records:
    cl_records[parent] = MParentDomain(parent, date)

  cl_records[parent].update(serv, domain, rr, ttl, value, date)


def csvdump(recs, sep='|', print_title=True):
  if print_title:
    print 'domain' + sep + 'server' + sep + 'rr' + sep + 'ttl' + sep + 'value' + sep + 'firstseen' + sep + 'lastseen' + sep + 'matches'

  for pdomain, v in recs.items():
    for domain, d in v.domains.items():
      for rr, vals in d.rrs.items():
        for value, entry in vals.items():
          for ttl, info in entry.ttls.items():
            for srv in info[3].keys():
              print ('{0}' + sep + '{1}' + sep + '{2}' + sep + '{3}' + sep + '{4}' + sep + '{5}' + sep + '{6}' + sep + '{7}').format(domain, srv, rr, ttl, value, info[1], info[2], info[0])



# initialize DB connection and create DB if not exist
def init_db(db_url):
  __all__ = ['Session', 'Base']

  db = sqlalchemy.create_engine(db_url, pool_size=20)
  # using transactions (i.e. autocommit=False) is better but make this task take way longer
  #Session = scoped_session(sessionmaker(bind=db, autoflush=False, autocommit=False))
  Session = scoped_session(sessionmaker(bind=db, autoflush=False, autocommit=True))

  return Session




if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('--csv', dest='csvdump', action='store_true', default=False,
                    help='dump the data as CSV')
  parser.add_option('-i', dest='inputfile', type='string',
                    help='input file, "-" for stding')
  parser.add_option('-s', dest='sensor', type='string', default='',
                    help='sensor name')
  parser.add_option('--db', dest='dbdump', action='store_true', default=False,
                    help='dump the data to the configured database')
  parser.add_option('-c', dest='config', type='string', default='',
                    help='configuration file')
  parser.add_option('--ignore', dest='ignore', type='string', default='',
                    help='domain ignore list')

  (options, args) = parser.parse_args()

  if not options.inputfile or not (options.csvdump or options.dbdump):
    parser.print_help()
    exit(1)
  elif options.csvdump and options.dbdump:
    print 'specify either CVS _or_ DB dump'
    print
    parser.print_help()
    exit(1)
  elif options.dbdump and (options.sensor.strip(' ') == '' or options.config.strip(' ') == ''):
    print 'ERROR: sensor name and config file required'
    print
    parser.print_help()
    exit(1)

  inputfile = None
  mf = None
  ignore_domains = []
  filter_domains = False

  if options.inputfile == '-':
    inputfile = sys.stdin
  else:
    f = open(options.inputfile, 'rb')
    mf = mmap.mmap(f.fileno(), 0, flags=mmap.MAP_PRIVATE, prot=mmap.PROT_READ)
    inputfile = mf

  if not options.ignore == '':
    f = open(options.ignore, 'rb')

    for l in f:
      ignore_domains.append(l.rstrip())

    ignore_domains = tuple(ignore_domains)
    f.close()

    if len(ignore_domains) > 0:
      filter_domains = True

  ####################
  # read DB config
  db_url = ''
  if options.dbdump:
    config = ConfigParser.RawConfigParser()
    config.read(options.config)

    db_user = config.get('db', 'user')
    db_pass = config.get('db', 'pass')
    db_host = config.get('db', 'host')
    db_db = config.get('db', 'db')

    db_url = 'postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_db)
  ####################

  domains_ignored = 0

  for l in iter(inputfile.readline, ''):
    if l.startswith('['):
      date = l.split(' ')[1]
      date_nice = None
    else:
      # Match the dns-server ip
      m = re.match(r'^\t\[([^\]]+)\]', l)
      if m:
        serv = m.group(1).lower()
        continue

      # match the data
      m = re.match(r'^\t(?:\d+ )?([^\s]+)', l)
      if m:
        res = m.group(1).lower().split(',')
        res_len = len(res)

        if not res_len in filter_res_lengths:
          continue

        if not res[1] == 'in':
          continue

        if not res[2] in filter_rrtype or filter_rrtype[res[2]] in filter_unwanted_rrtype:
          '''
          if not res[2] in filter_unwanted_rrtype:
            #print '\tdiscarded unknown rrtype:', str(res)
            pass
          '''
          continue

        if date_nice is None:
          date_nice = datetime.fromtimestamp(float(date))

        if res[2] in ['a', 'aaaa', 'cname'] and filter_domains:
          filter_domains_found = False
          if res[0].endswith(ignore_domains):
            filter_domains_found = True

          if filter_domains_found:
            domains_ignored += 1
            continue

        process_record(date_nice, res, serv)

  #print 'ignored domains: {0}'.format(domains_ignored)
  #exit(1)


  # cleanup open file / mmap handles
  if not mf is None:
    mf.close()
    f.close()

  if options.csvdump:
    csvdump(cl_records)
  elif options.dbdump:
    # Get the sensorid
    sensor_id = None

    db = init_db(db_url)
    try:
      sensor = db.query(Sensor).filter(Sensor.sensor_name == options.sensor).one()
    except MultipleResultsFound:
      print 'FATAL error, multiple rows for sensor name "{0}", exiting'.format(options.sensor)
      raise
    except NoResultFound:
      # Add new sensor to DB
      sensor = Sensor()
      sensor.sensor_name = options.sensor
      db.add(sensor)
      db.flush()

    sensor_id = sensor.sensor_id
    db = None

    # Add parent domains
    items = len(cl_records)
    split = items / 19

    dicts = []
    keys = cl_records.keys()
    dicts.append({})
    count = 0
    for key in keys:
      i = count / split
      try: 
        dicts[i][key] = cl_records[key]
      except:
        dicts.append({})
        dicts[i][key] = cl_records[key]

      count += 1

    pool = Pool()
    results = []

    for i in dicts:
      result = pool.apply_async(db_add_parent, [sensor_id, i, db_url])
      results.append(result)

    pool.close()
    pool.join()

    for k in results:
      res = k.get()

      for k2, v2 in res.items():
        cl_records[k2].oid = v2
    ####################
