#coding:utf-8

import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib2
import urllib
import datetime
from flask import make_response

app = Flask(__name__)

RSS_FEEDS = {
    'BBC':'http://feeds.bbci.co.uk/news/rss.xml',
    'CNN':'http://rss.cnn.com/rss/edition.rss',
    'FOX':'http://feeds.foxnews.com/foxnews/latest',
    'IOL':'http://www.iol.co.za/cmlink/1.640',
    'QQ':'http://view.news.qq.com/index2010/zhuanti/ztrss.xml'
}

DEFAULTS = {'publication':'BBC',
            'city':'Seoul,KR',
            'currency_from':'CNY',
            'currency_to':'KRW'}

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=03f1ab101e00331ccadda4e59e5d4c3b'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=8e527451c69f4b8a9cb3a8a9bbc2b109'

@app.route('/')
def home():

    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    city = get_value_with_fallback('city')
    weather = get_whether(city)

    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rate(currency_from,currency_to)

    response = make_response(render_template('home.html',
                           articles = articles,
                           rss_source = publication,
                           rss_sources = sorted(list(RSS_FEEDS.keys())),
                           weather = weather,
                           currency_from = currency_from,
                           currency_to = currency_to,
                           rate = rate,
                           # sorted()为python内置排序函数
                           currencies = sorted(currencies)))
    # 365天后过期
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

def get_news(query):
    if not query:
        publication = 'bbc'
    else:
        publication = query
    # return dictionary including all news storys
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_whether(query):
    # URLs中不能有空格等，通过这个函数可以帮助转换参数为符合URLs格式的参数
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    # 通过这个函数来访问这个URLs,拿到返回的JSON天气数据
    data = urllib2.urlopen(url).read()
    # 使用json的loads函数来解析接受到的数据,然后从json格式的数据变成python ditionary格式的数据
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description':parsed['weather'][0]['description'],
                   'temperature':parsed['main']['temp'],
                   'city':parsed['name'],
                   'country':parsed['sys']['country']
                   }
    return weather

def get_rate(frm,to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if key == 'publication':
        cookies_value = request.cookies.get(key)
        if cookies_value and cookies_value in RSS_FEEDS:
            return cookies_value
    else:
        if request.cookies.get(key):
            return request.cookies.get(key)
    return DEFAULTS[key]

if __name__ == '__main__':
    app.run(port=5000, debug=True)