import config
from twitter import Twitter, OAuth
import http.client
import urllib
import re
import json
import random

def connect_qiita(page, ppage, tag, created, stocks):
    conn = http.client.HTTPSConnection("qiita.com", 443)
    url = "/api/v2/items?page="+ page+ "&per_page="+ ppage+ "&query=tag%3A"+ tag+ "+created%3A%3E"+ created+ "+stocks%3A%3E"+ stocks
    regex = r'[^\x00-\x7F]'
    matchedList = re.findall(regex,url)
    for m in matchedList:
        url = url.replace(m, urllib.parse.quote_plus(m, encoding="utf-8"))
    conn.request("GET", url)

    res = conn.getresponse()
    return res

def get_post(tag, response):
#    print(response.status, response.reason)
    data = response.read().decode("utf-8")
    jsonstr = json.loads(data)
    posts = [(jsonstr[i]["url"], jsonstr[i]["title"], tag) for i in range(len(jsonstr))]
    return posts[random.randint(0, len(posts)-1)]

def tweet(msg):
    t = Twitter(
        auth=OAuth(
            config.TW_TOKEN,
            config.TW_TOKEN_SECRET,
            config.TW_CONSUMER_KEY,
            config.TW_CONSUMER_SECRET,
        )
    )
    t.statuses.update(status=msg)

def make_tagstr(tag, exceptions=None):
    """
    Type of exceptions is dict
    """
    if exceptions == None:
        return " #" + tag + " に関する"
    else:
        if tag not in exceptions:
            return " #" + tag + " に関する"
        else:
            return exceptions[tag] 

def main():
    PAGE, PAR_PAGE, CREATED, STOCKS = "1", "5", "2017-09-20", "5"
    BIGGINER = ["初心者", "初心者向け", "初学者", "プログラミング初心者"]
    tags = ["Python", "Django", "Apache", "Ubuntu", "Linux", "HTML", "CSS",
            "Bootstrap", "JavaScript", "HTTP", "AI", "GitHub", "Git",
            "機械学習", "深層学習"] + BIGGINER

    tag = tags[random.randint(0, len(tags)-1)]
    response = connect_qiita(PAGE, PAR_PAGE, tag.lower(), CREATED, STOCKS)
    post = get_post(tag, response)

    exceptions = {}
    for t in BIGGINER:
        exceptions[t] = "初心者向けの"

    msg = "Qiitaで"+ make_tagstr(tag, exceptions = exceptions) + "投稿を定期的に漁ってます！\n\n#プログラミング\n#プログラミング初心者\n#駆け出しエンジニアと繋がりたい\n\n" + post[1] + "\n" + post[0]
    print(msg)
    tweet(msg)

if __name__ == "__main__":
    main()