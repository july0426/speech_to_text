#!/usr/local/anaconda2/bin/python
#coding:utf8
'''
利用IBM的speech_to_text接口,对音频进行识别,将识别后的text文本存入数据库
业务逻辑:
1.从数据库获取音频信息,主要包括id,音频时长,存储路径
2.对时长进行数据处理,转换为秒数,5秒-240秒(4分钟)范围内进行识别,其他的暂时标记为3
3.识别的细节:(1)每次识别更换一个代理(2)音频需要通过ffmpeg进行处理,转成16k采样率和mp3格式,识别后删除临时文件
4.从数据库中取一个IBM账号,并且累计识别的时长,超过1000分钟时,修改状态,更换下一个账号

数据库相关改动:
1.音频文件数据表show_caller_audio:
    新增字段:speech_status
            初始值为0,开始识别1,识别成功为时间戳,识别失败-10,音频过长10000,音频过短为10
    新增字段speech_text:
            存储识别后的文本
2.新建一个IBM账号表show_caller_IBM_account:
    1.id
    2.username
    3.password
    4.duration  初始值为0,最大值60000,每月1号重置为0
    5.status    初始值为0,duration超过60000时,修改为时间戳,每月1号重置为0
'''

from __future__ import print_function
import re,MySQLdb,subprocess,time,random
import json                        # json
import threading                   # multi threading
import os                          # for listing directories
try:
    import Queue                       # queue used for thread syncronization
except:
    from queue import Queue
import sys                         # system calls
import argparse                    # for parsing arguments
#                                  # according to the RFC2045 standard
import requests                    # python HTTP requests library

# WebSockets
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS
from twisted.python import log
from twisted.internet import ssl, reactor
'''获取音频时长'''
def get_duration(save_path):
    # 判断文件是否存在
    if os.path.exists(save_path):
        # 利用ffmpeg获取音频信息
        commond = '/usr/local/bin/ffprobe -v quiet -print_format json -show_format -show_streams %s' % save_path
        # print(commond)
        p = subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True)
        # 获取命令行的输出
        js = p.stdout.read()
        print(js)
        duration_re = re.compile(r'"duration": "(.*)?"')
        # 正则匹配出duration(音频时长),是一个小数,字符串
        duration = re.search(duration_re, js)
        if duration:
            duration = duration.group(1)
            duration_s = int(duration.split('.')[0])
            duration_ss = int(duration.split('.')[1][0])
            print(duration_ss)
            # 对duration进行3舍4入,转换成int返回
            if duration_ss > 3:
                duration = duration_s + 1
            else:
                duration = duration_s
            print(duration)
            return duration
        else:
            # 如果没获取到duration,就返回FALSE
            return False
    else:
        return False
'''从数据库中提取一条音频数据'''
def get_data_from_mysql():
    # 建立数据库连接
    db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
    cocur = db.cursor()
    sql = 'select id,save_path,cc,tel_number,`size`,file_name from show_caller_audio where speech_status = 0 and audio_language="ar" and cc in (212,964,972,20)  ORDER BY id DESC limit 1'
    try:
        cocur.execute(sql)
        # 获取一条数据
        data = cocur.fetchone()
        if data:
            id = data[0]
            save_path = data[1]
            print(data)
            # 利用ffmpeg获取音频时长  调用get_duration函数
            duration = get_duration(save_path)
            print('duration  ',duration)
            # 根据duration进行判断,小于5秒修改状态为10,不识别,大于240秒改为10000,不识别,5-240的进行识别,状态改为1
            if duration == False:
                sql = 'update show_caller_audio set speech_status = -10 where id =%s' % id
            elif duration<5:
                print('Audio is too short...')
                sql = 'update show_caller_audio set speech_status=10 where id=%s' % id
                duration = False
            elif duration<240:
                print('Audio duration is ',duration)
                sql = 'update show_caller_audio set speech_status=1 where id=%s' % id
            else:
                print('Audio is too long...')
                sql = 'update show_caller_audio set speech_status=10000 where id=%s' % id
                duration = False
            try:
                cocur.execute(sql)
                db.commit()
                print('Speech_status update success!')
            except Exception as e:
                print('Speech_status update faild.....')
                print(str(e))
                db.rollback()
            db.close()
            # duration在目标范围内,就返回一个字典,否则返回False
            if duration is not False:
                return {'id': id, 'save_path': data[1], 'duration': duration,'cc':data[2],'tel_number':data[3],'size':data[4],'file_name':data[5]}
            else:
                return False
        else:
            exit('No data to process')
    except:
        print('No data to process....')
        return 'no data'
