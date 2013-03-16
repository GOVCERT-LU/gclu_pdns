#!/bin/bash

#
# Georges Toth 2013-03-11
#
# Takes DNSCAP CSV output as input, applied optional domain filtering
# and writes results to a file, auto-rotated by a configurable amount of
# minutes.
#
# DNS records
#   include:
#   ns a aaaa cname soa mx ptr
#
#   exclude:
#   43 46 47 50 99 16
#   DS RRSIG NSEC3 SPF TXT
#
#   wishlist:
#   srv dname
#
# DNS entry lengths (CSV)
#   7:  ns a aaaa cname ptr (txt nsec3 rrsig ds nsec spf dname srv)
#   8:  mx
#   13: soa
#

import datetime
import sys
import signal
import errno
import shutil
from optparse import OptionParser


debug = False
log = None
filename = ''
filter_domains = False
ignore_domains_file = ''
ignore_domains = []

record_type = {'a' : 1, 'aaaa' : 28, 'cname' : 5, 'ns' : 2, 'mx' : 15, 'soa' : 6, 'ptr' : 12, 'txt' : 16}
filter_res_lengths = [7, 8, 13]
blacklist_record_types = ['43', '46', '47', '50', '99', '16', 'ds', 'rrsig', 'nsec3', 'spf', 'txt']



def signal_handler(signal, frame):
  global log
  global filename
  print 'Exiting...'

  if log:
    filename_part = '{0}.part'.format(filename)
    print 'Closing log "{0}"...'.format(filename_part)
    print
    log.close()
    shutil.move(filename_part, filename)

  sys.exit(1)


def reload_ignore_domains(signal=None, frame=None):
  global filter_domains
  global ignore_domains

  if debug:
    print 'reloading ignore domains...'
  
  new_ignore_domains = []
  f = open(ignore_domains_file, 'rb')

  for l in f:
    new_ignore_domains.append(l.rstrip())

  f.close()

  if len(new_ignore_domains) > 0:
    new_ignore_domains = tuple(new_ignore_domains)
    filter_domains = True
    ignore_domains = new_ignore_domains
  else:
    filter_domains = False

  if debug:
    print 'loaded {0} domains'.format(len(ignore_domains))
    print 'done'
    print


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('--debug', dest='debug', action='store_true', default=False,
                    help='debug')
  parser.add_option('-s', dest='sensor', type='string', default='',
                    help='sensor name')
  parser.add_option('-d', dest='destination', type='string', default='',
                    help='destination folder')
  parser.add_option('-i', dest='ignore', type='string', default='',
                    help='list of domains to be ignored')
  parser.add_option('-r', dest='rotate', type='int', default=10,
                    help='auto-rotate output by this many minutes')

  (options, args) = parser.parse_args()

  if options.sensor == '' or options.destination == '':
    parser.print_help()
    exit(1)
  elif not options.rotate > 0:
    print 'Fatal error: "rotate" options has to be >0'
    print
    parser.print_help()
    exit(1)

  if options.debug:
    debug = True

  # catch all signals in order to be able to properly close the logfile
  # before exiting
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGHUP, reload_ignore_domains)

  ignored_domains = 0
  if not options.ignore == '':
    ignore_domains_file = options.ignore
    reload_ignore_domains()

  curtag = datetime.datetime.now().strftime('%Y%m%d_%H%M')
  filename = '{0}/{1}_{2}'.format(options.destination, options.sensor, curtag)
  filename_part = '{0}.part'.format(filename)
  log = open(filename_part, 'wb')

  try:
   for l in sys.stdin:
      date = datetime.datetime.now()
      tag = date.strftime('%Y%m%d_%H%M')

      if date.minute % options.rotate == 0 and tag != curtag:
        if options.debug:
          print 'rotating file, old: {0}, new: {1}'.format(curtag, tag)
          print 'ignored {0} entries'.format(ignored_domains)
          print

        ignored_domains = 0
        log.close()
        filename_part = '{0}.part'.format(filename)
        shutil.move(filename_part, filename)

        curtag = tag
        filename = '{0}/{1}_{2}'.format(options.destination, options.sensor, curtag)
        filename_part = '{0}.part'.format(filename)
        log = open(filename_part, 'wb')


      row = l.split(',')

      # check if entry length matches anything we care about
      if not len(row) in filter_res_lengths:
        ignored_domains += 1
        continue

      record_type = row[4]

      # if record type on blacklist, ignore this entry
      if record_type in blacklist_record_types:
        ignored_domains += 1
        continue

      # if filtering is turned on, filter out blacklisted domains
      if filter_domains:
        # index 2: A, AAAA, CNAME
        # index 6: CNAME, PTR
        if row[2].endswith(ignore_domains) or row[6].endswith(ignore_domains):
          ignored_domains += 1
          continue

      log.write(l)
  except IOError, e:
    # if not an interrupt sigcall
    if e.errno != errno.EINTR:
      raise

  log.close()
