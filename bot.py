import random
import sys
import twython

from generate import generate, get_subj_from_wikilink

consumer_key, consumer_secret, access_token, token_secret = sys.argv[1:]
twitter = twython.Twython(consumer_key, consumer_secret, access_token,
        token_secret)

pool = [s.strip() for s in open("pool.txt").readlines()]
if random.randrange(8) > 0:
    subj = get_subj_from_wikilink(
            'http://en.wikipedia.org' + random.choice(pool))
    status = generate(subj)
else:
    status = generate()
twitter.update_status(status=status)
