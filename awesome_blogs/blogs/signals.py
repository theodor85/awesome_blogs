from .models import Post, Subscriptions, Feed

# читать снизу вверх

def _get_followers(post):
    subscriptions = Subscriptions.objects.filter(subscribe_to=post.author)
    return [sub.user for sub in subscriptions]

def _refresh_feed(post):
    followers = _get_followers(post)
    for follower in followers:
        feed = Feed(user=follower, post=post, read=False)
        feed.save()


def _send_email_notifications(post):
    pass


def send_notifications_and_refresh_feed(sender, **kwargs):
    ''' Обработчик сигнала сохранения записи поста. '''
    
    instance = kwargs['instance']
    is_created = kwargs['created']

    if (type(instance) == Post) and is_created:
        _send_email_notifications(instance)
        _refresh_feed(instance)