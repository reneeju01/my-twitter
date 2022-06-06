from datetime import timedelta
from testing.testcases import TestCase
from utils.time_helpers import utc_now


class TweetTests(TestCase):
    def setUp(self):
        self.lucky = self.create_user('lucky')
        self.tweet = self.create_tweet(self.lucky, content='So lucky')

    def test_hours_to_now(self):
        # set the tweet created at 10 hours ago
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.lucky, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.lucky, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        cosmo = self.create_user('cosmo')
        self.create_like(cosmo, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

