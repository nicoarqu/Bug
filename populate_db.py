from flask_app import db
from config import *
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from models import News, Grants
import load_global
from webscraping_scripts import get_scraped_data
import json
import re

sched = BlockingScheduler()


"""----------------------------------------DATA CRAWL------------------------------------------------"""

def get_start_end_dates(days):
    tod = datetime.now()
    d = timedelta(days = days)
    a = tod - d
    date_start = a.strftime("%d %b, %Y")
    date_end =  tod.strftime("%d %b, %Y")
    return date_start, date_end

def filter_grants(news_list):
    grants_list = []
    for news_dict in news_list:
        if news_dict == None:
            continue
        if key_word_exists(news_dict):
            grants_list.append(news_dict)
    return grants_list

def key_word_exists(news_dict):
    key_words = []
    with open("data/filtering_words.json", "r") as key_words_file:
        file_dict = json.load(key_words_file)
        key_words = file_dict["palabras"]
        non_key_words = file_dict["palabras no queridas"]
    text = news_dict["summary"] + " " + news_dict["titulo"] 
    regex = re.compile('[^a-zA-Z]')
    text = regex.sub(' ', text)
    text_words = text.lower().split(" ")
    for non_key_word in non_key_words:
        if non_key_word in text_words:
            return False
    for key_word in key_words:
        if key_word in text_words:
            return True
    return False

def get_news_info():
    News = News.query.all()
    return News

def clean_events(events_list):
    title_list = []
    clean_events_list = []
    if events_list:
        for event in events_list:
            title = event["titulo"]
            if title in title_list:
                continue
            else:
                event["summary"] = cleanhtml(event["summary"])
                clean_events_list.append(event)
                title_list.append(title)
    return clean_events_list

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def organize_dates(new_news_list):
    ordered_list_dict = {}
    for n in range(50):
        ordered_list_dict["{}".format(2018+n)] = {"Dec": [], "Nov": [], "Oct": [], "Sep": [], "Aug": [], "Jul": [], "Jun": [], "May": [], "Apr": [], "Mar": [], "Feb": [], "Jan": []}
    for news_dict in new_news_list:
        date_elements = news_dict["pubDate"].split(" ")
        day = date_elements[1]
        month = date_elements[2]
        year = date_elements[3]
        if year in ordered_list_dict.keys():
            ordered_list_dict[year][month].append(news_dict)
    for year in ordered_list_dict.keys():
        year_dict = ordered_list_dict[year]
        for month in year_dict.keys():
            if year_dict[month]:
                year_dict[month] = sorted(year_dict[month], key = lambda i: i['pubDate'].split(" ")[1], reverse=True)
    new_ordered_news_list = []
    for year_key in ordered_list_dict.keys():
        for month_key in ordered_list_dict[year_key].keys():
            for news_dict in ordered_list_dict[year_key][month_key]:
                new_ordered_news_list.append(news_dict)
    return new_ordered_news_list

def add_grants(grants_list):
    grants_list = filter_grants(grants_list)
    grants_list.sort(key=lambda item:item['pubDate'], reverse=True)
    grants_list = organize_dates(grants_list)
    grants_list = clean_events(grants_list)
    for grant_dict in grants_list:
        if grant_dict == None:
            continue
        grant_exists = Grants.query.filter_by(link=grant_dict['link']).first()
        if grant_exists:
            continue
        new_grant = Grants(title=grant_dict['titulo'], description=grant_dict['summary'], link=grant_dict['link'], datetime=grant_dict['pubDate'])
        db.session.add(new_grant)
        db.session.commit()
    scraped_grant_list = get_scraped_data()
    for n_dict in scraped_grant_list:
        if n_dict != None:
            for title, data_dict in n_dict.items():
                grant_exists = Grants.query.filter_by(link=data_dict['href']).first()
                db.session.commit()
                if grant_exists:
                    continue
                date = "  {} {} {}".format(datetime.now().day, datetime.now().strftime("%b"), datetime.now().year)
                new_grant = Grants(title=title, description='', link=data_dict['href'], datetime=date)
                db.session.add(new_grant)
                db.session.commit()

def add_news(news_list):
    news_list.sort(key=lambda item:item['pubDate'], reverse=True)
    news_list = organize_dates(news_list)
    news_list = clean_events(news_list)
    for news_dict in news_list:
        if news_dict == None:
            continue
        news_exists = News.query.filter_by(link=news_dict['link']).first()
        db.session.commit()
        if news_exists:
            continue
        new_news = News(title=news_dict['titulo'], description=news_dict['summary'], link=news_dict['link'], datetime=news_dict['pubDate'])
        db.session.add(new_news)
        db.session.commit()
    scraped_news_list = get_scraped_data()
    for n_dict in scraped_news_list:
        if n_dict != None:
            for title, data_dict in n_dict.items():
                news_exists = News.query.filter_by(link=data_dict['href']).first()
                db.session.commit()
                if news_exists:
                    continue
                date = "  {} {} {}".format(datetime.now().day, datetime.now().strftime("%b"), datetime.now().year)
                new_news = News(title=title, description='', link=data_dict['href'], datetime=date)
                db.session.add(new_news)
                db.session.commit()

@sched.scheduled_job('interval', minutes=5)
def crawl_new_data():
    rss_grants_data_dict_list, rss_news_data_dict_list = load_global.load_all()
    add_grants(rss_news_data_dict_list)
    add_news(rss_news_data_dict_list)

if __name__ == "__main__":
    crawl_new_data()
    sched.start()
