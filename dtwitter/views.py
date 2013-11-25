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
    else:
        if "next" in request.session:
            del request.session["next"]

    if "app" in request.REQUEST:
        request.session["dtwitter_app"] = request.REQUEST["app"]
    else:
        if "dtwitter_app" in request.session:
            del request.session["dtwitter_app"]

    DTWITTER = settings.DTWITTER
    CONF = DTWITTER.get(request.session.get("dtwitter_app"), DTWITTER)

    if "KEY" in CONF:
        KEY = CONF["KEY"]
    else:
        KEY = DTWITTER["KEY"]

    if "SECRET" in CONF:
        SECRET = CONF["SECRET"]
    else:
        SECRET = DTWITTER["SECRET"]

    if "TEMPLATE" in CONF:
        TEMPLATE = CONF["TEMPLATE"]
    else:
        TEMPLATE = DTWITTER.get("TEMPLATE")

    if TEMPLATE and request.method == "GET":
        return TEMPLATE

    twitter = Twython(KEY, SECRET)
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
    DTWITTER = settings.DTWITTER
    CONF = DTWITTER.get(request.session.get("dtwitter_app"), DTWITTER)

    if "KEY" in CONF:
        KEY = CONF["KEY"]
    else:
        KEY = DTWITTER["KEY"]

    if "SECRET" in CONF:
        SECRET = CONF["SECRET"]
    else:
        SECRET = DTWITTER["SECRET"]

    if "DENIED" in CONF:
        DENIED = CONF["DENIED"]
    else:
        DENIED = DTWITTER.get("DENIED", "/?denied=true")

    if "PROFILE" in CONF:
        PROFILE = CONF["PROFILE"]
    else:
        PROFILE = DTWITTER.get("PROFILE", True)

    if "CALLBACK" in CONF:
        CALLBACK = CONF["CALLBACK"]
    else:
        CALLBACK = DTWITTER.get("CALLBACK", "dtwitter.default_callback")

    if "denied" in request.GET:
        resp = d.HttpResponseRedirect(DENIED)
    else:
        twitter = Twython(
            KEY, SECRET, request.session["OAUTH_TOKEN"],
            request.session["OAUTH_TOKEN_SECRET"]
        )
        oauth_verifier = request.GET['oauth_verifier']
        final_step = twitter.get_authorized_tokens(oauth_verifier)

        OAUTH_TOKEN = final_step['oauth_token']
        OAUTH_TOKEN_SECRET = final_step['oauth_token_secret']
        TWITTER_USERNAME = final_step["screen_name"]
        TWITTER_USERID = final_step["user_id"]

        cb_module, cb_method = get_mod_func(CALLBACK)
        cb = getattr(__import__(cb_module, {}, {}, ['']), cb_method)

        twitter = Twython(KEY, SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

        if PROFILE:
            profile = twitter.show_user(user_id=TWITTER_USERID)
            resp = cb(
                request, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, TWITTER_USERNAME,
                TWITTER_USERID, profile=profile
            )
        else:
            resp = cb(
                request, OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                TWITTER_USERNAME, TWITTER_USERID
            )

    if "next" in request.session:
        del request.session["next"]

    if "dtwitter_app" in request.session:
        del request.session["dtwitter_app"]

    if "OAUTH_TOKEN" in request.session:
        del request.session["OAUTH_TOKEN"]

    if "OAUTH_TOKEN_SECRET" in request.session:
        del request.session["OAUTH_TOKEN_SECRET"]

    return resp

