#coding:utf8
import requests,jsonpath,json,base64,MySQLdb,os,time,random,langid
'''从数据库提取代理'''
def get_proxy():
    db = MySQLdb.connect('localhost', 'aio_music', 'aio_music_pass', 'kiss_png')
    cursor = db.cursor()
    sql = "select id,proxy,counts,faild from proxy_google_tag order by status asc limit 1 "
    try:
        cursor.execute(sql)
        proxies = cursor.fetchone()
        counts = proxies[2] + 1
        # 更新代理时间戳
        sql = "update proxy_google_tag set status=%d,counts=%d where id=%d" % (int(time.time()),counts, proxies[0])
        cursor.execute(sql)
        db.commit()
    except Exception, e:
        db.rollback()
        proxies = ''
    db.close()
    return proxies
'''图片base64编码'''
def encode_image(file_path):
    with open(file_path,'rb') as f:
        image_content = f.read()
        return base64.b64encode(image_content)
'''从数据库中取出文件本地路径'''
def get_path():
    db = MySQLdb.connect('localhost', 'aio_music', 'aio_music_pass', 'kiss_png')
    cursor = db.cursor()
    # 连接数据库，取出图片路径
    sql = "select id,icon_local_path,url from png_center_pdts where tag_status = 0 order by priority desc limit 1"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        if data:
            id = data[0]
            print id
            # 数据取出后改一下状态，表示开始处理
            sql = "update png_center_pdts set tag_status=2 where id=%d" % id
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print str(e)
                db.rollback()
            # 判断图片是否存在
            if os.path.exists(data[1]):
                pass
            else:
                data = ''
                print 'png not exists'
        else:
            data=''
    except Exception as e:
        print "Process Done"
        db.rollback()
        data = ''
    db.close()
    return data
'''提取labels'''
def get_labels(text):
    # 提取labels
    labels = jsonpath.jsonpath(text, '$..labelAnnotations')
    label_list = []
    if labels:
        labels = labels[0]
        for label in labels:
            if 'description' in label.keys():
                label_list.append(label['description'].replace("'","\\'"))
    label_list = list(set(label_list))
    label_str = '\n '.join(label_list)
    return label_str
'''提取webEntities'''
def get_webEntities(text):
    # 提取webEntities
    webEntities = jsonpath.jsonpath(text, '$..webEntities')
    web_list = []
    key_list = []
    web_tag2_list = []
    if webEntities:
        webEntities = webEntities[0]
        for web in webEntities:
            if 'description' in web.keys():
                try:
                    description = web['description'].replace("'", "\\'").encode('windows-1251')
                except:
                    description = web['description'].replace("'", "\\'")
                    print description, langid.classify(description)
                if description not in key_list:
                    key_list.append(description)
                    print description, langid.classify(description)
                    if langid.classify(description)[0] == 'en':
                        # web_dict[description] = web['score']
                        web_dict = '"%s":"%s"' % (description, web['score'])
                        web_list.append(web_dict)
                    else:
                        web_tag2_dict = '"%s":"%s"' % (description, web['score'])
                        web_tag2_list.append(web_tag2_dict)
    web_list = ','.join(web_list)
    web_list = "{" + web_list + "}"
    web_tag2_list = ','.join(web_tag2_list)
    web_tag2_list = "{" + web_tag2_list + "}"
    print 'web_list:', web_list
    return (web_list, web_tag2_list)
