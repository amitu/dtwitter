from dtwitter.models import TwitterUser

# TwitterAuthMiddleware
class TwitterAuthMiddleware:
    def process_request(self, request):
        if "twitter_user_id" in request.session:
            request.twitter_user = TwitterUser.objects.get(
                pk=request.session["twitter_user_id"]
            )
        else:
            request.twitter_user = None

def twitter_user(request):
    return { "twitter_user": getattr(request, 'twitter_user', None) }

