#-*- coding: utf-8 -*-

from django.db.models.aggregates import Count

from django.shortcuts import render_to_response
from django.template.context import RequestContext

from .models import TwitterUser, TwitterHistory


def render_to(template_path):
    def decorator(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(template_path, output,
                context_instance=RequestContext(request))
        return wrapper
    return decorator


@render_to("index.html")
def index(request):
    users = TwitterUser.objects.all().annotate(history_len=Count('twitterhistory')).order_by("history_len").reverse()
    return vars()



@render_to("user_history.html")
def user_history(request, user_id=None):
    history = TwitterHistory.objects.filter(user__pk=user_id)
    return vars()


