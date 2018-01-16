#coding:utf-8

import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib2
import urllib

app = Flask(__name__)

RSS_FEEDS = {
    'bbc':'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn':'http://rss.cnn.com/rss/edition.rss',
    'fox':'http://feeds.foxnews.com/foxnews/latest',
    'iol':'http://www.iol.co.za/cmlink/1.640'
}

DEFAULTS = {'publication':'bbc',
            'city':'Seoul,KR',
            'currency_from':'CNY',
            'currency_to':'KRW'}

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=03f1ab101e00331ccadda4e59e5d4c3b'
CURRENCY_URL = 'https://openexchangerates.org//api/latest.json?app_id=8e527451c69f4b8a9cb3a8a9bbc2b109'

@app.route('/')
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_whether(city)
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from,currency_to)
    return render_template('home.html',
                           articles = articles,
                           weather = weather,
                           currency_from = currency_from,
                           currency_to = currency_to,
                           rate = rate,
                           # sorted()为python内置排序函数
                           currencies = sorted(currencies))

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = 'bbc'
    else:
        publication = query.lower()
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

if __name__ == '__main__':
    app.run(port=5000, debug=True)