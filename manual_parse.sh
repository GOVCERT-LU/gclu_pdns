#!/bin/bash

# Copyright (c) 2013 GOVCERT.LU / Georges Toth & Foetz Guy


./dnscap -r $1 -g 2>&1| python pdns_pcap_parser.py --csv -i -
