from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        followers = FriendshipService.get_followers(tweet.user)

        # Wrong approach: for loop + query, very slow opreation
        # for follower in followers:
        #     NewsFeed.objects.create(user=follower, tweet=tweet)

        # Correct approach: use bulk_create
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in followers
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)
