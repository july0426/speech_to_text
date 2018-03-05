#coding:utf8
import requests
res = requests.get('https://www.baidu.com')
print res.text
a = ['a',2]
c = 'a'
if c in str(a):
    print a
else:
    a.append(c)
print a
li = [x for x in range(0,100) if x <90 if x >50]
print li
with open('./proxy.txt','wb') as f:
    for i in range(500,1000):
        f.writelines('187.123.12.1:'+str(i)+'\n')
with open('./proxy.txt','r+') as f:
    a = f.readlines()
    print a
import linecache
import random
a = random.randrange(1, 500)  # 生成随机数
# 从文件poem.txt中对读取第a行的数据
theline = linecache.getline(r'proxy.txt', a)
print theline
