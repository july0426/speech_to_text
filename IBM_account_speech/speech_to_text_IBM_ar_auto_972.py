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
import json,re,MySQLdb,os,subprocess,time
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1
'''获取音频时长'''
def get_duration(save_path):
    # 判断文件是否存在
    if os.path.exists(save_path):
        # 利用ffmpeg获取音频信息
        commond = 'ffprobe -v quiet -print_format json -show_format -show_streams %s' % save_path
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
    sql = 'select id,save_path,cc,tel_number,`size`,file_name from show_caller_audio where speech_status = 0 and audio_language="ar" and cc=972 ORDER BY id DESC limit 1'
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
'''从数据库中提取一个IBM账号'''
def get_account(audio_duration):
    # 建立数据库连接
    db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
    cocur = db.cursor()
    sql = 'select id,username,password,duration from show_caller_IBM_account where duration < 60000 order by duration asc limit 1'
    try:
        cocur.execute(sql)
        # 获取一条数据
        data = cocur.fetchone()
        if data:
            id = data[0]
            print(data)
            duration = int(data[3])
            new_duration = duration + audio_duration
            sql = 'update show_caller_IBM_account set duration=%s where id=%s' % (new_duration, id)
            try:
                cocur.execute(sql)
                db.commit()
            except Exception as e:
                print(str(e))
                db.rollback()
            if new_duration <60000:
                print(new_duration)
                return {'username': data[1], 'password': data[2],'id':data[0]}
            else:
                print('This account duration is used 60000,Replace a new account.')
                # 超出60000秒,就把账号状态改为时间戳
                sql = 'update show_caller_IBM_account set duration=%s where id=%s' % (new_duration, id)
                try:
                    cocur.execute(sql)
                    db.commit()
                except Exception as e:
                    print(str(e))
                    db.rollback()
                # 如果超出,就重新选择一个账号(递归)
                account = get_account(audio_duration)
                return account
            db.close()

        else:
            exit('No account to used')
            return False
    except:
        exit('No account to process....')
        return 'no account'
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
'''利用IBM的SDK,获取识别后的文本'''
def speech_to_text(account,audio,proxy):
    speech_to_text = SpeechToTextV1(
        username=account['username'],
        password=account['password'],
        x_watson_learning_opt_out=False
    )
    temp_file_path = audio['save_path'][:-3]+'mp3'
    print(temp_file_path)
    if os.path.exists(temp_file_path):
        pass
    else:
        command = 'ffmpeg -i %s -ar 16000 %s' % (audio['save_path'],temp_file_path)
        pipe = subprocess.check_call(command,stdout=subprocess.PIPE, shell=True)
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
        with open(join(dirname(__file__), temp_file_path),
                  'rb') as audio_file:
            text = json.dumps(speech_to_text.recognize(audio_file, content_type='audio/mp3',model='ar-AR_BroadbandModel', timestamps=True,word_confidence=False,proxies=proxy),indent=2)
        db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio', use_unicode=True,
                             charset='utf8')
        cocur = db.cursor()
        if text:
            #   正则匹配出识别后的音频
            re_trans = re.compile(r'"transcript":.*?}', re.S)
            text_list = re.findall(re_trans, text)
            print(text_list)
            re_transcript = re.compile(r'"transcript": "(.*)?"')
            text_list_new = []
            for i in text_list:
                text = re.search(re_transcript, i)
                if text:
                    text = text.group(1)
                    text_list_new.append(text)
            text = ','.join(text_list_new)
            # 把返回的文本解码
            text = text.decode('unicode_escape')
            if text:
                # 修改audio表的status为时间戳
                sql = 'update show_caller_audio set speech_status = "%s" where id =%s' % (int(time.time()),audio['id'])
                try:
                    cocur.execute(sql)
                    db.commit()
                except Exception as e:
                    print(str(e))
                    db.rollback()
                print(text)
                # 吧text存入数据库
                sql = 'insert into show_caller_audio_text(cc,tel_number,save_path,audio_language,`size`,speech_text,file_name) VALUES ("%s","%s","%s","ar","%s","%s","%s")' % (audio['cc'],audio['tel_number'],audio['save_path'],audio['size'],text,audio['file_name'])
            else:
                # 更新audio数据表为识别失败-10
                sql = 'update show_caller_audio set speech_status = -10 where id =%s' % audio['id']
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
        # print(text)
        db.close()
    except Exception as e:
        os.remove(temp_file_path)
        # 识别失败,可能是代理失效或者账号失效
        print(str(e))
        if 'requests.exceptions.ProxyError' in str(e):
            print('Proxy may faild')
            # 更新audio数据表为识别失败-100  代理原因
            sql = 'update show_caller_audio set speech_status = -100 where id =%s' % audio['id']
        else:
            print('Account may faild')
            # 更新audio数据表为识别失败-1000账号原因
            sql = 'update show_caller_audio set speech_status = -1000 where id =%s' % audio['id']
        db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
        cocur = db.cursor()
        try:
            cocur.execute(sql)
            db.commit()
        except Exception as e:
            print(str(e))
            db.rollback()
        db.close()




if __name__ == '__main__':
    # 从数据库中取出一条数据
    while True:
        time.sleep(15)
        data = get_data_from_mysql()
        if data == 'no data':
            break
        elif data:
            # 获取音频时长
            duration = data['duration']
            print(data)
            # 获取一个IBM账户
            account = get_account(duration)
            if account == 'no account':
                break
            elif account:
                print(account)
                # 获取代理
                proxy = get_proxy()
                if proxy:
                    speech_to_text(account, data,proxy)
            else:
                print('Get account faild...')
        else:
            print('Get data faild or audio is too short or too lang...')
    # 从数据库中取出一条数据
    # data = get_data_from_mysql()
    # if data:
    #     # 获取音频时长
    #     duration = data['duration']
    #     print(data)
    #     # 获取一个IBM账户
    #     account = get_account(duration)
    #     if account:
    #         print(account)
    #         # 获取代理
    #         # proxy = get_proxy()
    #         proxie = '61.220.26.97:80'
    #         proxy = {
    #             'http': 'http://%s' % proxie,
    #             'https': 'https://%s' % proxie,
    #         }
    #         if proxy:
    #             # 进行语音识别
    #             speech_to_text(account,audio,proxy)
    #         else:
    #             print('Get proxy faild...')
    #     else:
    #         print('Get account faild...')
    # else:
    #     print('Get data faild or audio is too short or too lang...')


    # audio = {'duration': 6, 'id': 2L, 'save_path': '/Users/qiyue/myxuni/pngtree/google_speech/+13304003418_133614fc2ad48d90.amr'}
    # account = {'username': '5dbeced5-b1f2-49d9-97c9-4be855fe4c93', 'password': 'OGyHxNroqlEX','id':1L}
    # proxie = '61.220.26.97:80'
    # proxy = {
    #     'http': 'http://%s' % proxie,
    #     'https': 'https://%s' % proxie,
    # }
    # speech_to_text(account,audio,proxy)