'''从数据库中获取一个代理'''
def get_proxy():
    db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
    cursor = db.cursor()
    # 从数据库中取出代理
    sql = "select id,proxy from show_caller_proxy order by status asc limit 1"
    try:
        cursor.execute(sql)
        proxies = cursor.fetchone()
        if proxies:
            # 更新代理时间戳
            sql = "update show_caller_proxy set status=%d where id=%d" % (int(time.time()), proxies[0])
            cursor.execute(sql)
            proxie = proxies[1]
            proxy = {
                'http': 'http://%s' % proxie,
                'https': 'https://%s' % proxie,
            }
            db.commit()
            return proxy
        else:
            return False
    except Exception as e:
        print(str(e))
        return False
'''利用websocket获取识别后的文本'''
try:
    raw_input          # Python 2
except NameError:
    raw_input = input  # Python 3

# 获取token
class Utils:
    @staticmethod
    def getAuthenticationToken(proxy):
        try:
            token = requests.get('https://speech-to-text-demo.ng.bluemix.net/api/token',proxies = proxy)
            print(token.text)
            return token.text
        except Exception as e:
            print(str(e))
            db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
            cursor = db.cursor()
            # 从数据库中取出代理
            proxie = proxy['http'].replace('http://','')
            sql = 'update show_caller_proxy set use_count = use_count + 1 WHERE proxy = "%s"' % proxie
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print(str(e))
                db.rollback()
            db.close()
            return False


class WSInterfaceFactory(WebSocketClientFactory):

    def __init__(self, queue, summary, contentType, model,
                 url=None, headers=None, debug=None):

        WebSocketClientFactory.__init__(self, url=url, headers=headers)
        self.queue = queue
        self.summary = summary
        # self.dirOutput = dirOutput
        self.contentType = contentType
        self.model = model
        self.queueProto = Queue.Queue()

        self.openHandshakeTimeout = 10
        self.closeHandshakeTimeout = 10

        # start the thread that takes care of ending the reactor so
        # the script can finish automatically (without ctrl+c)
        endingThread = threading.Thread(target=self.endReactor, args=())
        endingThread.daemon = True
        endingThread.start()

    def prepareUtterance(self):

        try:
            utt = self.queue.get_nowait()
            self.queueProto.put(utt)
            return True
        except Queue.Empty:
            print("getUtterance: no more utterances to process, queue is "
                  "empty!")
            return False

    def endReactor(self):

        self.queue.join()
        print("about to stop the reactor!")
        reactor.stop()

    # this function gets called every time connectWS is called (once
    # per WebSocket connection/session)
    def buildProtocol(self, addr):
        try:
            utt = self.queueProto.get_nowait()
            proto = WSInterfaceProtocol(self, self.queue, self.summary, self.contentType)
            proto.setUtterance(utt)
            return proto
        except Queue.Empty:
            print("queue should not be empty, otherwise this function should "
                  "not have been called")
            return None
