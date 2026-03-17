import renard, tools, os

r = renard.Renard()
r.memory.recall = lambda _msg: 'No memories'
r.memory.remember = lambda **kwargs: None

def fake_chat(model, messages):
    txt = messages[0]['content']
    if 'Classify this message' in txt:
        return {'message': {'content': 'code'}}
    return {'message': {'content': "```python\nprint('hello')\n```"}}

renard.ollama.chat = fake_chat

resp = r.think('Build a Python script to print hello')
print('RESP')
print(resp)
print('OUTPUT_DIR', tools.OUTPUT_DIR)
print('FILES', os.listdir(tools.OUTPUT_DIR))
