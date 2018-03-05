#coding:utf8
import requests,re,json,base64,subprocess,os,shutil,MySQLdb,time
from pydub import AudioSegment
'''利用谷歌的语音识别接口，返回识别后的文本'''
def get_result(file_path):
    url = 'https://speech.googleapis.com/v1/speech:recognize?fields=results&key=AIzaSyBrqJW6Nj5Zha2M8hkhP4uH7yjP6nWBv3Q'
    data = {
         "config":{
          "encoding": "flac",
          "languageCode": "en-US",
          "sampleRateHertz": 8000,
          "enableWordTimeOffsets":False,
         },
         "audio": {
          "content": encode_audio(file_path)
         }
    }
    res = requests.post(url,data=json.dumps(data))
    text= res.text
    print text
    text = json.loads(text)
    try:
        transcript = text['results'][0]['alternatives'][0]['transcript']
        print transcript
    except:
        transcript = ''
    return transcript

def encode_audio(file_path):
    with open(file_path,'rb') as f:
        audio_content = f.read()
        return base64.b64encode(audio_content)

def cut_audio(audio_len,file_path):
    # temp_file_path = file_path[:-4] + '_cut.flac'
    temp_dir_path = re.sub(r'/[\w-]+\.amr','',file_path)
    temp_dir_path += '/temp'
    print temp_dir_path
    if not os.path.exists(temp_dir_path):
        os.mkdir(temp_dir_path)
    audio_len_int= int(audio_len)
    file_range = audio_len_int/60
    res_list = []
    for i in range(file_range):
        temp_file_path = temp_dir_path +'/'+ 'temp%s.flac' % i
        commond = 'ffmpeg -ss 00:%02d:00 -t 00:%02d:00 -i %s %s' % (i,i+1,file_path,temp_file_path)
        # pipe = subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True).stdout
        pipe = subprocess.call(commond, shell=True)
        if pipe == 0:
            print pipe
            # res_text = get_result(temp_file_path)
            # res_list.append(res_text)
        else:
            print 'cut file faild'
        print commond
    last_file = audio_len_int + 1 - file_range * 60
    temp_file_path = temp_dir_path + '/' + 'temp%s.flac' % (file_range)
    commond = 'ffmpeg -ss 00:%02d:00 -t 00:%02d:00 -i %s %s' % (file_range, file_range + 1, file_path, temp_file_path)
    print commond
    subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True)
    print temp_file_path
    time.sleep(10)
    print os.path.exists(temp_file_path)
    print encode_audio(temp_file_path)
    # res_text = get_result(temp_file_path)
    # res_list.append(res_text)
    text = ','.join(res_list)

    # except:
    #     print 'http post faild'
    shutil.rmtree(temp_dir_path)
    return text

def get_audio_from_mysql():
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cursor = db.cursor()
    # 连接数据库，取出图片路径
    sql = "select id,path from speech where status = 0 order by id limit 1"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        if data:
            id = data[0]
            path = data[1]
            print path
            # 数据取出后改一下状态，表示开始处理
            sql = "update speech set status=1 where id=%d" % id
            # try:
            #     cursor.execute(sql)
            #     db.commit()
            #     db.close()
            # except Exception as e:
            #     print str(e)Dear All:
            #     db.rollback()
            #     db.close()
            # 判断图片是否存在
            if os.path.exists(path):
                return data
            else:
                print 'audio is not exists'
                return False
    except Exception as e:
        print str(e)
        db.rollback()
        db.close()
        return False

def save_text_to_mysql(text,id):
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cursor = db.cursor()
    sql = "update speech set text='%s' where id=%d" % (text,id)
    try:
        cursor.execute(sql)
        db.commit()
        print 'Text save sucess'
    except Exception as e:
        print str(e)
        db.rollback()
    db.close()

def get_audio_len(file_path):
    sound1 = AudioSegment.from_file(file_path, format="amr")
    print len(sound1)
    audio_len = len(sound1)/1000
    print audio_len
    return audio_len
    # commond = 'ffprobe -v quiet -print_format json -show_format -show_streams %s' % file_path
    # print commond
    # p = subprocess.Popen(commond, stdout=subprocess.PIPE, shell=True)
    # js = p.stdout.read()
    # print type(js)
    # js = json.load(p.stdout.read())
    # print js
    # print js['streams'][0]['duration'],type(js)
    # return float(js['streams'][0]['duration'])
if __name__ == '__main__':
    # 从数据库提取一条数据
    data = get_audio_from_mysql()
    if data:
        # 获取id,音频文件本地存储路径
        id = data[0]
        file_path = data[1]
        # 获取音频时长
        # audio_len = float(get_audio_len(file_path))
        audio_len = 76
        # 如果音频长度>60s,需要进行切割,切割后分开进行识别,在合并在一起
        if audio_len >= 60.0:
            text = cut_audio(audio_len,file_path)
        else:
            # 如果音频小于60s,直接进行识别
            text = get_result(file_path)
        save_text_to_mysql(text,id)
    else:
        print 'Get data from mysql faild...'
    # get_result('/Users/qiyue/myxuni/pngtree/google_speech/temptemp0.flac')
    # cut_audio(file_path)
    # file_path = '/Users/qiyue/myxuni/pngtree/ocr/who1.jpeg'
    # print encode_audio(file_path)