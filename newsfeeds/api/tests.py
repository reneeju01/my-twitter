from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from rest_framework import status

NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):

        self.lucky = self.create_user('lucky')
        self.lucky_client = APIClient()
        self.lucky_client.force_authenticate(self.lucky)

        self.cosmo = self.create_user('cosmo')
        self.cosmo_client = APIClient()
        self.cosmo_client.force_authenticate(self.cosmo)

    def test_list(self):
        # test fail with an anonymous user, login needed
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test fail to use POST method
        response = self.lucky_client.post(NEWSFEEDS_URL)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        # no any news at the begginning
        response = self.lucky_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # you can see your own post
        self.lucky_client.post(POST_TWEETS_URL, {'content': 'Hello World'})
        response = self.lucky_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # after follow others able to see the tweets from others
        self.lucky_client.post(FOLLOW_URL.format(self.cosmo.id))
        response = self.cosmo_client.post(POST_TWEETS_URL, {
            'content': 'Hello Twitter',
        })
        posted_tweet_id = response.data['id']
        response = self.lucky_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(
            response.data['newsfeeds'][0]['tweet']['id'],
            posted_tweet_id
        )