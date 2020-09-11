from bs4 import BeautifulSoup
import requests
import re


def obtain_content(url):
    page_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(page_response.content, "html.parser")
    print(soup)

def obtain_news_culturalfoundation(url):
    regex = re.compile("[^a-zA-Z0-9 -]")
    page_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(page_response.content, "html.parser")
    textContent = ""
    dict_news = {}
    dates = []
    for node in soup.findAll("a", {"class": "summary-title-link"}):
        title = regex.sub(' ',str(node.findAll(text=True)))
        title = title[1:len(title)]
        url = node['href']
        dict_news[title]={'href':"https://www.culturalfoundation.eu{}".format(url)}
    for title_date in soup.findAll("time", {"class": "summary-metadata-item summary-metadata-item--date"}):
        date = regex.sub(' ',str(title_date.findAll(text=True)))
        dates.append(date)
    index = 0
    for key in dict_news.keys():
        dict_news[key]["date"] = dates[index]
        index += 1
    return dict_news

def obtain_news_nordiskkulturkontakt(url):
    regex = re.compile("[^a-zA-Z0-9 -]")
    page_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(page_response.content, "html.parser")
    textContent = ""
    dict_news = {}
    dates = []
    for node in soup.findAll("a", {"class": "post-content"}):
        title = regex.sub(' ',str(node.findAll(text=True)))
        title = title[20:len(title)]
        title_list = title.split(" ")
        title_list.remove("n")
        title_list = [x for x in title_list if x != 'n']
        title_list = title_list[:len(title_list)-6]
        date_list = title_list[-3:]
        title_list = title_list[:len(title_list)-10]
        date = '/'.join(date_list)
        title = ' '.join(title_list)
        url = node['href']
        dict_news[title]={'href':url, 'date': date}
    return dict_news

obtain_news_nordiskkulturkontakt("https://www.nordiskkulturkontakt.org/en/news/")