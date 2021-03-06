import re
from requests_html import HTMLSession, HTML
from datetime import datetime
from ftfy import fix_text

session = HTMLSession()


def get_tweets(user, tweets=None, retweets=False, notext=False, adddot=True, maxpages=25):
    """Gets tweets for a given user, via the Twitter frontend API."""

    url = f'https://twitter.com/i/profiles/show/{user}/timeline/tweets?include_available_features=1&include_entities=1&include_new_items_bar=true'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': f'https://twitter.com/{user}',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8',
        'X-Twitter-Active-User': 'yes',
        'X-Requested-With': 'XMLHttpRequest'
    }

    def gen_tweets(tweets, retweets, notext, adddot, maxpages):
        r = session.get(url, headers=headers)
        pages = maxpages
        json = r.json()
        # if no number of tweets specified, all tweets from the json will be returned
        found = tweets or json['new_latent_count'] - 1

        while pages > 0 and found > 0:
            json = r.json()
            try:
                html = HTML(html=json['items_html'],
                            url='bunk', default_encoding='utf-8')
            except KeyError:
                raise ValueError(
                    f'Oops! Either "{user}" does not exist or is private.')

            comma = ","
            dot = "."
            tweets = []
            for tweet in html.find('.stream-item'):
                data = tweet.find('.tweet-text')
                if len(data) < 1:
                    continue
                raw = tweet.find('.tweet-text')[0].raw_html
                text = tweet.find('.tweet-text')[0].full_text
                text = re.sub('\Shttp', ' http', text, 1)
                text = re.sub('.@', ' @', text)
                remove = 'pic.twitter.com'
                removelen = len(remove) + 11
                index = text.find(remove)
                while index > -1:
                    text = text[0:index] + text[index + removelen:]
                    index = text.find('pic.twitter.com')
                text = text.replace(u'\xa0', u' ')
                text = re.sub('[ \t\f\v]+', ' ', text)
                # fixes common encoding problems in the tweet text body
                text = fix_text(text.strip())
                tweetId = tweet.find(
                    '.js-permalink')[0].attrs['data-conversation-id']
                originaluserId = tweet.find(
                    '.js-original-tweet')[0].attrs['data-screen-name']
                time = datetime.fromtimestamp(
                    int(tweet.find('._timestamp')[0].attrs['data-time-ms']) / 1000.0)
                time = time.strftime("%Y-%m-%d %H:%M:%S")
                interactions = [
                    x.text for x in tweet.find('.ProfileTweet-actionCount')]
                replies = interactions[0].split(" ")[0].replace(
                    comma, "").replace(dot, "") or "0"
                retweets = interactions[1].split(" ")[0].replace(
                    comma, "").replace(dot, "") or "0"
                likes = interactions[2].split(" ")[0].replace(
                    comma, "").replace(dot, "") or "0"
                hashtags = [
                    hashtag_node.full_text for hashtag_node in tweet.find('.twitter-hashtag')]
                urls = [url_node.attrs['data-expanded-url']
                        for url_node in tweet.find('a.twitter-timeline-link:not(.u-hidden)')]
                photos = [photo_node.attrs['data-image-url']
                          for photo_node in tweet.find('.AdaptiveMedia-photoContainer')]
                videos = []
                video_nodes = tweet.find(".PlayableMedia-player")
                for node in video_nodes:
                    try:
                        styles = node.attrs['style'].split()
                        for style in styles:
                            if style.startswith('background'):
                                tmp = style.split('/')[-1]
                                video_id = tmp[:tmp.index('.jpg')]
                                videos.append({'id': video_id})
                    except ValueError:
                        continue

                emoji = [emoji_node.attrs['title']
                         for emoji_node in tweet.find('.Emoji')]
                correcttweet = retweets == True or originaluserId.lower() == user.lower()
                tweetsize = len(text)
                accepttweet = notext == True or tweetsize > 0
                if correcttweet and accepttweet:
                    if adddot and tweetsize > 0:
                        if not (text[-1] == '!' or text[-1] == '?' or text[-1] == '.'):
                            text += '.'
                    text = text.replace(' .', '.')
                    tweets.append({'tweetId': tweetId, 'time': time, 'user': user, 'originaluser': originaluserId,
                                   'text': text, 'replies': replies, 'retweets': retweets, 'likes': likes,
                                   'entries': {
                                       'hashtags': hashtags, 'emoji': emoji,
                                       'urls': urls,
                                       'photos': photos, 'videos': videos
                                   }
                                   })

            for tweet in tweets:
                if tweet and found > 0:
                    found += -1
                    yield tweet

            if json['has_more_items'] == True:
                last_tweet = html.find('.stream-item')[-1].attrs['data-item-id']
                r = session.get(url, params={'max_position': last_tweet}, headers=headers)
                pages += -1
            else:
                # reset the count regardless since there are no more tweets left
                found = 0


    yield from gen_tweets(tweets, retweets, notext, adddot, maxpages)
