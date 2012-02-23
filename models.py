#-*- coding: utf-8 -*-

from django.db import models



class TwitterUser(models.Model):

    twitter_user_id_str = models.CharField(db_index=True, max_length=32)
    name = models.CharField(max_length=128, default="")

    is_active = models.BooleanField(default=True)
    last_user_reply = models.IntegerField(null=True, blank=True)
    last_scanned_tweet = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('name',)



class TwitterHistory(models.Model):

    twitter_message_id_str = models.CharField(db_index=True, max_length=32)

    user = models.ForeignKey(TwitterUser)
    text = models.CharField(max_length=140, default="")
    in_reply_to = models.IntegerField(null=True, blank=True)
    is_incoming = models.BooleanField()

    class Meta:
        ordering = ("user", "twitter_message_id_str")
        get_latest_by = ("twitter_message_id_str", )




