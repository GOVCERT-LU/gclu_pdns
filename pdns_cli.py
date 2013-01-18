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
filter_rrtype_rev = {1: 'a', 28: 'aaaa', 5: 'cname', 2: 'ns', 15: 'mx', 6: 'soa'}
filter_res_lengths = [5, 6, 11]
filter_unwanted_rrtype = [15, 50, 46, 43, 47, 12]
sensor_name = ""
records = {}
cl_records = {}


# initialize DB connection and create DB if not exist
def init_db(db_url):
  __all__ = ['Session', 'Base']

  db = sqlalchemy.create_engine(db_url)
  Session = scoped_session(sessionmaker(bind=db, autoflush=False, autocommit=False))

  return Session


def print_parent_domain_like(db, name):
  q = db.query(Parent_Domain)
  q = q.filter(Parent_Domain.parent_domain_name.like('%' + name))

  for r in q:
    print r
    print_domain_parent_id(db, r.parent_domain_id)
    print


def print_parent_domain_name(db, name):
  q = db.query(Parent_Domain)
  q = q.filter(Parent_Domain.parent_domain_name == name)

  for r in q:
    print r
    print_domain_parent_id(db, r.parent_domain_id)


def get_low_ttl_parent_domains(db, ttl):
  q = db.query(Parent_Domain.parent_domain_name)
  q = q.filter(and_(Parent_Domain.parent_domain_id == Domain.parent_domain_id, Domain.domain_id == Entry.domain_id, Entry.ttl <= ttl))
  domains = []
  ret = q.all()

  for k in ret:
    domains.append(k[0])

  domains = list(set(domains))

  return domains


def get_entries(db, record_type, value):
  q = db.query(Entry)
  q = q.filter(and_(Entry.type == filter_rrtype[record_type], Entry.value == value)).order_by(Entry.domain_id.desc())
  entries = []

  for k in q:
    entries.append(k)

  return entries


# @FIXME for some reason a relationship does not work, investigate and fix
def get_domain_name(db, domain_id):
  q = db.query(Domain.domain_name)
  q = q.filter(Domain.domain_id == domain_id)

  try:
    o = q.one()
    return o[0]
  except NoResultFound:
    return 'domain not found'


def print_domain_parent_id(db, parent_domain_id):
  q = db.query(Domain)
  q = q.filter(Domain.parent_domain_id == parent_domain_id)

  for r in q:
    print r
    print_domain_id(db, r.domain_id)


def print_domain_like(db, name):
  q = db.query(Domain)
  q = q.filter(Domain.domain_name.like('%' + name + '%'))

  for r in q:
    print r
    print_domain_id(db, r.domain_id)


def print_domain_name(db, domain):
  q = db.query(Domain)
  q = q.filter(Domain.domain_name == domain)

  try:
    o = q.one()
    print ' domain: {0}'.format(str(o))
    print_domain_id(db, o.domain_id)
  except NoResultFound:
    print ' no result'


def print_domain_id(db, domain_id):
  q = db.query(Entry)
  q = q.filter(Entry.domain_id == domain_id).order_by(Entry.type.desc(), Entry.value.desc())

  for r in q:
    print '  ' + str(r)



if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('--csv', dest='csvdump', action='store_true', default=False,
                    help='dump the data as CSV')
  parser.add_option('-s', dest='sensor', type='string', default='',
                    help='sensor name')
  parser.add_option('-c', dest='config', type='string',
                    help='configuration file')
  parser.add_option('-d', dest='domain', type='string', default='',
                    help='domain to search for')
  parser.add_option('--ld', dest='likedomain', type='string', default='',
                    help='domain to be used for like query (make sure you know what you are doing!!!!)')
  parser.add_option('--lttl', dest='lowttl', type='int', default=-1,
                    help='get all domains with low TTL as specified (expensive query make sure you know what you are doing!!!!)')

  parser.add_option('-e', dest='entries', action='store_true', default=False,
                    help='search for entries; also specify record type and record value')
  parser.add_option('--e-rt', dest='record_type', type='string', default='',
                    help='record type')
  parser.add_option('--e-rv', dest='record_value', type='string', default='',
                    help='record value')


  (options, args) = parser.parse_args()

  if not options.csvdump or (options.domain == '' and options.likedomain == '' and options.lowttl == -1 and not options.entries):
    parser.print_help()
    exit(1)
  elif not options.domain == '' and not options.likedomain == '':
    print 'specify _either_ domain _or_ likedomain !!!'
    exit(1)
  elif options.entries and (options.record_type == '' or options.record_value == ''):
    print 'specify record type _and_ record  value !!!'
    exit(1)
  elif options.config.strip(' ') == '':
    print 'ERROR: config file required'
    print
    parser.print_help()
    exit(1)


  ####################
  # read DB config
  config = ConfigParser.RawConfigParser()
  config.read(options.config)

  db_user = config.get('dbro', 'user')
  db_pass = config.get('dbro', 'pass')
  db_host = config.get('dbro', 'host')
  db_db = config.get('dbro', 'db')

  db_url = 'postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_db)
  ####################


  db = init_db(db_url)

  if not options.domain == '':
    if len(options.domain.split('.')) == 2:
      print_parent_domain_name(db, options.domain)
    else:
      print_domain_name(db, options.domain)
  elif not options.likedomain == '':
    if len(options.likedomain.split('.')) == 2:
      print_parent_domain_like(db, options.likedomain)
    else:
      print_domain_like(db, options.likedomain)
  elif not options.lowttl == -1:
    for k in get_low_ttl_parent_domains(db, options.lowttl):
      print k
  elif options.entries:
    entries = get_entries(db, options.record_type, options.record_value)
    last_domain_id = -1
    for k in entries:
      if not k.domain_id == last_domain_id:
        print get_domain_name(db, k.domain_id)
        last_domain_id = k.domain_id
      print '  ' + str(k)
