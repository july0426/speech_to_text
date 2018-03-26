#coding:utf8
'''控制阿拉伯语的识别中心'''
import MySQLdb,subprocess,time,random
while True:

    db = MySQLdb.connect('163.172.254.11', 'speech_text_ar', 'speechIBM', 'show_caller_audio')
    cocur = db.cursor()
    # sql = 'select id,audio_language from show_caller_audio where speech_status = 0 and audio_language in ("ar","en") and cc in (1,91,212,964,972,20)  ORDER BY id DESC limit 1'
    sql = 'select id,audio_language from show_caller_audio where speech_status = 0 and audio_language="en" and cc in (1,91)  ORDER BY id DESC limit 1'

    try:
        cocur.execute(sql)
        # 获取一条数据
        data = cocur.fetchone()
        if data:
            print data
            if data[1] == 'en':
                commond = '/usr/local/anaconda2/bin/python  /home/wwwroot/show_caller_audio/speech_to_text_IBM_socket_en.py'
            elif data[1] == 'ar':
                commond = '/usr/local/anaconda2/bin/python  /home/wwwroot/show_caller_audio/speech_to_text_IBM_socket_ar.py'
            print(commond)
            p = subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True)
            sleepTime = random.randint(30,50)
            print("Random sleep time is : ",sleepTime)
            time.sleep(sleepTime)
        else:
            break
    except Exception as e:
        print str(e)
        break
