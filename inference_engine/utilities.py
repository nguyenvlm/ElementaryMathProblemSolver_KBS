# -*- coding: utf-8 -*-

import json


def read_json(path):
    json_value = None
    with open(path, 'r', encoding='utf-8') as file:
        json_string = file.read().replace('\n', '')
        json_value = json.loads(json_string)
    return json_value

def numericZeroStrip(num):
    dtype = type(num)
    nparts = str(num).split('.')
    if len(nparts) > 2:
        return dtype(0)
    ipart = nparts[0].lstrip('0')
    if ipart == '': ipart = '0'
    if len(nparts) > 1:
        dpart = nparts[1].rstrip('0')
        if dpart == '':
            return dtype(ipart)
        return dtype("%s.%s"%(ipart, dpart))
    return dtype(ipart)