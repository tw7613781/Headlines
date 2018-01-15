#coding:utf-8
import feedparser

from flask import Flask

app = Flask(__name__)

BBC_FEED = "http://feeds.bbci.co.uk/news/rss.xml"
Tencent_FEED = "http://news.qq.com/newsgn/rss_newsgn.xml"

@app.route('/')
def get_news():
    feed = feedparser.parse(BBC_FEED)
    feed2 = feedparser.parse(Tencent_FEED)
    # return dictionary including all news storys
    first_article = feed['entries'][0]
    second_artical = feed2['entries'][0]
    return """<html>
    <body>
        <h1> BBC Headlines </h1>
        <b>{0}</b> <br/>
        <i>{1}</i> <br/>
        <p>{2}</p> <br/>
        <hr/>
        <h1> 腾讯国内新闻 </h1>
        <b>{3}</b> <br/>
        <i>{4}</i> <br/>
        <p>{5}</p> <br/>
    </body>
    </html>
    """.format(first_article.get("title"), first_article.get("published"), first_article.get("summary"), second_artical.get("title"), second_artical.get("published"), second_artical.get("summary"))
    # using dict.get() to avoid key missing causing runtime error

if __name__ == '__main__':
    app.run(port=5000, debug=True)