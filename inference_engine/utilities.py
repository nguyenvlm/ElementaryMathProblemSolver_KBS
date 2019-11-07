# -*- coding: utf-8 -*-

import json
from math import gcd

def DecimalToFraction(Max,n):
    a,b = (0,1),(1,0)
    while True:
        mid = (a[0]+b[0],a[1]+b[1])
        if mid[1]//gcd(*mid) > Max: 
            if abs(a[0]/a[1]-n) < abs(b[0]/b[1]-n): return str(a[0])+'/'+str(a[1])
            else: return str(b[0])+'/'+str(b[1])
            break
        if n <= mid[0]/mid[1]: b = mid
        else: a = mid

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