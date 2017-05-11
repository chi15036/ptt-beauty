import requests
from bs4 import BeautifulSoup
import time
import urllib.request
import re
import os

def get_web_page(url):
    resp = requests.get(
        url=url
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text

def get_articles(dom, date, articles):
    has_match_page = False 
    page_link = ""
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find_all('a', 'btn wide')
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').string.replace(" ", "") == date:
            push_count = 0
            if d.find('div', 'nrec').string:
                try:
                    if d.find('div', 'nrec').string == "爆":
                        push_count = 30
                    else:
                        push_count = int(d.find('div', 'nrec').string) 
                except ValueError:
                    pass
			
            if d.find('a'): 
                href = d.find('a')['href']
                title = d.find('a').string
                articles.append({
                    'title': title,
                    'href': href,
                    'push_count': push_count
                })
            has_match_page = True
        if has_match_page:
            page_link = links[1]['href']
    return articles, page_link   

def parse(dom):
    soup = BeautifulSoup(dom, 'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
    return img_urls

def save(img_urls, push_count):
    if img_urls:
        try:
            if push_count == 0:
                dname = "0"
            elif push_count > 0 and push_count < 5:
                dname = "0-5"
            elif push_count >= 5 and push_count < 10:
                dname = "5-10"
            elif push_count >= 10 and push_count < 15:
                dname = "10-15"
            elif push_count >= 15 and push_count < 20:
                dname = "15-20"
            elif push_count >= 20 and push_count < 25:
                dname = "20-25"
            elif push_count >= 25 and push_count < 30:
                dname = "25-30"
            else:
                dname = "30"
                dname = "/home/ubuntu/ptt-beauty/" + dname

            for img_url in img_urls:
                if img_url.split('//')[1].startswith('m.'):                                                           img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)

articles = []
page_link = "/bbs/Beauty/index.html"
while page_link != "":
    page = get_web_page('https://www.ptt.cc' + page_link)
    date = time.strftime("%m/%d").lstrip('0')
    articles, page_link = get_articles(page, date, articles)
for article in articles:
    print(article)
    page = get_web_page('https://www.ptt.cc' + article['href'])
    if page:
        img_urls = parse(page)
        save(img_urls, article['push_count'])
