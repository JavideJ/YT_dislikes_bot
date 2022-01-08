import numpy as np
from googleapiclient.discovery import build
import tweepy
import os
from time import sleep
import pymongo
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager


#Twitter
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']                           #passwords to be used in Heroku
access_token  = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']

#YouTube
api_key = os.environ['api_key']

#MongoDB
mongo_client = os.environ['mongo_client']


def dislikes():

    #Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)                #Tweepy authentication
    api = tweepy.API(auth, wait_on_rate_limit=True)

    #YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)                  #YouTube API authentication
    
    #MongoDB
    db = pymongo.MongoClient(mongo_client)
    dbtwitter_bot = db.twitter_bot.mentions_list
    answered_tweets_id = [k['id_'] for k in dbtwitter_bot.find()]             #list of tweets already answered
    

    tweets = api.mentions_timeline(count=20, tweet_mode='extended')          #List of last 20 tweets tagging me


    tweets_list = [tweet for tweet in tweets if tweet.id not in answered_tweets_id]     #List of new tweets tagging me from checking if these tweets were in the old list

    if len(tweets_list) == 0:

        return 

    
    
    for tweet in tweets_list:

        link_check = 0
    
        try:                                                                                        #links are different if they come from a browser or from the YouTube app
            yt_from_web = tweet.entities['urls'][0]['expanded_url'].split('www.')[1][:7]            #We need to do this to get the video ID for later on

            if yt_from_web == 'youtube':
                url_id = tweet.entities['urls'][0]['expanded_url'].split('v=')[-1].split('&t=')[0]

        except:
            link_check += 1


        try:
            yt_from_cell = tweett.entities['urls'][0]['expanded_url'].split(r'://')[1][:8]

            if yt_from_cell == 'youtu.be':
                url_id = tweet.entities['urls'][0]['expanded_url'].split('.be/')[-1]

        except:
            link_check += 1


        if link_check == 2:                                                           #If link_check == 2 means that the url is not a YouTube video
            mongo_tweet = {'id_': tweet.id, 'date': tweet.created_at}
            result = dbtwitter_bot.insert_one(mongo_tweet) 
            
            return



        try:                

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_extension(os.environ['return_dislikes_path'])                       #Here we add the dislikes YouTube extension from https://github.com/Anarios/return-youtube-dislike
                                                                                                   #We didn´t need it before but now is impossible to retrieve the number of dislikes from the API
                
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

            driver.get(tweet.entities['urls'][0]['expanded_url'])                                  #with Selenium, open the YouTube link in Chrome

            sleep(7)

            driver.find_element(By.XPATH, '/html/body/ytd-app/ytd-consent-bump-v2-lightbox/tp-yt-paper-dialog/div[4]/div[2]/div[5]/div[2]/ytd-button-renderer[2]/a/tp-yt-paper-button').click()

            sleep(3)

            driver.get_screenshot_as_file("screenshot.png")                        #Do a screenhot of the video

            sleep(1)

            driver.quit()

            img = Image.open('screenshot.png')                         #Get the image, crop it and save it
            img = np.array(img)
            crop_img = img[670:730, 370:]                        
            crop_img = Image.fromarray(crop_img)

            crop_img.save('cropped_screenshot.png')


            request = youtube.videos().list(part = ['snippet'], id = url_id)            #YouTube Data API to get the title of the video
            
            response = request.execute()
            title = response['items'][0]['snippet']['title']

            api.update_status_with_media(status = title , filename = "cropped_screenshot.png", in_reply_to_status_id = tweet.id)            #Answer the tweet with the title of the video and the
                                                                                                                                        #screenshot with the number of dislikes
                                
        except:
            pass

        mongo_tweet = {'id_': tweet.id, 'date': tweet.created_at}
        result = dbtwitter_bot.insert_one(mongo_tweet)                              #Add the ID of the tweet to the MongoDB so we don´t answer it again


    return

        

while True:
    
    dislikes()
    
    sleep(60)