# WebSockets interface to the STT service
#
# note: an object of this class is created for each WebSocket
# connection, every time we call connectWS
class WSInterfaceProtocol(WebSocketClientProtocol):

    def __init__(self, factory, queue, summary, contentType):
        self.factory = factory
        self.queue = queue
        self.summary = summary
        # self.dirOutput = dirOutput
        self.contentType = contentType
        self.packetRate = 20
        self.listeningMessages = 0
        self.timeFirstInterim = -1
        self.bytesSent = 0
        self.chunkSize = 2000     # in bytes
        super(self.__class__, self).__init__()
        # print(dirOutput)
        print("contentType: {} queueSize: {}".format(self.contentType,
                                                     self.queue.qsize()))

    def setUtterance(self, utt):

        self.uttNumber = utt[0]
        self.uttFilename = utt[1]
        self.summary[self.uttNumber] = {"hypothesis": "",
                                        "status": {"code": "", "reason": ""}}

    # helper method that sends a chunk of audio if needed (as required
    # what the specified pacing is)
    def maybeSendChunk(self, data):

        def sendChunk(chunk, final=False):
            self.bytesSent += len(chunk)
            self.sendMessage(chunk, isBinary=True)
            if final:
                self.sendMessage(b'', isBinary=True)

        if (self.bytesSent + self.chunkSize >= len(data)):
            if (len(data) > self.bytesSent):
                sendChunk(data[self.bytesSent:len(data)], True)
                return
        sendChunk(data[self.bytesSent:self.bytesSent + self.chunkSize])
        self.factory.reactor.callLater(0.01, self.maybeSendChunk, data=data)
        return

    def onConnect(self, response):
        print("onConnect, server connected: {}".format(response.peer))

    def onOpen(self):
        print("onOpen")
        data = {"action": "start",
                "content-type": str(self.contentType),
                "continuous": True,
                "interim_results": True,
                "inactivity_timeout": 600,
                'max_alternatives': 3,
                'timestamps': True,
                'word_confidence': True}
        print("sendMessage(init)")
        # send the initialization parameters
        self.sendMessage(json.dumps(data).encode('utf8'))

        # start sending audio right away (it will get buffered in the
        # STT service)
        print(self.uttFilename)
        with open(str(self.uttFilename), 'rb') as f:
            self.bytesSent = 0
            dataFile = f.read()
        self.maybeSendChunk(dataFile)
        print("onOpen ends")

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print(u"Text message received: {0}".format(payload.decode('utf8')))

            # if uninitialized, receive the initialization response
            # from the server
            jsonObject = json.loads(payload.decode('utf8'))
            if 'state' in jsonObject:
                self.listeningMessages += 1
                if self.listeningMessages == 2:
                    print("sending close 1000")
                    # close the connection
                    self.sendClose(1000)

            # if in streaming
            elif 'results' in jsonObject:
                jsonObject = json.loads(payload.decode('utf8'))
                hypothesis = ""
                # empty hypothesis
                if len(jsonObject['results']) == 0:
                    print("empty hypothesis!")
                # regular hypothesis
                else:
                    # dump the message to the output directory
                    jsonObject = json.loads(payload.decode('utf8'))

                    res = jsonObject['results'][0]
                    hypothesis = res['alternatives'][0]['transcript']
                    bFinal = (res['final'] is True)
                    if bFinal:
                        print('final hypothesis: "' + hypothesis + '"')
                        self.summary[self.uttNumber]['hypothesis'] += hypothesis + ','
                    else:
                        print('interim hyp: "' + hypothesis + '"')

    def onClose(self, wasClean, code, reason):

        print("onClose")
        print("WebSocket connection closed: {0}, code: {1}, clean: {2}, "
              "reason: {0}".format(reason, code, wasClean))
        self.summary[self.uttNumber]['status']['code'] = code
        self.summary[self.uttNumber]['status']['reason'] = reason

        # create a new WebSocket connection if there are still
        # utterances in the queue that need to be processed
        self.queue.task_done()

        if not self.factory.prepareUtterance():
            return

        # SSL client context: default
        if self.factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(self.factory, contextFactory)