'''请求Google接口,返回识别的数据,存入数据库'''
def goole_vision():
    headers = {
    'authority':'cxl-services.appspot.com',
    'method':'POST',
    'path':'/proxy?url=https%3A%2F%2Fvision.googleapis.com%2Fv1%2Fimages%3Aannotate',
    'scheme':'https',
    'accept':'*/*',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.9',
    'content-type':'text/plain;charset=UTF-8',
    'origin':'https://cloud.google.com',
    'referer':'https://cloud.google.com/vision/?authuser=1',
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    sleeptime = random.randint(5,20)
    time.sleep(sleeptime)
    print sleeptime
    # 获取要是别的图片路径
    path_id = get_path()
    if path_id:
        file_path = path_id[1]
        id = path_id[0]
        old_url = path_id[2]
        # 构造请求的json数据,post发送
        requests_json = {
            "requests":[
                {
                    "image":{
                        "content":encode_image(file_path)
                    },
                    "features":[
                        {
                            "type": "LABEL_DETECTION",
                            "maxResults": 50
                        },
                        {
                            'type': "TEXT_DETECTION",
                            'maxResults': 50
                        },
                        {
                            "type": "WEB_DETECTION",
                            "maxResults": 50
                        }
                    ],
                    "imageContext":{
                        "cropHintsParams":{
                            "aspectRatios":[
                                0.8,
                                1,
                                1.2
                            ]
                        }
                    }
                }
            ]
        }
        # 识别接口
        url = 'https://cxl-services.appspot.com/proxy?url=https%3A%2F%2Fvision.googleapis.com%2Fv1%2Fimages%3Aannotate'
        # 加代理
        proxy = get_proxy()
        proxie = {
            'http': 'http://%s' % proxy[1],
            'https': 'https://%s' % proxy[1],
        }
        print proxie
        try:
            res = requests.post(url,headers=headers,data = json.dumps(requests_json),proxies = proxie)
        except Exception as e:
            print "Get Tag Faild"
            # 更改代理表
            proxy_faild = proxy[3] + 1
            db = MySQLdb.connect('localhost', 'aio_music', 'aio_music_pass', 'kiss_png')
            cursor = db.cursor()
            proxy_sql = "update proxy_google_tag set faild=%d,counts=%d where id=%d " % (proxy_faild, proxy[2], proxy[0])
            cursor.execute(proxy_sql)
            db.commit()
            sql = "update png_center_pdts set tag_status = 0 where id=%d " % id
            cursor.execute(sql)
            db.commit()
            db.close()
            return False
        # 不加代理
        # res = requests.post(url, headers=headers, data=json.dumps(requests_json))
        # 把返回的数据转成json格式
        res_json = json.loads(res.text)
        labels = get_labels(res_json)
        webEntities = get_webEntities(res_json)
        if len(webEntities) > 1:
            web_tag2 = webEntities[1]
            webEntities = webEntities[0]
        else:
            webEntities = webEntities[0]
            web_tag2 = ''
        # 连接数据库
        db = MySQLdb.connect('localhost', 'aio_music', 'aio_music_pass', 'kiss_png')
        cursor = db.cursor()
        # 获取texts
        texts = jsonpath.jsonpath(res_json, '$..textAnnotations')
        # 获取文本语言
        langua = jsonpath.jsonpath(res_json, '$..languageCode')
        # 提取相关网址
        pages_url = jsonpath.jsonpath(res_json, '$..pagesWithMatchingImages..url')
        if pages_url:
            pages_url = pages_url[::2]
            pages_url_new = [str(i) for i in pages_url]
            print pages_url_new
            #  png_google_web 中的web_txt 字段中，并将提取数据的id 写入字段img_id 中，将提取数据的url 写入字段url 中
            sql = 'insert into png_google_web(img_id,url,web_txt) values("%s","%s","%s")' % (id,old_url,pages_url_new)
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print str(e)
        if labels:
            print "Get Tag Success"
            if texts:
                texts = texts[0][0]['description']
                # 主要的文本语言
                # locale = jsonpath.jsonpath(res_json, '$..locale')[0]
                langu = list(set(langua))
                # 具体的文本语言,可能会含有其他语言
                langua = ','.join(langu)
                print langua
                sql = "update png_center_pdts set tag_status=15,lab_tag='%s',web_tag='%s',web_tag2='%s',lang='%s',lang_txt='%s' where id='%s'" % (labels, webEntities,web_tag2, langua, texts, id)
            else:
                sql = "update png_center_pdts set tag_status=15,lab_tag='%s',web_tag='%s',web_tag2='%s' where id='%d'" % (labels, webEntities,web_tag2,id)
        else:
            #更改代理表
            proxy_faild = proxy[3] + 1
            proxy_sql = "update proxy_google_tag set faild=%d,counts=%d where id=%d " % (proxy_faild,proxy[2],proxy[0])
            cursor.execute(proxy_sql)
            db.commit()
            print "Faild To Get"
            sql = "update png_center_pdts set tag_status = -11 where id=%d " % id
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print str(e)
        db.close()
if __name__ == '__main__':
    goole_vision()



