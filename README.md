# YT_dislikes is a twitter bot that allows you to know the number of dislikes (and likes) of a YouTube video.
Now it is not possible to see the number of dislikes in YouTube. To discover it, tweet tagging @YT_dislikes and adding the url of the YouTube video and the bot will answer you with the stats.

These are the main tools used in this project:

  - Tweepy
  - YouTube Data API
  - MongoDB
  - Selenium
  - Heroku (now disabled)

And this is how the bot works:

  - Get the last 20 tweets tagging the bot
  - Compare their tweet ID to the ones stored in the Mongo database (which are the tweets already answered)
  - If those IDs are already in the database, do nothing
  - If one or some are not in the database, extract the ID of the YouTube video from its url, get the number of likes and dislikes with the YouTube API and generate
  a response to the tweet
  - Add these tweets ID to the database

UPDATE!
Now it is not possible to get the dislikes from the API (I´m sad), so this update includes a Chrome extension to unlock them on the YouTube website.
