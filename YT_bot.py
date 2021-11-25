from googleapiclient.discovery import build
import tweepy
import os
from dotenv import load_dotenv
from time import sleep  


load_dotenv()

#Twitter
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']                           #passwords to be used in Heroku
access_token  = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']

#YouTube
api_key = os.environ['api_key']


def dislikes():

    #Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)                #Tweepy authentication
    api = tweepy.API(auth, wait_on_rate_limit=True)

    #YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)                  #YouTube API authentication

    global set_id_tweets

    try:

        set_id_tweets_anterior = set_id_tweets.copy()                       #make a copy to be used later on to compare new list of mentions to the old one

    except:

        set_id_tweets_anterior = set()

    set_id_tweets = set() 
    tweets = api.mentions_timeline(count=10, tweet_mode='extended')          #List of last 10 tweets tagging me

    for tweet in tweets:

        set_id_tweets.add(tweet.id)

    lista_tweets = [tweet for tweet in tweets if tweet.id not in set_id_tweets_anterior]     #List of new tweets tagging me from checking if these tweets were in the old list

    if len(lista_tweets) == 0:

        return 

    for tweet in lista_tweets:

        try:                                                                                        #links are different if they come from a browser or from the YouTube app

            yt_from_web = tweet.entities['urls'][0]['expanded_url'].split('www.')[1][:7]

            if yt_from_web == 'youtube':

                url_id = tweet.entities['urls'][0]['expanded_url'].split('v=')[-1].split('&t=')[0]           #first we try to get the ID of the video as if it comes from a browser

        except:
            pass                                                                                    #we don´t include the other possibility on the except because it could
                                                                                                    #happen that the link provided is not from YouTube
        try:

            yt_from_cell = tweett.entities['urls'][0]['expanded_url'].split(r'://')[1][:8]

            if  yt_from_cell == 'youtu.be':

                url_id = tweet.entities['urls'][0]['expanded_url'].split('.be/')[-1]                         #then we try to get the ID as if the url comes from the app

        except:
            pass

        try:                

            request = youtube.videos().list(part = 'statistics', id = url_id)                       #on this part, we get the stats from the given YouTube video and generate
                                                                                                    #a response with the number of likes, dislikes and percentages
            response = request.execute()                                                            #if it is not a video from YouTube, it will go to the except

            dislikes = int(response['items'][0]['statistics']['dislikeCount'])
            likes = int(response['items'][0]['statistics']['likeCount'])
            total= likes+dislikes

            my_response = 'This video has:\n\n{} likes ({} %)\n{} dislikes ({} %)'.format(likes, round(likes/total*100, 1), dislikes, round(dislikes/total*100, 1))

            api.update_status(my_response, in_reply_to_status_id = tweet.id, auto_populate_reply_metadata = True)

        except:
            pass

    
    return 


while True:
    
    dislikes()
    
    sleep(60)
