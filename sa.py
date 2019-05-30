import praw
import requests
from textblob import TextBlob
from datetime import datetime, time
import math
import ujson as json

PUSHSHIFT_REDDIT_URL = "http://api.pushshift.io/reddit"

reddit = praw.Reddit(
    client_id='KnNdqfjLry_nBg',
    client_secret='FKJUYm41LesdrdohPWftbkT5-eg',
    user_agent='subSentiment'
)

with open('subreddits.txt', 'r') as f:
    n = 1

    for line in f:
        subreddit = reddit.subreddit(line.strip())

        # epoch of earliest and latest time of the current date
        day_start = int(datetime.combine(datetime.today(), time.min).timestamp())
        day_end = int(datetime.combine(datetime.today(), time.max).timestamp())

        url = PUSHSHIFT_REDDIT_URL + '/submission/search/?'
        url += 'after=' + str(day_start)
        url += '&before=' + str(day_end)
        url += '&sort_type=score&sort=desc'
        url += '&subreddit=' + str(subreddit.display_name)

        r = requests.get(url)

        if r.status_code == 200:
            response = json.loads(r.text)
            data = response['data']
            #sorted_data_by__id = sorted(data, key=lambda x: int(x['id'],36))
            #print(json.dumps(data, indent=4, sort_keys=True))

            sub_sentiment = 0
            num_comments = 0

            for submission in data:
                if submission['stickied'] == False:
                    #print('#')
                    post = reddit.submission(id=submission['id'])  # if you have the ID
                    post.comments.replace_more(limit=0)

                    # Iterate over all of the top-level comments on the post:
                    for comment in post.comments.list():
                        #print(comment.body)
                        blob = TextBlob(comment.body)

                        comment_sentiment = blob.sentiment.polarity
                        sub_sentiment += comment_sentiment

                        num_comments += 1

            nth = str(n) + '. '
            n += 1

            print(nth + 'r/' + str(subreddit.display_name) + ": ")

            try:
                ratio = sub_sentiment/num_comments
                polarity = ''

                if ratio > 0:
                    polarity = 'positive'
                elif ratio < 0:
                    polarity = 'negative'
                else:
                    polarity = 'neutral'

                print('Ratio: %.4f' % ratio)
                print('Polarity: ' + polarity + '\n')

            except:
                print('No commment sentiment.' + '\n')
                ZeroDivisionError
            