#coding:utf8
import json
import websocket
import ssl,requests
# 创建一个socket:
def encode_image(file_path):
    with open(file_path,'rb') as f:
        image_content = f.read()
        return image_content
try:
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    # print 3
    # ws.connect('ws://echo.websocket.org/')
    url = 'wss://cloudspeech.goog/ws'
    ws.connect(url)
    # print 4
    start = {"rate":16000,"language":"en-US","format":"amr"}
    ws.send(json.dumps(start))
    data = encode_image('/Users/qiyue/Downloads/+26773382998_31812d3f32cd22ae.amr')
    print(data)
    ws.send(data)
    end = {"action": "stop"}
    ws.send(json.dumps(end))
    while True:
        # print 2
        data = ws.recv()
        print(data)
        # JsonData = re.sub('[0-9]+', '', data, 1)
        # print JsonData.replace('[','').replace(']', '')
except Exception as e:
    print(str(e))

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # 建立连接:
# s.connect(('stream.watsonplatform.net', 80))
# # 发送数据:
# # s.send('{"watson-token"}:{"f9sN0OulvhFp514oUjkqSEcaKByq7lDwTpWnsDnFDhCCHYpfFoBLxF4hElosFhDiBC4t9a20sacqI0JK2axivVIJr9lWgM2V5FfmbAHjci2Vr+SNNj0BoPnE6NBNLsd1x9UJxNmdZQ2ebb2wSTpcrmvilzg/ItI4T6HEiGFlhLRUuYM/xmtA4r25wx4w9ppu2i01Oc9PBCz/401J+r/VE382acTarcsrmXiSWNVBueGmHgyIhBYCmmGtvVQRSKpcRZqsOjgZqqXuDDfw629xYPZupwh7PBL6KhMx9Ybw+BDEHfbJDIxhz5F9SamV+SZHtSAAlAIbm/0J2Oxez5EVK0gKQF0YXqNCf97myhunwGLQ9sGVGhcbAygsH7uCovGG3G0+89sbPJ2Fnjl5shJYAT9W6PNlkkRt9hZqVaBJ8z2IMZdJCI9JHWEbYqbZzfBrRs4uX4YvO0x9GCs0K18rO3z7ktclSHghQ6eJYw6a5WXy1RCJ4i5Ap6XzN8z31epIqtzFcbp4vZJUImcm3T6UgHiMkqtTiCwSjSpAfy4i5Kn71SmMHaA9u3yrQFYdgt1v3n4qSxCt/lOAtoahS8Hv2t83gGfSgZv4gBxlb0gEKtDd7cfG0y0q9G9h/lv0HQT3P7IMzOV1UvVb6eCObjBKc3Ex6J2L6NujGa9Q5lUt+4N5HtD2anZjCd3xQ7bxnAqXLMIYVkQ4s9Lh6lEr6nD1N2XHRO0+OB+9TYw8Zb5vPhX1ZanXdM8HWB63245z15nCoSgy8h3U0Hb9nxlNVDqDvmZ80BvLWoXnrolneokLc2F0G18/9Jc3Yv2a6h/I0Ncm9omJ9Jyz1g6jZ2gYyzmcz1aMG6Fags9oxfUKfHq1IDGbN9QN3OObDVCjnLyxRRGnvLT7EAshq8x3bxxtmsG+xYNZpgXRUy6lP09wu2wsazov+EErujouvmkKxJ8ecPrKGPbF7KdY+2PTuVY8IRa8Sojk+eAHa6JwoZ4NOA+0eFovocqlx7y1Y9yFvNxcEyrM9won44zyguBAnxHgQJnNpw=="}')
# start = {"timestamps":True,"content-type":"audio/mp3","interim_results":True,"keywords":["IBM","admired","AI","transformations","cognitive","Artificial Intelligence","data","predict","learn"],"keywords_threshold":0.01,"word_alternatives_threshold":0.01,"smart_formatting":True,"speaker_labels":True,"action":"start"}
# s.send(json.dumps(start))
# data = encode_image('/Users/qiyue/Downloads/+26773382998_31812d3f32cd22ae.mp3')
# # print data
# s.send(data)
# end = {"action":"stop"}
# s.send('{"action":"stop"}')
# # s.send(data,1024)
#                       # wss://stream.watsonplatform.net/speech-to-textwats/api/v1/recognize?model=en-US_BroadbandModel&on-token=2FTgeMgX3UgjYkMpu8SllTCzsRpauFgAkVuA1qkKjUw%2FaMV0h4rbIQsEDWUGZFjAdaVHBroxl%2BRXufyma51DlylA3wTBbKkhpDxxn2P8dsiZveFEsSkjc0NcP2%2BJ2pzYs1GvyafI1L1Be5xO3MqUzv0P00q42bsEo3gsrcgjLs%2BGn0%2FSAkaqQQpdiVxNaWPvaIdP5c8vGaDYFvplzuDmuPyyxhbz%2B9MDVQI%2FURPtHeb%2FL5w9116PlYOwQ0Yu1PTEopBGKlPnWHZz2bTYsVgWIchMvjq8zjUbe3i2MFAyYqG%2BMbHO%2B4abVasBDdogP7TebLuEB6xVojHlxiCo24s%2Ft%2BXruROTHEpDXjZrYwGGeL%2Bbi%2FFZD%2FdXYYMl4xk9z9lCQ0qCi6Es%2BHdf6PyDGm45XXIf1rk6U8SyqKnxhkHhcDPMtaOKCZm7m%2B33Y6A4Al%2BuZgF97AEHi7IdxDaj9Ejue1efUg4GmHctoGqm%2B%2BnOXP5RWm3vJboGO477usVSAHJifobCHuGVUC3lLvO%2Fxkqh49kW74Zv4Wyj5ry1OGbjLjzX7MA3mepE5fTp%2FCd8Hj8cWuY1iBzDJcyRU0gKwhfHCj7bZvnGxXoIO7jxWEVgcP9jcyslsu8fOANG0ihKMk%2BcH%2FFgmWHK%2B0IqHppClpcH%2BMpzpeGPcJz%2Fp%2BppmTYvtp5V5mr29pLJiZYmZT7%2FwvQRRgbR84YCOjKZ%2B4y9OOkHayl%2BFBfOwHXLzc%2FEUL%2FnS4vRKFQLK6wMo%2FrcjkhI4NMYlZep8Wb0ko1zErgXgZlFJDsmO5lFqSepDdikixEGwuujwUVboXxW9VQDgYkYKNPBgcFWUamILYGbG2927RjRn5r7mnInvVgI6j5u3%2FqdkNULO1VORQjyEPdZaE4JMZQkYweKjRniwg4nrtBiL%2Bxs%2F8Ard1H0%2B%2BqpM2iYezky1p%2FxBb25k2AfvvbWHUIRN7KxVeif9JnsJzz5hHcv4ts5t1h2NHbAp7H5T1H%2Bx4guMcp7Syi1KFV4y%2F8TOtmf97YFuWcpSapq%2B922sMtYqU0Hdg%3D%3D
# # 接收数据:
# buffer = []
# while True:
#     # 每次最多接收1k字节:
#     d = s.recv(1024)
#     if d:
#         buffer.append(d)
#     else:
#         break
# data = ''.join(buffer)
# # 关闭连接:
# s.close()
# print data
# # url = 'https://stream.watsonplatform.net/speech-to-text/api/v1'
# # res = requests.get(url)
# # print res.text