from comments.models import Comment
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from testing.testcases import TestCase


COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.lucky = self.create_user('lucky')
        self.lucky_client = APIClient()
        self.lucky_client.force_authenticate(self.lucky)
        self.cosmo = self.create_user('cosmo')
        self.cosmo_client = APIClient()
        self.cosmo_client.force_authenticate(self.cosmo)

        self.tweet = self.create_tweet(self.lucky)

    def test_create(self):
        # test fail to create with anonymous user
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


    def test_destroy(self):
        comment = self.create_comment(self.lucky, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # test fail to delete with anonymous user
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test fail to delete for non comment owner
        response = self.cosmo_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test success to delete with comment owner
        count = Comment.objects.count()
        response = self.lucky_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.lucky, self.tweet, 'original')
        another_tweet = self.create_tweet(self.cosmo)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # test fail to update with anonymous user
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # test fail to delete for non comment owner
        response = self.cosmo_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # test can ONLY update content
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.lucky_client.put(url, {
            'content': 'new',
            'user_id': self.cosmo.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.lucky)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)




