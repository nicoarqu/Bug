from bs4 import BeautifulSoup
import requests
import re
import datetime


def obtain_content(url):
    page_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(page_response.content, "html.parser")
    print(soup)

def obtain_news_culturalfoundation():
    url = "https://www.culturalfoundation.eu/news"
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

def obtain_news_nordiskkulturkontakt():
    url = "https://www.nordiskkulturkontakt.org/en/news/"
    regex = re.compile("[^a-zA-Z0-9 -]")
    try:
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
    except:
        return{}

def obtain_news_eeagrants():
    regex = re.compile("[^a-zA-Z0-9 -]")
    index = 1
    dict_news = {}
    while index <= 3:
        page_response = requests.get("https://eeagrants.org/currently-available-funding?page={}".format(index), timeout=5)
        soup = BeautifulSoup(page_response.content, "html.parser")
        textContent = ""
        dates = []
        for node in soup.findAll("a", {"class": "field-group-link"}):
            title = regex.sub(' ',str(node.findAll(text=True)))
            title_list = title.split(" ")
            title_list = [x for x in title_list if x != 'n']
            title = ' '.join(title_list)
            title = title.split("            ")[0][8:]
            url = "https://eeagrants.org{}".format(node['href'])
            dict_news[title] = {'href': url }
        index += 1

def obtain_grants_creativeeurope():
    url = "https://ec.europa.eu/programmes/creative-europe/calls_en"
    regex = re.compile("[^a-zA-Z0-9 -]")
    try:
        page_response = requests.get(url, timeout=5)
        soup = BeautifulSoup(page_response.content, "html.parser")
        textContent = ""
        dict_news = {}
        dates = []
        for node in soup.findAll("div", {"class": "update-highlight--list--content"}):
            title = regex.sub(' ',str(node.findAll(text=True)))
            title_list = title.split(" ")
            title_list = [x for x in title_list if x != 'n']
            title = ' '.join(title_list)
            title_list = title.split("        ")
            title = title_list[0][]
        return dict_news
    except:
        return{}

def get_scraped_news():
    news_list = []
    news_list.append(obtain_news_eeagrants())
    news_list.append(obtain_news_nordiskkulturkontakt())
    news_list.append(obtain_news_culturalfoundation())
    return news_list