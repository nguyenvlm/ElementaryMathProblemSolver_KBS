# -*- coding: utf-8 -*-

import json
from math import gcd
# from decimal import Decimal

def read_json(path):
    json_value = None
    with open(path, 'r', encoding='utf-8') as file:
        json_string = file.read().replace('\n', '')
        json_value = json.loads(json_string)
    return json_value

# def numericZeroStrip(num):
#     dtype = type(num)
#     nparts = str(num).split('.')
#     if len(nparts) > 2:
#         return dtype(0)
#     ipart = nparts[0].lstrip('0')
#     if ipart == '': ipart = '0'
#     if len(nparts) > 1:
#         dpart = nparts[1].rstrip('0')
#         if dpart == '':
#             return dtype(ipart)
#         return dtype("%s.%s"%(ipart, dpart))
#     return dtype(ipart)

# def DecimalToFraction(Number, Max = 10000):
#     if Number == int(Number):
#         return str(Number)
#     Number = float(Number)
#     a,b = (0,1),(1,0)
#     while True:
#         mid = (a[0]+b[0],a[1]+b[1])
#         if mid[1]//gcd(*mid) > Max: 
#             if abs(a[0]/a[1]-Number) < abs(b[0]/b[1]-Number): 
#                 return str(a[0]) + ('/'+str(a[1]) if a[1] != 1 else '')
#             else: 
#                 return str(b[0]) + ('/'+str(b[1]) if b[1] != 1 else '')
#             break
#         if Number <= mid[0]/mid[1]: b = mid
#         else: a = mid
#     return str(Number)