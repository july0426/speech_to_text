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
    加一个字段speech_status,初始值为0,已识别1,识别失败2,不需要识别3(过短或者过长)
2.新建一个IBM账号表show_caller_IBM_account:
    1.id
    2.username
    3.password
    4.duration  初始值为0,最大值60000,每月1号重置为0
    5.status    初始值为0,duration超过60000时,修改为0,每月1号重置为0


'''
from __future__ import print_function
import json,re,MySQLdb,os,subprocess
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1
'''获取音频时长'''
def get_duration(save_path):
    pass
'''从数据库中提取一条音频数据'''
def get_data_from_mysql():
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cocur = db.cursor()
    sql = 'select id,save_path from show_caller_audio where speech_status = 0 and audio_language="ar" limit 1'
    try:
        cocur.execute(sql)
        data = cocur.fetchone()
        if data:
            id = data[0]
            save_path = data[1]
            print(data)
            duration = get_duration(save_path)
            if second < 240 and second > 5:
                print(second)
                return {'id':id,'save_path':data[1],'duration':second}
            else:
                print('audio is too lang or too short')
                sql = 'update show_caller_audio set speech=3 where id=%s' % id
                try:
                    cocur.execute(sql)
                    db.commit()
                    print('Speech_status update success!')
                except Exception as e:
                    print('Speech_status update faild.....')
                    print(str(e))
                    db.rollback()
            db.close()
        else:
            print('No data to process')
            return False
    except:
        print('No data to process....')
        return False
'''从数据库中提取一个IBM账号'''
def get_account():
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cocur = db.cursor()
    sql = 'select id,save_path,duration from show_caller_IBM_ where speech_status = 0 and audio_language="ar" limit 1'
    try:
        cocur.execute(sql)
        data = cocur.fetchone()
        if data:
            id = data[0]
            print(data)
            duration = data[2]
            duration_s = duration.split(':')
            time_to_second = lambda x: int(x[0] * 60) + int(x[1])
            second = time_to_second(duration_s)
            if second < 240 and second > 5:
                print(second)
                return {'id': id, 'save_path': data[1], 'duration': second}
            else:
                print('audio is too lang or too short')
                sql = 'update show_caller_audio set speech=3 where id=%s' % id
                try:
                    cocur.execute(sql)
                    db.commit()
                    print('Speech_status update success!')
                except Exception as e:
                    print('Speech_status update faild.....')
                    print(str(e))
                    db.rollback()
            db.close()
        else:
            print('No data to process')
            return False
    except:
        print('No data to process....')
        return False
'''从数据库中获取一个代理'''
def get_proxy():
    pass
'''利用IBM的SDK,获取识别后的文本'''
def speech_to_text(account,audio):
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cocur = db.cursor()
    speech_to_text = SpeechToTextV1(
        username='5dbeced5-b1f2-49d9-97c9-4be855fe4c93',
        password='OGyHxNroqlEX',
        x_watson_learning_opt_out=False
    )
    # print(json.dumps(speech_to_text.models(), indent=2))
    with open(join(dirname(__file__), '/Users/qiyue/myxuni/pngtree/google_speech/333_fa54709dd09a1f9e.mp3'),
              'rb') as audio_file:
        text = json.dumps(speech_to_text.recognize(audio_file, content_type='audio/mp3',model='ar-AR_BroadbandModel', timestamps=True,word_confidence=False),indent=2)
    if text:
        sql = 'update show_caller_IBM_account set duration=duration+%s where id=%s' % (audio['duration'],account['id'])
        try:
            cocur.execute(sql)
            db.commit()
            print('Speech_status update success!')
        except Exception as e:
            print('Speech_status update faild.....')
            print(str(e))
            db.rollback()
    print(text)
    # print(text)
    re_trans = re.compile(r'"transcript":.*?}',re.S)
    text_list = re.findall(re_trans,text)
    print(text_list)
    re_transcript = re.compile(r'"transcript": "(.*)?"')
    text_list_new = []
    for i in text_list:
        text = re.search(re_transcript,i)
        if text:
            text = text.group(1)
            text_list_new.append(text)
    text = ','.join(text_list_new)
    text = text.decode('unicode_escape')
    print(text)


if __name__ == '__main__':
    data = get_data_from_mysql()
    # print(data)
    file_path = '/Users/qiyue/myxuni/pngtree/speech_audio/4min/972111_c3b6a05586d3f86f.mp3'
    commond = 'ffprobe -v quiet -print_format json -show_format -show_streams %s' % file_path
    print(commond)
    p = subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True)
    js = p.stdout.read()
    print(type(js))
    print(js)
    duration_re = re.compile(r'"duration": "(.*)?"')
    duration = re.search(duration_re,js)
    if duration:
        duration = duration.group(1)
        duration_s = int(duration.split('.')[0])
        duration_ss = int(duration.split('.')[1][0])
        print(duration_ss)
        if duration_ss > 3:
            duration = duration_s + 1
        else:
            duration = duration_s
        print(duration)

    # return float(js['streams'][0]['duration'])