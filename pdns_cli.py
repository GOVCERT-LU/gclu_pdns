#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# mail feature extractor
# submits results to a remote mailm0n server via REST API
#

import sys
import os
try:
  import ConfigParser as configparser
except ImportError:
  import configparser
from optparse import OptionParser
import json
import gclu_pdns.api


def main(api_url, api_key, proxies):
  api = gclu_pdns.api.PDNSApi(api_url, api_key, verify_ssl=False, proxies=proxies)

  #j = api.get_domain_entries('google.org', ['a', 'mx'])
  #j = api.check_domains(['google.org', 'google.cn'])
  #j = api.check_domains(['google'], search_like=True)
  j = api.get_domains_by_a_record('173.194.70.139')
  #j = api.get_domains_by_a_record('127.0.0.1')

  j = gclu_pdns.api.json_pretty_print(j)
  print(j)


if __name__ == '__main__':
  config_file = os.path.expanduser('~/.pdns_cli.conf')
  if not os.path.isfile(config_file):
    print('Fatal error: config file not found!')
    sys.exit(1)

  config = configparser.ConfigParser()
  config.read(config_file)

  try:
    api_url = config.get('api', 'url')
    api_key = config.get('api', 'key')
    http_proxy = config.get('api', 'http_proxy')
    https_proxy = config.get('api', 'https_proxy')
  except:
    print('Fatal error: invalid config file!')
    sys.exit(1)

  proxies = {}
  if not http_proxy == '':
    proxies['http'] = http_proxy
  if not https_proxy == '':
    proxies['https'] = https_proxy

  api = gclu_pdns.api.PDNSApi(api_url, api_key, verify_ssl=False, proxies=proxies)

  parser = OptionParser()
  parser.add_option('-d', dest='domain', type='string', default='',
                    help='comma seperated list of domains to search for (e.g. test1.com,test2.com)')
  parser.add_option('--ld', dest='likedomain', type='string', default='',
                    help='domain to be used for like query (make sure you know what you are doing!)')
  parser.add_option('--r-a', dest='record_a', type='string', default='',
                    help='A record value to search for')
  parser.add_option('-r', dest='records', type='string', default='',
                    help='comma seperated list of records to search for (e.g. a,mx,aaaa)')
  parser.add_option('-e', dest='entries', action='store_true', default=False,
                    help='get entries for domain')

  (options, args) = parser.parse_args()


  if options.domain == '' and options.likedomain == '' and options.record_a == '':
    parser.print_help()
    exit(1)

  domains = []
  likedomains = []
  record_a = ''
  records = []
  entries = options.entries
  if not options.domain == '':
    domains = options.domain.split(',')
  if not options.likedomain == '':
    likedomains = options.likedomain.split(',')
  if not options.record_a == '':
    record_a = options.record_a
  if not options.records == '':
    records = options.records.split(',')


  if entries and len(domains) > 0:
    j = {}
    for d in domains:
      j.update(api.get_domain_entries(d, records))
  elif len(domains) > 0 or len(likedomains) > 0:
    like = False
    if len(likedomains) > 0:
      like = True

    domains += likedomains
    j = api.check_domains(domains, search_like=like)
  elif not record_a == '':
    j = api.get_domains_by_a_record(record_a)
  else:
    print('Fatal error: nothing to do O_o, check parameters!')
    print()
    parser.print_help()
    exit(1)


  j = gclu_pdns.api.json_pretty_print(j)
  print(j)


  sys.exit(1)
  try:
    main()
  except KeyboardInterrupt:
    sys.exit(1)
  except Exception as e:
    import traceback
    print(traceback.format_exc())
    print('{0}'.format(e))
    sys.exit(1)

