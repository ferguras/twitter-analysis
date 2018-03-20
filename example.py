from twitter_analysis import get_tweets
import simplejson

thefile = open('tweets.txt', 'w')

tweets = list(get_tweets('Urbandecay', tweets=100))

for tweet in tweets:
	print(tweet['text'])
	simplejson.dump(tweet,thefile)
	thefile.write('\n')

thefile.close()
