#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# REST server API for passive_dns server
#

import cherrypy
import os
import syslog
try:
  import ConfigParser as configparser
except ImportError:
  import configparser
import datetime
import dateutil.tz
import json

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import and_, or_
import sqlalchemy
from sqlalchemy.sql.expression import exists
from gclu_pdns.db_model import Base, Session, Domain, Entry, Parent_Domain, Sensor, Sensor_Domain, DNS_Server


filter_rrtype = {'a' : 1, 'aaaa' : 28, 'cname' : 5, 'ns' : 2, 'mx' : 15, 'soa' : 6}


class CustomJsonEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, datetime.datetime):
      # we do know that all our datetime objects are saved _only_ in UTC
      # since objects returned by sqlalchemy are naive, add UTC tzinfo
      o_date = obj.replace(tzinfo=dateutil.tz.tzutc())
      return o_date.isoformat()

    return json.JSONEncoder.default(self, obj)


# initialize DB connection
def init_db(db_url):
  __all__ = ['Session', 'Base']

  db = sqlalchemy.create_engine(db_url)
  Session = scoped_session(sessionmaker(bind=db, autoflush=False, autocommit=False))

  return Session


def is_authorized():
  if not cherrypy.request.headers.get('key', '') in cherrypy.config['api_keys']:
    raise cherrypy.HTTPError(403, 'Forbidden')


def audit():
  log('{0} {1} {2}'.format(cherrypy.request.headers.get('remote-addr', 'NONE'), cherrypy.request.headers.get('key', ''),
    cherrypy.request.request_line))


cherrypy.tools.is_authorized = cherrypy.Tool('before_handler', is_authorized, priority = 49)
cherrypy.tools.audit = cherrypy.Tool('before_handler', audit, priority = 50)


def log(msg, priority=syslog.LOG_INFO):
  '''
  Central logging method

  :param msg: message
  :param priority: message priority
  :type msg: str
  :type priority: syslog.LOG_*
  '''

  syslog.syslog(priority, msg)



class Manage(object):
  def __init__(self, Session):
    self.db = Session

  @cherrypy.expose
  @cherrypy.tools.audit()
  @cherrypy.tools.is_authorized()
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def get_domain_entries(self):
    params = cherrypy.request.json
    domain = params['domain']
    records = params.get('records', [])

    out = {'domain' : domain, 'entries' : []}

    try:
      domain_id = self._get_domain_id(domain)
    except NoResultFound:
      raise cherrypy.HTTPError(404, 'Nothing found')

    try:
      out['entries'] = self._get_entries(domain_id, records)
    except NoResultFound:
      pass

    cherrypy.response.status = 200
    return json.dumps(out, cls=CustomJsonEncoder)

  @cherrypy.expose
  @cherrypy.tools.audit()
  @cherrypy.tools.is_authorized()
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def get_domains_by_record_value(self):
    params = cherrypy.request.json
    record = params['record']
    value = params['value']

    if not record in filter_rrtype:
      raise cherrypy.HTTPError(500, 'Requested record type is invalid')

    record = filter_rrtype[record]

    out = []

    try:
      out = self._search_domain_by_record_value(record, value)
    except NoResultFound:
      raise cherrypy.HTTPError(404, 'Nothing found')

    cherrypy.response.status = 200
    return json.dumps(out, cls=CustomJsonEncoder)

  @cherrypy.expose
  @cherrypy.tools.audit()
  @cherrypy.tools.is_authorized()
  @cherrypy.tools.json_in()
  @cherrypy.tools.json_out()
  def check_domains(self):
    params = cherrypy.request.json
    domains = params['domains']
    search_like = params.get('search_like', False)

    out = {}

    for d in domains:
      try:
        res = self._domain_exists(d, search_like=search_like)
        out.update(res)
      except NoResultFound:
        out[d] = False

    cherrypy.response.status = 200
    return json.dumps(out, cls=CustomJsonEncoder)

  def _domain_exists(self, domain, search_like=False):
    q = self.db.query(Domain.domain_id, Domain.domain_name)
    ret = {}

    if search_like:
      res = self._search_domain(domain)

      for r in res:
        ret[r] = True
    else:
      res = self.db.query(exists().where(Domain.domain_name == domain)).scalar()

      if res:
        ret[domain] = True
      else:
        ret[domain] = False

    return ret
    
  def _search_domain(self, domain):
    q = self.db.query(Domain.domain_id, Domain.domain_name)
    q = q.filter(Domain.domain_name.like('%' + domain + '%'))
    ret = {}

    for d in q:
      ret[d[1]] = d[0]

    return ret

  def _get_domain_id(self, domain):
    q = self.db.query(Domain.domain_id)
    q = q.filter(Domain.domain_name == domain)

    return q.scalar()

  def _get_entries(self, domain_id, records=[]):
    q = self.db.query(Entry)
    q = q.filter(Entry.domain_id == domain_id)

    if len(records) > 0:
      records_ = []
      for r in records:
        if not r in filter_rrtype:
          raise cherrypy.HTTPError(500, 'Requested record type is invalid')

        records_.append(filter_rrtype[r])

      # create an OR filter based on all records
      q = q.filter(or_(*map(lambda n: Entry.type == n, records_)))

    q = q.order_by(Entry.type.desc(), Entry.value.desc())

    ret = []

    for entry in q:
      ret.append(entry.get_dict())

    return ret

  def _get_domain_name_by_id(self, domain_id):
    q = self.db.query(Domain.domain_name)
    q = q.filter(Domain.domain_id == domain_id)

    return q.scalar()

  def _search_domain_by_record_value(self, record_type, value):
    q = db.query(Entry.domain_id)
    q = q.filter(and_(Entry.type == record_type, Entry.value == value))
    ret = []

    for r in q:
      domain_name = self._get_domain_name_by_id(r[0])
      ret.append(domain_name)

    return sorted(tuple(ret))



