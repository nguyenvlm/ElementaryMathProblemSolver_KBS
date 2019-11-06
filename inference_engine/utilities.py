# -*- coding: utf-8 -*-

import json


def read_json(path):
    json_value = None
    with open(path, 'r', encoding='utf-8') as file:
        json_string = file.read().replace('\n', '')
        json_value = json.loads(json_string)
    return json_value

def decimalZeroStrip(dec_str):
    if '.' in dec_str:
        return dec_str.rstrip('0').rstrip('.')
    return dec_str