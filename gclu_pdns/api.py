#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Georges Toth'
__email__ = 'georges.toth@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Georges Toth'
__license__ = 'GPL v3+'

#
# PDNS client API
#

import json
import requests



class PDNSApi(object):
  def __init__(self, api_url, api_key, http_timeout=5, verify_ssl=False, proxies={}):
    self.api_url = api_url
    self.api_key = api_key
    self.verify_ssl = verify_ssl
    self.proxies = proxies

  def __request(self, method, data, extra_headers=None):
    url = '{0}/{1}'.format(self.api_url, method)
    headers = {'Content-Type': 'application/json; charset=utf-8', 'key' : self.api_key}

    if extra_headers:
      for k, v in extra_headers.items():
        headers[k] = v

    r = requests.post(url, data=json.dumps(data), headers=headers, verify=self.verify_ssl, proxies=self.proxies)

    r_text = r.text
    if r.text and len(r.text) > 20:
      r_text = r.text[:20]

    rest_msg_text = 'Code: {0}, Msg: {1}'.format(r.status_code, r_text)

    if not (r.status_code == 200 and r.json):
      raise Exception('Error ({0})'.format(rest_msg_text))

    return json.loads(r.json)

  def get_domain_entries(self, domain, records):
    return self.__request('get_domain_entries', {'domain' : domain, 'records' : records})

  def check_domains(self, domains, search_like=False):
    return self.__request('check_domains', {'domains' : domains, 'search_like' : search_like})

  def get_domains_by_a_record(self, value):
    return self.__request('get_domains_by_record_value', {'record' : 'a', 'value' : value})

  def get_domains_by_aaaa_record(self, value):
    return self.__request('get_domains_by_record_value', {'record' : 'aaaa', 'value' : value})

  def get_domains_by_mx_record(self, value):
    return self.__request('get_domains_by_record_value', {'record' : 'ns', 'value' : value})

  def get_domains_by_ns_record(self, value):
    return self.__request('get_domains_by_record_value', {'record' : 'mx', 'value' : value})


def json_pretty_print(j):
  return json.dumps(j, sort_keys=True, indent=4, separators=(',', ': '))
