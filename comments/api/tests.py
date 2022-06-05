from rest_framework import status
from rest_framework.test import APIClient
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.lucky = self.create_user('lucky')
        self.lucky_client = APIClient()
        self.lucky_client.force_authenticate(self.lucky)
        self.comsmo = self.create_user('comsmo')
        self.comsmo_client = APIClient()
        self.comsmo_client.force_authenticate(self.comsmo)

        self.tweet = self.create_tweet(self.lucky)

    def test_create(self):
        # anonymous user
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post without any parameter
        response = self.lucky_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Plase check input.')
        self.assertEqual('content' in response.data['errors'], True)
        self.assertEqual('tweet_id' in response.data['errors'], True)

        # post with tweet_id
        response = self.lucky_client.post(
            COMMENT_URL,
            {'tweet_id': self.tweet.id},
        )
        self.assertEqual(response.data['message'], 'Plase check input.')
        self.assertEqual('content' in response.data['errors'], True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # post with content
        response = self.lucky_client.post(COMMENT_URL, {'content': '1'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Plase check input.')
        self.assertEqual('tweet_id' in response.data['errors'], True)

        # content too long, longer than 140
        response = self.lucky_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Plase check input.')
        self.assertEqual('content' in response.data['errors'], True)

        # post sucess with tweet_id and content
        response = self.lucky_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.lucky.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')




