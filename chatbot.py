# -*- coding: utf-8 -*-

from inference_engine import InferenceEngine
import sys

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print("stdin", sys.stdin.encoding)
print("stdout", sys.stdout.encoding)

while True:
    try:
        engine = InferenceEngine()
        print(engine.fit(input()))
    except Exception as ex:
        print("ERROR:", ex)
