from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob
import json

ACCESS_TOKEN = "2460921473-QkIBOaOI0AQjtbqovO88IA2T5ATOI0h1vUYKRts"
ACCESS_TOKEN_SECRET = "ZWNGkGLhb91rmVH1RENkgPVq9C6R4AZfKxcXSdMJJAllb"
CONSUMER_KEY = "CCDd0CvDC3g4a1kyopo48lCwG"
CONSUMER_SECRET = "Ajysc67bUC8cM3tp8Ox1IlthqE7irXRTTG5rxpirjabSKKmDeK"

class TwitterStreamer():
    """
    Class for streaming and processinf live tweets for a given list of hashtags
    """
    def stream_tweets(selfself, hashtag_list):
        listener = StdOutListener()
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        stream = Stream(auth, listener)

        stream.filter(track=hashtag_list)


class StdOutListener(StreamListener):

    def on_data(self, data):
        newData = json.loads(data)
        analysis = TextBlob(newData["text"])
        print(analysis.sentiment)
        print(newData["text"])
        return True

    def on_error(self, status):
        print(status)


def main():
    hashtag_list = ['Chelsea']
    fetched_tweets_filename = "tweets.json"
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(hashtag_list)

main()