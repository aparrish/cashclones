import sys
import twython

import generate

consumer_key, consumer_secret, access_token, token_secret = sys.argv[1:]
twitter = twython.Twython(consumer_key, consumer_secret, access_token,
        token_secret)
twitter.update_status(status=generate.generate())