def error_page_403(status, message, traceback, version):
  return 'Error {0} - {1}'.format(status, message)

cherrypy.config.update({'error_page.403': error_page_403})


def application(environ, start_response):
  syslog.openlog('passive_dns_wsgi_server', logoption=syslog.LOG_PID)
  myprefix = os.path.dirname(os.path.abspath(__file__))
  wsgi_config = myprefix + '/wsgi_api.ini'

  if not os.path.exists(wsgi_config):
    wsgi_config = '/etc/passivedns_wsgi_api.ini'
  if not os.path.exists(wsgi_config):
    log('Fatal error: config file not found!', priority=syslog.LOG_ERR)
    sys.exit(1)


  ####################
  # read DB config
  config = configparser.ConfigParser()
  config.read(wsgi_config)

  db_user = config.get('dbro', 'user').strip('\'').strip('"')
  db_pass = config.get('dbro', 'pass').strip('\'').strip('"')
  db_host = config.get('dbro', 'host').strip('\'').strip('"')
  db_db = config.get('dbro', 'db').strip('\'').strip('"')

  db_url = 'postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_db)
  ####################

  db = init_db(db_url)

  cherrypy.config['tools.encode.on'] = True
  cherrypy.config['tools.encode.encoding'] = 'utf-8'
  cherrypy.config.update(config=wsgi_config)

  cherrypy.tree.mount(Manage(db), '/', config=wsgi_config)

  return cherrypy.tree(environ, start_response)


if __name__ == '__main__':
  syslog.openlog('passive_dns_wsgi_server', logoption=syslog.LOG_PID)
  myprefix = os.path.dirname(os.path.abspath(__file__))
  wsgi_config = myprefix + '/wsgi_api.ini'

  if not os.path.exists(wsgi_config):
    wsgi_config = '/etc/passivedns_wsgi_api.ini'
  if not os.path.exists(wsgi_config):
    log('Fatal error: config file not found!', priority=syslog.LOG_ERR)
    sys.exit(1)


  ####################
  # read DB config
  config = configparser.ConfigParser()
  config.read(wsgi_config)

  db_user = config.get('dbro', 'user').strip('\'').strip('"')
  db_pass = config.get('dbro', 'pass').strip('\'').strip('"')
  db_host = config.get('dbro', 'host').strip('\'').strip('"')
  db_db = config.get('dbro', 'db').strip('\'').strip('"')

  db_url = 'postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(db_user, db_pass, db_host, db_db)
  ####################

  db = init_db(db_url)

  cherrypy.config['tools.encode.on'] = True
  cherrypy.config['tools.encode.encoding'] = 'utf-8'
  cherrypy.config.update(config=wsgi_config)

  log('starting')
  cherrypy.quickstart(Manage(db), '/', config=wsgi_config)
