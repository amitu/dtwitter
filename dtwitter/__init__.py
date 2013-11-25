from importd import d


def default_callback(request, token, secret, username, userid, profile=None):
    request.session["dtwitter_token"] = token
    request.session["dtwitter_secret"] = secret
    request.session["dtwitter_username"] = username
    request.session["dtwitter_userid"] = userid
    if profile:
        request.session["dtwitter_profile"] = profile
    return d.HttpResponseRedirect(request.session.get("next", "/"))

