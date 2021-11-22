from googleapiclient.discovery import build
import tweepy
from dotenv import load_dotenv
import os
from time import sleep  

load_dotenv()

#Twitter
consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
access_token  = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']

#YouTube
api_key = os.environ['api_key']

def dislikes():
    
    #Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    #YouTube
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    global set_id_tuits
    
    try:
        
        set_id_tuits_anterior = set_id_tuits.copy()
        
    except:
        
        set_id_tuits_anterior = set()
        
    set_id_tuits = set()
    
    tuits = api.mentions_timeline(count=10)          #List of tweets tagging me
    
    for tuit in tuits:
        set_id_tuits.add(tuit.id)

    lista_tuits = [tuit for tuit in tuits if tuit.id not in set_id_tuits_anterior]     #List of new tweets tagging me
    
    if len(lista_tuits) == 0:
        
        return
    
    for tuit in lista_tuits:
        
        try:
        
            yt_from_web = tuit.entities['urls'][0]['expanded_url'].split('www.')[1][:7]
            
            if yt_from_web == 'youtube':

                url_id = tuit.entities['urls'][0]['expanded_url'].split('v=')[-1].split('&t=')[0]
            
        except:
            pass
        
        try:
            
            yt_from_cell = tuit.entities['urls'][0]['expanded_url'].split(r'://')[1][:8]
            
            if  yt_from_cell == 'youtu.be':
                
                url_id = tuit.entities['urls'][0]['expanded_url'].split('.be/')[-1]     
            
        except:
            pass

        try:                

            request = youtube.videos().list(part = 'statistics', id = url_id)

            response = request.execute()

            dislikes = int(response['items'][0]['statistics']['dislikeCount'])
            likes = int(response['items'][0]['statistics']['likeCount'])
            total= likes+dislikes

            comentario = 'This video has:\n\n{} likes ({} %)\n{} dislikes ({} %)'.format(likes, round(likes/total*100, 1), dislikes, round(dislikes/total*100, 1))

            api.update_status(comentario, in_reply_to_status_id = tuit.id, auto_populate_reply_metadata = True)

            return

        except:

            return

    else:
        return
    

while True:
    
    dislikes()
    sleep(60)
