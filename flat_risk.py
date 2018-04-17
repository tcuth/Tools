#!/usr/bin/env python

import json
import csv
import pprint

writer = csv.writer(open('carrier_flat.psv','w'), delimiter='|')
writer.writerow(['carrier','0','1','bayes_proportion','proportion','total'])

with open('whitepages.credit.risk.json') as json_file:
    json_data = json.load(json_file)
    for key, value in json_data['Billing Phone Carrier'].iteritems():
        carrier = key
        zero = value.get('0',0)
        one = value.get('1',0)
        bprop = value['bayes_proportion']
        prop = value['proportion']
        total = value['total']
        writer.writerow([carrier,zero,one,bprop,prop,total])
