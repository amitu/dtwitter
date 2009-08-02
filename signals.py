import django.dispatch 

new_twitter_user = django.dispatch.Signal(providing_args=["twitter_user"])
user_logged_in = django.dispatch.Signal(providing_args=["twitter_user"])
user_logged_out = django.dispatch.Signal(providing_args=["twitter_user"])

