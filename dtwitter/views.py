from importd import d
from django.conf import settings
from django.core.urlresolvers import get_mod_func

from twython import Twython

@d("/dtwitter/")
def idx(request):
    return d.HttpResponse("<a href='/dtwitter/connect/'>start</a>")

@d("/dtwitter/connect/")
def connect(request):
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET)
    auth = twitter.get_authentication_tokens(
        callback_url="http://%s/dtwitter/callback" % settings.DOMAIN
    )
    request.session["OAUTH_TOKEN"] = auth['oauth_token']
    request.session["OAUTH_TOKEN_SECRET"] = auth['oauth_token_secret']
    return d.HttpResponseRedirect(auth["auth_url"])

@d("/dtwitter/callback/")
def callback(request):
    twitter = Twython(
        settings.TWITTER_KEY, settings.TWITTER_SECRET,
        request.session["OAUTH_TOKEN"], request.session["OAUTH_TOKEN_SECRET"]
    )
    oauth_verifier = request.GET['oauth_verifier']

    final_step = twitter.get_authorized_tokens(oauth_verifier)

    OAUTH_TOKEN = final_step['oauth_token']
    OAUTH_TOKEN_SECERT = final_step['oauth_token_secret']
    TWITTER_USERNAME = final_step["screen_name"]
    TWITTER_USERID = final_step["user_id"]

    cb_module, cb_method = get_mod_func(settings.TWITTER_CALLBACK)
    cb = getattr(__import__(cb_module, {}, {}, ['']), cb_method)

    return cb(
        OAUTH_TOKEN, OAUTH_TOKEN_SECERT, TWITTER_USERNAME, TWITTER_USERID
    )
