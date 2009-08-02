from django.db import models
from django.conf import settings

from datetime import datetime
import oauth
from oauthtwitter import OAuthApi

# TwitterUserManager # {{{ 
class TwitterUserManager(models.Manager):
    def get_or_create_from_info(self, user_info, access_token):
        twitter_user, _ = self.get_or_create(twitter_id=user_info.id)
        twitter_user.access_token = access_token
        twitter_user.update_twitter_info(user_info) # it saves
        return twitter_user, _
# }}} 

# TwitterUser # {{{ 
class TwitterUser(models.Model):
    twitter_id = models.CharField(max_length=20, primary_key=True)
    twitter_username = models.CharField(max_length=100, blank=True) 
    twitter_name = models.CharField(max_length=100, blank=True) 
    twitter_profile_picture = models.URLField(blank=True, verify_exists=False)
    twitter_description = models.CharField(max_length=200, blank=True)
    twitter_location = models.CharField(max_length=100, blank=True)

    access_token = models.CharField(max_length=200, blank=True)
    created_on = models.DateTimeField(default=datetime.now) 

    objects = TwitterUserManager()

    def __unicode__(self): return self.twitter_username

    def twitter_url(self): 
        return "http://twitter.com/%s" % self.twitter_username

    # get_twitter_api # {{{ 
    def get_twitter_api(self):
        assert self.access_token
        access_token = oauth.OAuthToken.from_string(self.access_token)
        return OAuthApi(
            settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET,
            access_token
        )
    api = property(get_twitter_api)
    # }}} 

    # update_twitter_info # {{{ 
    def update_twitter_info(self, user_info=None): 
        if not user_info:
            if self.access_token:
                user_info = self.get_twitter_api().GetUserInfo()
            else: return self 
        if user_info.id: self.twitter_id = user_info.id
        if user_info.name: self.twitter_name = user_info.name
        if user_info.screen_name: 
            self.twitter_username = user_info.screen_name
        if user_info.profile_image_url:
            self.twitter_profile_picture = user_info.profile_image_url
        if user_info.description: 
            self.twitter_description = user_info.description
        if user_info.location:
            self.twitter_location = user_info.location

        self.save()
        return self
    # }}} 

    def configure_url(self):
        return "http://fwd2tweet.com/configure/%s/%s/" % (
            self.email, md5.new(
                "%s%s" % (settings.SECRET_KEY, self.email)
            ).hexdigest()[:8]
        )

    def is_following(self, other_user):
        return other_user in [
            str(tu.screen_name) for tu in self.api.GetFriends()
        ]
# }}} 
