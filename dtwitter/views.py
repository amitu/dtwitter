from importd import d
from django.conf import settings
from django.core.urlresolvers import get_mod_func, reverse

from twython import Twython

@d("/", name="dtwitter-index")
def idx(request):
    return d.HttpResponse(
        "<a href='%s'>start</a>" % reverse("dtwitter-connect")
    )

@d("/connect/", name="dtwitter-connect")
def connect(request):
    if "next" in request.REQUEST:
        request.session["next"] = request.REQUEST["next"]
    if getattr(settings, "DTWITTER_TEMPLATE") and request.method == "GET":
        return settings.DTWITTER_TEMPLATE

    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET)
    auth = twitter.get_authentication_tokens(
        callback_url="http://%s%s" % (
            settings.DOMAIN, reverse("dtwitter-callback")
        )
    )
    request.session["OAUTH_TOKEN"] = auth['oauth_token']
    request.session["OAUTH_TOKEN_SECRET"] = auth['oauth_token_secret']

    return d.HttpResponseRedirect(auth["auth_url"])

@d("/callback/", name="dtwitter-callback")
def callback(request):
    if "denied" in request.GET:
        return d.HttpResponseRedirect("/?denied=true")

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
        request, OAUTH_TOKEN, OAUTH_TOKEN_SECERT, TWITTER_USERNAME,
        TWITTER_USERID
    )
