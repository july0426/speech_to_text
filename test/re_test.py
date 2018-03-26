#coding:utf8
import requests
url = 'https://180info.co.uk'
proxy = {
    "http":"http://23.19.101.37:29842",
    "https":"https://23.19.101.37:29842"
}
url1 = 'https://who-called.co.uk/'
print requests.get(url1).text