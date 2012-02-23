#-*- coding: utf-8 -*-


import os, sys
import random
import re
import time
from multiprocessing.pool import ThreadPool


import tweepy
from tweepy.error import TweepError

sys.path.append("..")
os.environ["DJANGO_SETTINGS_MODULE"] = "slono_job.settings"

from django.db import transaction

import logging
logger = logging.getLogger("slono_daemon")


from slono_job.models import TwitterUser, TwitterHistory
from slono_job.settings import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET, TWITTER_OWN_NAME, TWITTER_TRIGGER_KEYWORDS, TWITTER_INITIAL_QUOTES, TWITTER_TEMPLATE_REPLY



def cut_to_twitter_status_size(reply_text):
    #TODO: сделать более толковую обрезку до 140 символов
    if len(reply_text) > 140:
        reply_text = reply_text[:68] + u" .. " + reply_text[-68:]
    return reply_text

def make_unique_suffix():
    return "%04X" % (int(time.time()*10) % 0xFFFF)


def do_stream_filtered(thread_pool, api, status):
    try:
        if status.user.screen_name == TWITTER_OWN_NAME:
            # свои сообщения можно смело игнорить.
            return

        # если пользователь есть в базе
        if TwitterUser.objects.filter(twitter_user_id_str=status.user.id_str).count():
            # отбой тревоги (все его слоны будут обрабатываться через follow + мой userstream)
            logger.info("user already in db: %s" % status.user.name)
            return

        logger.info("new user: %s" % status.user.screen_name)

        # добавить в пул отправку ему начального сообщения "цитата про слонов".
        thread_pool.apply_async(do_initial_quoute_and_follow, (api, status))

    except TweepError, e:
        logger.exception(u"something wrong with twitter api: %s" % unicode(e))

    except Exception, e:
        logger.exception("error in do_stream_filtered")



def do_initial_quoute_and_follow(api, original_status):
    transaction.enter_transaction_management()
    transaction.managed(True)

    try:
        logger.info("do_initial_quoute for %s" % original_status.user.screen_name)

        # создать пользователя
        new_user = TwitterUser.objects.create(twitter_user_id_str=original_status.user.id_str, name=original_status.user.screen_name)

        TwitterHistory.objects.create(user=new_user, twitter_message_id_str=original_status.id_str, text=original_status.text, is_incoming=True)

        quote = random.choice(TWITTER_INITIAL_QUOTES)
        reply_text = u"@%(user)s %(text)s %(uniq)s" % {"user":original_status.user.screen_name, "text": quote, "uniq":make_unique_suffix()}

        reply_text = cut_to_twitter_status_size(reply_text)

        new_status = api.update_status(status=reply_text, in_reply_to_status_id=original_status.id)
        logger.info("initial quote sent")

        TwitterHistory.objects.create(user=new_user, twitter_message_id_str=new_status.id_str, text=reply_text, is_incoming=False, in_reply_to=str(original_status.id))

        api.create_friendship(user_id=original_status.user.id)
        logger.info("user followed")

        transaction.commit()

    except TweepError, e:
        transaction.rollback()
        logger.exception(u"something wrong with twitter api: %s" % unicode(e))

    except Exception:
        transaction.rollback()
        logger.exception("error in do_initial_quoute_and_follow")


    transaction.leave_transaction_management()


def do_stream_my(thread_pool, api, status):
    try:
        if status.user.screen_name == TWITTER_OWN_NAME:
            # свои сообщения можно смело игнорить.
            return

        # вытащить из статуса юзера, in_reply_to
        try:
            user = TwitterUser.objects.get(twitter_user_id_str=str(status.user.id_str))
        except TwitterUser.DoesNotExist:
            logger.info("unknown user in my stream: %s, ignoring..." % status.user.screen_name)
            return

        if not user.is_active:
            logging.info("inactive user: %s. ignoring..." % status.user.screen_name)
            return

        # вытащить из базы юзера и последнее сообщение к нему - по идее юзер должен отвечать только на него
        latest_sent_status_id_str = user.twitterhistory_set.filter(is_incoming=False).latest().twitter_message_id_str
        if status.in_reply_to_status_id_str == latest_sent_status_id_str:
            logger.info("user replied to our message")
            thread_pool.apply_async(do_send_tempate_reply, (api, user, status))
        else:
            logging.info("ignoring user status update - this is not reply to last my status")

    except Exception:
        logger.exception("error in do_stream_my")



