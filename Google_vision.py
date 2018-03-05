#coding:utf8
import requests,jsonpath,json,base64,MySQLdb,os
'''从数据库提取代理'''
def get_proxy():
    db = MySQLdb.connect('localhost', 'root', '123456', 'test')
    cursor = db.cursor()
    sql = "select * from pngtree_proxy where id = "
    try:
        cursor.execute(sql)
        proxies = cursor.fetchone()
        # 更新代理时间戳
        # sql = "update pngtree_proxy set status=%d where id=%d" % (int(time.time()), proxies[0])
        # cursor.execute(sql)
        proxy = {
            'http': 'http://%s' % proxie,
            'https': 'https://%s' % proxie,
        }
        db.commit()
        return proxy
    except Exception, e:
        print sql
        print str(e)
        db.rollback()
        proxy = 0
        return proxy
    db.close()
'''图片base64编码'''
def encode_image(file_path):
    with open(file_path,'rb') as f:
        image_content = f.read()
        return base64.b64encode(image_content)
'''从数据库中取出文件本地路径'''
def get_path():
    db = MySQLdb.connect('localhost', 'root', '123456', 'pngtree_201712')
    cursor = db.cursor()
    # 连接数据库，取出图片路径
    sql = "select id,icon_path from pngtree_pdts_test where status = 0 order by id limit 1"
    # sql = "select id,icon_path from pngtree_pdts_test where id=19225"
    try:
        cursor.execute(sql)
        data = cursor.fetchone()
        if data:
            id = data[0]
            icon_path = data[1]
            print icon_path
            # 数据取出后改一下状态，表示开始处理
            sql = "update pngtree_pdts_test set status=1 where id=%d" % id
            # try:
            #     cursor.execute(sql)
            #     db.commit()
            # except Exception as e:
            #     print str(e)
            #     db.rollback()
            # 判断图片是否存在
            if os.path.exists(icon_path):
                return data
            else:
                print '图片不存在'
    except Exception as e:
        print str(e)
        db.rollback()
    db.close()
'''提取labels'''
def get_labels(text):
    # 提取labels
    labels = jsonpath.jsonpath(text, '$..labelAnnotations')
    label_list = []
    if labels:
        labels = labels[0]
        for label in labels:
            if 'description' in label.keys():
                label_list.append(label['description'].replace("'",' '))
    label_list = list(set(label_list))
    label_str = '\n'.join(label_list)
    print label_str
    return label_str
'''提取webEntities'''
def get_webEntities(text):
    # 提取webEntities
    webEntities = jsonpath.jsonpath(text, '$..webEntities')
    web_list = []
    key_list = []
    if webEntities:
        webEntities = webEntities[0]
        for web in webEntities:
            if 'description' in web.keys():
                description = web['description'].replace("'",' ').encode('windows-1251')
                if description not in key_list:
                    key_list.append(description)
                    web_dict = {description: web['score']}
                    web_list.append(str(web_dict))
    web_list = ','.join(web_list)
    print 'web_list:',web_list
    return web_list
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
    # 获取要是别的图片路径
    path_id = get_path()
    if path_id:
        file_path = path_id[1]
        id = path_id[0]
        # 构造请求的json数据,post发送
        requests_json = {
            "requests":[
                {
                    "image":{
                        "content":encode_image(file_path)
                    },
                    "features":[
                        {
                            "type":"LABEL_DETECTION",
                            "maxResults":50
                        },
                        {
                            "type":"TEXT_DETECTION",
                            "maxResults":50
                        },
                        {
                            'type': "TEXT_DETECTION",
                            'maxResults': 50
                        },
                        {
                            "type":"WEB_DETECTION",
                            "maxResults":50
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
        # proxy = get_proxy()
        # res = requests.post(url,headers=headers,data = json.dumps(requests_json),proxies = proxy)
        # 不加代理
        res = requests.post(url, headers=headers, data=json.dumps(requests_json))
        # print res.text,type(res.json)
        # 把返回的数据转成json格式
        res_json = json.loads(res.text)
        # print res.text
        labels = get_labels(res_json)
        webEntities = get_webEntities(res_json)
        db = MySQLdb.connect('localhost', 'root', '123456', 'pngtree_201712')
        cursor = db.cursor()
        # 判断是否含有text,有的话,提取语种标识
        texts = jsonpath.jsonpath(res_json,'$..textAnnotations')
        langua = jsonpath.jsonpath(res_json,'$..languageCode')
        if texts:
            texts = texts[0][0]['description']
            # 主要的文本语言
            locale = jsonpath.jsonpath(res_json,'$..locale')[0]
            print locale
            langu = list(set(langua))
            # 具体的文本语言,可能会含有其他语言
            langua = ','.join(langu)
            print langua
            if 'zh' in langua:
                print texts
                sql = 'update pngtree_pdts_test set labels="%s",webEntities="%s",langu="%s",texts="%s" where id="%s"' % (labels,webEntities,langua,texts,id)
            else:
                sql = 'update pngtree_pdts_test set labels="%s",webEntities="%s",langu="%s",texts="%s" where id="%s"' % (labels, webEntities, langua,texts,id)
        else:
            sql = 'update pngtree_pdts_test set labels="%s",webEntities="%s" where id="%s"' % (labels, webEntities, id)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print sql
            print str(e)
            db.rollback()
        db.close()
if __name__ == '__main__':
    # for i in range(7):
    #     goole_vision()
    goole_vision()



