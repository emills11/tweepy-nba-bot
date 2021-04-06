import tweepy
import logging
import os
from decouple import config

logger = logging.getLogger()

def create_api():
    # Keys / tokens are environment variables
    consumer_key = config("CONSUMER_KEY")
    consumer_secret = config("CONSUMER_SECRET")
    access_token = config("ACCESS_TOKEN")
    access_token_secret = config("ACCESS_TOKEN_SECRET")

    # Set auth keys and creates API
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        # Credentials could not be verified, keys are probably wrong / outdated
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api
