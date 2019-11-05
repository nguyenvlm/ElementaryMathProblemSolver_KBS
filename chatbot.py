# coding=utf-8


from inference_engine import InferenceEngine

while True:
    engine = InferenceEngine()
    text = input()
    print(engine.fit(text))
