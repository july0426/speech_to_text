#coding:utf8
'''
App ID: 10675192

API Key: N7jL27INLSyTyzetkzzxwakC

Secret Key: ca02caf245a337dadb6a3a8e3de73099
'''
from aip import AipSpeech
import os
""" 你的 APPID AK SK """
APP_ID = '10675192'
API_KEY = 'N7jL27INLSyTyzetkzzxwakC'
SECRET_KEY = 'ca02caf245a337dadb6a3a8e3de73099'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
# 识别本地文件
print os.path.exists('/Users/qiyue/Downloads/4048002184_a9fda31bfcf59fa31.pcm')
print client.asr(get_file_content('/Users/qiyue/Downloads/+14242772618_3910bc2277720601.pcm'), 'pcm', 16000, {
    'lan': 'en',
})
# # 从URL获取文件识别
# client.asr('', 'pcm', 16000, {
#     'url': 'http://121.40.195.233/res/16k_test.pcm',
#     'callback': 'http://xxx.com/receive',
# })
# ffmpeg -i /Users/qiyue/Downloads/+14242772618_3910bc2277720601.amr -ac -1 -ar 16.0k /Users/qiyue/Downloads/+14242772618_3910bc2277720601.mp3
# ffmpeg -i /Users/qiyue/Downloads/+14242772618_3910bc2277720601.mp3 -f s16le -acodec pcm_s16le /Users/qiyue/Downloads/+14242772618_3910bc2277720601.pcm
