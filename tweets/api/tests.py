from rest_framework.test import APIClient
from rest_framework import status
from testing.testcases import TestCase
from tweets.models import Tweet


# need to add '/' at the end, otherwise status.HTTP_301_MOVED_PERMANENTLY
# redirect exception will be raised
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@my-twitter.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        # loged in user
        self.user1_client.force_authenticate(self.user1)


        self.user2 = self.create_user('user2', 'user2@my-twitter.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]


    def test_list_api(self):
        # anonymous request, without user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # normal request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # test order by created_at desc, the newest tweet displayed first
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)


    def test_create_api(self):
        # must login user
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # must have content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # content not too short, len(content) > 6
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # content not too long, len(content) < 400
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': '0' * 141
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # normal post
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hello World, this is my first tweet!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # tweet with id=-1 does not exist
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        # test get a tweet along with its comments
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, tweet, 'holly s***')
        self.create_comment(self.user1, tweet, 'hmm...')
        self.create_comment(
            self.user1,
            self.create_tweet(self.user2, 'another tweet'),
            'hmm...this comment won not show under the current tweet',
        )
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)