# function to check that a value is a positive integer
def check_positive_int(value):
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError(
            '"%s" is an invalid positive int value' % value)
    return ivalue
# function to check the credentials format
def check_credentials(credentials):
    elements = credentials.split(":")
    if len(elements) == 2:
        return elements
    else:
        raise argparse.ArgumentTypeError(
            '"%s" is not a valid format for the credentials ' % credentials)


'''利用IBM的SDK,获取识别后的文本'''




if __name__ == '__main__':
    # 从数据库中取出一条数据

    def get_text(audio_path, proxy):
        # parse command line parameters
        parser = argparse.ArgumentParser(
            description=('client to do speech recognition using the WebSocket '
                         'interface to the Watson STT service'))
        parser.add_argument(
            '-type', action='store', dest='contentType', default='audio/mp3',
            help='audio content type, for example: \'audio/l16; rate=44100\'')
        # parser.add_argument(
        #     '-model', action='store', dest='model', default='en-US_BroadbandModel',
        #     help='STT model that will be used')
        parser.add_argument(
            '-model', action='store', dest='model', default='ar-AR_BroadbandModel',
            help='STT model that will be used')
        parser.add_argument(
            '-amcustom', action='store', dest='am_custom_id', default=None,
            help='id of the acoustic model customization that will be used', required=False)
        parser.add_argument(
            '-lmcustom', action='store', dest='lm_custom_id', default=None,
            help='id of the language model customization that will be used', required=False)
        parser.add_argument(
            '-threads', action='store', dest='threads', default='1',
            help='number of simultaneous STT sessions', type=check_positive_int)
        parser.add_argument(
            '-optout', action='store_true', dest='optOut',
            help=('specify opt-out header so user data, such as speech and '
                  'hypotheses are not logged into the server'))
        parser.add_argument(
            '-tokenauth', action='store_true', dest='tokenauth',
            help='use token based authentication')

        args = parser.parse_args()
        # logging
        log.startLogging(sys.stdout)
        # add audio files to the processing queue
        q = Queue.Queue()
        # fileName = '/Users/qiyue/myxuni/pngtree/speech_audio/3min/9647730104474_5b44b3a2ddd8e328.mp3'
        # j将任务加入队列
        q.put((0, audio_path))
        hostname = "stream.watsonplatform.net"
        headers = {'X-WDC-PL-OPT-OUT': '1'} if args.optOut else {}
        '''获取token'''
        token = Utils.getAuthenticationToken(proxy)
        if token:
            headers['X-Watson-Authorization-Token'] = token
        else:
            return False
        # create a WS server factory with our protocol
        fmt = "wss://{}/speech-to-text/api/v1/recognize?model={}"
        url = fmt.format(hostname, args.model)
        if args.am_custom_id != None:
            url += "&acoustic_customization_id=" + args.am_custom_id
        if args.lm_custom_id != None:
            url += "&customization_id=" + args.lm_custom_id
        summary = {}
        factory = WSInterfaceFactory(q, summary, args.contentType,
                                     args.model, url, headers, debug=False)
        factory.protocol = WSInterfaceProtocol
        for i in range(min(int(args.threads), q.qsize())):
            factory.prepareUtterance()
            # SSL client context: default
            if factory.isSecure:
                contextFactory = ssl.ClientContextFactory()
            else:
                contextFactory = None
            connectWS(factory, contextFactory)
        reactor.run()
        # dump the hypotheses to the output file

        for key, value in enumerate(sorted(summary.items())):
            value = value[1]
            print(type(value['hypothesis']))
            try:
                text = value['hypothesis'].decode('unicode_escape')[:-1]
                # text = value['hypothesis'].encode('utf-8')[:-1]
            except UnicodeDecodeError:
                text = value['hypothesis'].encode('utf-8')[:-1]
                print('decode unicode faild....')
            except Exception as e:
                print('encode utf8 faild....')
                print(str(e))
                text = value['hypothesis'][:-1]
            # if value['status']['code'] == 1000:
            #     print('{}: {} {}'.format(key, value['status']['code'],
            #                              value['hypothesis'].encode('utf-8')))
            # else:
            #     fmt = '{}: {status[code]} REASON: {status[reason]}'
            #     print(fmt.format(key, **status))

        print(text)
        return text
    def speech_to_text(audio, proxy):
        temp_file_path = audio['save_path'][:-3] + 'mp3'
        print(temp_file_path)
        if os.path.exists(temp_file_path):
            pass
        else:
            command = '/usr/local/bin/ffmpeg -i %s -ar 16000 %s' % (audio['save_path'], temp_file_path)
            pipe = subprocess.check_call(command, stdout=subprocess.PIPE, shell=True)
            if pipe == 0:
                print('Subprocess excute sucessed! ')
                if os.path.exists(temp_file_path):
                    print('Temp_file make sucessed!')
                else:
                    print('Temp_file make faild!')
                    return False
            else:
                print('Subprocess excute Faild! ')
                return False
        try:
            text = get_text(temp_file_path, proxy)
            db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio',
                                 use_unicode=True,
                                 charset='utf8')
            cocur = db.cursor()
            if text:
                # text = text.decode('unicode_escape')
                # 修改audio表的status为时间戳
                sql = 'update show_caller_audio set speech_status = "%s" where id =%s' % (
                    int(time.time()), audio['id'])
                try:
                    cocur.execute(sql)
                    db.commit()
                except Exception as e:
                    print('text save to mysql faild:reason is    :')
                    print(str(e))
                    db.rollback()
                # 吧text存入数据库
                sql = 'insert into show_caller_audio_text(cc,tel_number,save_path,audio_language,`size`,speech_text,file_name) VALUES ("%s","%s","%s","ar","%s","%s","%s")' % (
                    audio['cc'], audio['tel_number'], audio['save_path'], audio['size'], text,
                    audio['file_name'])
            else:
                # 更新audio数据表为识别失败-10
                sql = 'update show_caller_audio set speech_status = -10 where id =%s' % audio['id']

            try:
                cocur.execute(sql)
                db.commit()
            except Exception as e:
                print(str(e))
                db.rollback()
            # 删除临时文件
            os.remove(temp_file_path)
            db.close()
        except Exception as e:
            os.remove(temp_file_path)
            # 识别失败,可能是代理失效
            print(str(e))
            print('Proxy may faild')
            # 更新audio数据表为识别失败-100  代理原因
            sql = 'update show_caller_audio set speech_status = -100 where id =%s' % audio['id']
            db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
            cocur = db.cursor()
            try:
                cocur.execute(sql)
                db.commit()
            except Exception as e:
                print(str(e))
                db.rollback()
            db.close()


    import sys

    # make a copy of original stdout route
    stdout_backup = sys.stdout
    # define the log file that receives your log info
    log_file = open("/home/wwwroot/show_caller_audio/message_ar.log", "w")
    # redirect print output to log file
    sys.stdout = log_file
    data = get_data_from_mysql()
    time.sleep(random.randint(10, 25))
    if data == 'no data':
        exit()
    elif data:
        # 获取音频时长
        duration = data['duration']
        print(data)
        proxy = get_proxy()
        if proxy:
            speech_to_text(data, proxy)
        else:
            print('Get account faild...')
    else:
        print('Get data faild or audio is too short or too lang...')
    log_file.close()
    # while True:
    #     # time.sleep(random.randint(10,30))
    #     data = get_data_from_mysql()
    #     if data == 'no data':
    #         break
    #     elif data:
    #         # 获取音频时长
    #         duration = data['duration']
    #         print(data)
    #         proxy = get_proxy()
    #         if proxy:
    #             speech_to_text(data,proxy)
    #
    #         else:
    #             print('Get account faild...')
    #     else:
    #         print('Get data faild or audio is too short or too lang...')
