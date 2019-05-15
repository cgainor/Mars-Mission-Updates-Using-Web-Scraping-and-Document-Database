# Dependencies
import pymongo
import requests
import pandas as pd
import time
from splinter import Browser
from bs4 import BeautifulSoup as bs

# Set up DataBase
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

# Scrape Data
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}

def scrape():

    collection.drop()

    browser = Browser('chrome', **executable_path, headless=False)
    
    # NASA Mars News
    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html, 'lxml')
    news_title = news_soup.find('div', class_="content_title").text
    news_p = news_soup.find('div', class_="rollover_description_inner").text


	# JPL Mars Space Images - Featured Image
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    time.sleep(2)
    browser.click_link_by_partial_text("FULL IMAGE")
    time.sleep(2)
    browser.click_link_by_partial_text("more info")
    time.sleep(2)
    image_html = browser.html
    image_soup = bs(image_html, 'lxml')
    buttons = image_soup.find_all('div', class_='download_tiff')
    for button in buttons:
        if ('JPG' in button.text):
            featured_image_url = 'https:' + button.a['href']


	# Mars Weather
    twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(twitter_url)
    twitter_html = browser.html
    twitter_soup = bs(twitter_html, 'lxml')
    tweets = twitter_soup.find_all('p', class_='tweet-text')
    for tweet in tweets:
        if tweet.text.startswith('InSight'):
            tweet_image_text_length = len(tweet.find('a', class_="twitter-timeline-link").text)
            mars_weather = tweet.text[:-tweet_image_text_length]
            break
        else:
            continue


	# Mars Facts
    facts_url = 'https://space-facts.com/mars/'
    facts_table = pd.read_html(facts_url)
    mars_table = facts_table[0]
    mars_table_html = mars_table.to_html(header=False, index=False)


	# Mars Hemispheres
    hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemis_url)
    hemis_html = browser.html
    hemis_soup = bs(hemis_html, 'lxml')
    hemisphere_image_urls = []
    hemispheres = hemis_soup.find_all('div', class_="item")
    for hemis in hemispheres:
        hemis_info = {}
        hemis_title = hemis.div.a.h3.text
        hemis_info['title'] = hemis_title
        browser.click_link_by_partial_text(hemis_title)
        time.sleep(1)
        hemis_img_html = browser.html
        hemis_img_soup = bs(hemis_img_html, 'lxml')
        hemis_img = hemis_img_soup.find('div', class_='downloads').ul.li.a['href']
        hemis_info['img_url'] = hemis_img
        hemisphere_image_urls.append(hemis_info)
        browser.back()
        time.sleep(1)

    browser.quit()

    # Insert Data
    mars_data ={
        'news_title' : news_title,
        'news_summary': news_p,
        'featured_image': featured_image_url,
        'weather': mars_weather,
        'fact_table': mars_table_html,
        'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'image_url': image_url,
        'weather_url': twitter_url,
        'facts_url': facts_url,
        'hemisphere_url': hemis_url,
        }

    collection.insert(mars_data)