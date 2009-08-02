from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect

import oauthtwitter, oauth

from dtwitter.models import TwitterUser
from dtwitter.signals import user_logged_out, user_logged_in
from dtwitter.signals import new_twitter_user

# connect # {{{ 
def connect(request):
    twitter = oauthtwitter.OAuthApi(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET
    )
    request_token = twitter.getRequestToken()
    request.session["request_token"] = request_token.to_string()
    twitter_url = "https://twitter.com/oauth/authorize?oauth_token=%s" % (
        request_token.key
    )
    return render_to_response(
        "dtwitter/redirect.html", { 'twitter_url': twitter_url },
        context_instance=RequestContext(request)
    )
# }}} 

# callback # {{{ 
def callback(request):
    request_token = oauth.OAuthToken.from_string(
        request.session["request_token"] 
    )
    twitter = oauthtwitter.OAuthApi(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET,
        request_token
    )
    access_token = twitter.getAccessToken()

    twitter = oauthtwitter.OAuthApi(
        settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET,
        access_token
    )

    user_info = twitter.GetUserInfo()
    assert user_info.screen_name # make sure auth worked

    twitter_user, created = TwitterUser.objects.get_or_create_from_info(
        user_info, access_token.to_string()
    )

    if created:
        new_twitter_user.send(sender=request, twitter_user=twitter_user)

    del request.session["request_token"]

    request.session["twitter_user_id"] = twitter_user.pk

    user_logged_in.send(sender=request, twitter_user=twitter_user)

    return render_to_response(
        "dtwitter/configuration-done.html", { 'twitter_user': twitter_user },
        context_instance=RequestContext(request)
    )
# }}} 

# logout # {{{ 
def logout(request, template='', next=None):
    if hasattr(request, "twitter_user"):
        twitter_user = request.twitter_user
        del request.twitter_user
    if "twitter_user_id" in request.session:
        del request.session["twitter_user_id"]

    # send signal
    user_logged_out.send(sender=request, twitter_user=twitter_user)

    if next: return HttpResponseRedirect("next")
    if "redirect_to" in request.REQUEST:
        return HttpResponseRedirect(request.REQUEST["redirect_to"])
    if "come_back" in request.REQUEST:
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    return render_to_response(
        [template, "dtwitter/logout.html"], 
        context_instance=RequestContext(request)
    )
# }}} 


