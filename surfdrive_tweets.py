#!/usr/bin/env python

import sys
import oauth2 as oauth
import urllib

ckey='consumer key'
csecret='consumer secret'
akey='access token key'
asecret='access token secret'

def post_twitter(status):
    try:
        consumer = oauth.Consumer(key=ckey, secret=csecret)
        token = oauth.Token(key=akey, secret=asecret)
        client = oauth.Client(consumer, token)
        resp, content = client.request(
            'https://api.twitter.com/1.1/statuses/update.json',
            method='POST',
            body = urllib.urlencode({"status": status,
                                     "wrap_links": True}),
            )
    except oauth.Error as err:
        print("Twitter Error:"+err)
    return resp, content

def main():

    tweet=raw_input('Tweet: ')

    if len(tweet)>140:
        print "The length of the tweet is: "+str(len(tweet))
        print "Exceeding maximum lengt of 140 characters."
        sys.exit(1)

    print "The tweet has: "+str(len(tweet))+" characters."
    print tweet

    answer=''
    while answer=='':
        input=raw_input('Do you want to publish (y/n): ').lower()
        if len(input)==1:
            if input=='y' or input=='n':
                answer=input

    if answer=='y':
        post_twitter(tweet)
    else:
        print "Tweet is not published"
        

if __name__=='__main__':
    main()
