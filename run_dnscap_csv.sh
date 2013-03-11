#!/bin/bash

# Copyright (c) 2013 GOVCERT.LU / Georges Toth & Foetz Guy

PDNSROOT=/root/passive_dns
PDNSOUTPUTROOT=/log/passive_dns
TIMEOUT=600
INT=eth2
SENSOR=ctie
QUEUE=${PDNSOUTPUTROOT}/queue
DNSCAP=${PDNSROOT}/dnscap
PYDNSCAPCSVLOGGER=${PDNSROOT}/dnscap_csv_logger.py


INT=eth3
SENSOR=ctie2

${DNSCAP} -T -s r -i ${INT} -P | grep ",IN," | tr [:upper:] [:lower:] | python ${PYDNSCAPCSVLOGGER} -s ${SENSOR} -d ${QUEUE}/ -i ${PDNSROOT}/ignore_domains -r 10 --debug