def do_send_tempate_reply(api, user, original_status):
    transaction.enter_transaction_management()
    transaction.managed(True)
    try:
        # добавить сообщение в хистори
        TwitterHistory.objects.create(user=user, twitter_message_id_str=original_status.id_str, text=original_status.text,
            is_incoming=True, in_reply_to=original_status.in_reply_to_status_id_str)

        # ответить "все говорят "ХХХ", а ты купи слона!"

        # откусить @юзернейм в начале сообщения
        original_text = re.sub("^(@\w+)\s", "", original_status.text, flags=re.UNICODE)
        reply_text = TWITTER_TEMPLATE_REPLY % {"original": original_text}
        reply_status = u"@%(user)s %(text)s %(uniq)s" % {
            "user": original_status.user.screen_name, "text": reply_text, "uniq":make_unique_suffix()}

        reply_status = cut_to_twitter_status_size(reply_status)

        new_status = api.update_status(status=reply_status, in_reply_to_status_id=original_status.id)
        logger.info("template reply sent")

        TwitterHistory.objects.create(user=user, twitter_message_id_str=new_status.id_str, text=reply_status,
            is_incoming=False, in_reply_to=original_status.id_str)


        transaction.commit()

    except TweepError, e:
        transaction.rollback()
        logger.exception(u"something wrong with twitter api: %s" % unicode(e))


    except Exception:
        transaction.rollback()
        logger.exception("error in do_send_tempate_reply")

    transaction.leave_transaction_management()



class SlonoListener(tweepy.StreamListener):
    def __init__(self, api, thread_pool):
        tweepy.StreamListener.__init__(self, api)
        self.thread_pool = thread_pool


    def on_status(self, status):
        try:
            self.thread_pool.apply_async(do_stream_filtered, (self.thread_pool, self.api, status))
            logger.info("new listener stream status: %s" % status.text)
        except Exception, e:
            logger.exception('SlonoListener: on_status')

    def on_error(self, status_code):
        logger.error('SlonoListener: An error has occured! Status code = %s' % status_code)
        return True  # keep stream alive

    def on_timeout(self):
        logger.info('SlonoListener: on_timeout')



class UserStreamListener(tweepy.StreamListener):
    def __init__(self, api, thread_pool):
        tweepy.StreamListener.__init__(self, api)
        self.thread_pool = thread_pool


    def on_status(self, status):
        try:
            self.thread_pool.apply_async(do_stream_my, (self.thread_pool, self.api, status))
            logger.info("new user stream status: %s" % status.text)
        except Exception, e:
            logger.exception('UserStreamListener: on_status')



    def on_error(self, status_code):
        logger.error('UserStreamListener: An error has occured! Status code = %s' % status_code)
        return True  # keep stream alive

    def on_timeout(self):
        logger.info('UserStreamListener: on_timeout')




if __name__ == "__main__":
    print TwitterUser.objects.count()
    #TwitterUser.objects.all().delete()

    logger.setLevel(logging.DEBUG+1)

    logging.root.setLevel(logging.DEBUG+1)
    logging.basicConfig()#filename=os.path.join(os.path.split(__file__)[0],"daemon.log"))

    logger.info("slono_daemon stared")

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_KEY, TWITTER_ACCESS_SECRET)
    api=tweepy.API(auth)

    logger.info("authentication successfull")


    thread_pool = ThreadPool(processes=2)

    slono_listener = SlonoListener(api, thread_pool)
    slono_stream = tweepy.Stream(auth, slono_listener, timeout=None)
    slono_stream.filter(track=TWITTER_TRIGGER_KEYWORDS, async=True)
    logger.info("filter stream started")

    my_listener = UserStreamListener(api, thread_pool)
    my_stream = tweepy.Stream(auth, my_listener, timeout=None)
    my_stream.userstream(async=True)
    logger.info("user stream started")

    #TODO сделать unfollow давно не отвечавших пользователей.

    try:
        while True:
            #print "tick"
            time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("shutting down...")
        slono_stream.disconnect()
        my_stream.disconnect()
        thread_pool.close()
        thread_pool.join()
        logger.info("shutdown complete!")

