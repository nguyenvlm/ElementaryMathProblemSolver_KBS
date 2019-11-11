# -*- coding: utf-8 -*-

from inference_engine import InferenceEngine
import sys
import traceback

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print("stdin", sys.stdin.encoding)
print("stdout", sys.stdout.encoding)

engine = InferenceEngine()
print(engine)

running = True

while running:
    try:
        print(engine.fit(input()))
    except Exception as ex:
        running = False
        print(engine.answer)
        print("An error has occured! Here is the error details:")
        try:
            traceback.print_tb(ex.__traceback__, file=sys.stdout)
            print(ex)
        except Exception as another_ex:
            print("Another error has occured::", another_ex)
    finally:
        pass
