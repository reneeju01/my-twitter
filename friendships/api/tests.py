from rest_framework import status
from friendships.models import Friendship
from testing.testcases import TestCase
from rest_framework.test import APIClient


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):

        self.lucky = self.create_user('lucky')
        self.lucky_client = APIClient()
        self.lucky_client.force_authenticate(self.lucky)

        self.cosmo = self.create_user('comsmo')
        self.cosmo_client = APIClient()
        self.cosmo_client.force_authenticate(self.cosmo)

        # create followers and followingsfor cosmo
        for i in range(2):
            follower = self.create_user('cosmo_follower_{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.cosmo)
        for i in range(3):
            following = self.create_user('cosmo_following_{}'.format(i))
            Friendship.objects.create(from_user=self.cosmo, to_user=following)

        print(Friendship.objects.all())

    def test_follow(self):
        url = FOLLOW_URL.format(self.lucky.id)

        # test fail to follow with an anonymous user, login needed
        print('\n------ test fail to follow with an anonymous user ------')
        response = self.anonymous_client.post(url)
        print('response.data ==> ', response.data)
        print('response.status_code ==> ', response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test fail to follow with GET method
        print('\n------ test fail to follow with GET method ------')
        response = self.lucky_client.get(url)
        print('response.data ==> ', response.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # test fail to follow yourself
        print('\n------ test fail to follow with GET method ------')
        response = self.lucky_client.post(url)
        print('response.data ==> ', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test success to follow
        print('\n------ test success to follow ------')
        response = self.cosmo_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        print('response.data ==> ', response.data)
        self.assertEqual('created_at' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user']['id'], self.lucky.id)
        self.assertEqual(response.data['user']['username'], self.lucky.username)


        # # test silent operation on duplicated follow
        # print('\n------ test silent operation on duplicated follow ------')
        # response = self.cosmo_client.post(url)
        # print('response.data ==> ', response.data)
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(response.data['duplicate'], True)

        # test fail to duplicated follow
        print('\n------ test silent operation on duplicated follow ------')
        response = self.cosmo_client.post(url)
        print('response.data ==> ', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test success to reverse follow and create a new record
        print('\n------ test success to reverse follow and create a new '
              'record ------')
        count = Friendship.objects.count()
        response = self.lucky_client.post(FOLLOW_URL.format(self.cosmo.id))
        print('response.data ==> ', response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.lucky.id)

        # test fail to unfollow with an anonymous user, login needed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test fail to unfollow with GET method
        response = self.lucky_client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # test fail to unfollow yourself
        response = self.lucky_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test success to unfollow
        print('\n------ test success to unfollow ------')
        Friendship.objects.create(from_user=self.cosmo, to_user=self.lucky)
        count = Friendship.objects.count()
        print(Friendship.objects.all())
        response = self.cosmo_client.post(url)
        print('response.data ==> ', response.data)
        print(Friendship.objects.all())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # test silent operation on unfollow a unfollowed user
        print('\n------ test silent operation on unfollow a unfollowed user ------')
        count = Friendship.objects.count()
        response = self.cosmo_client.post(url)
        print('response.data ==> ', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)


    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.cosmo.id)

        # test fail to get followings with POST method
        response = self.anonymous_client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # test success to get the followings
        print('\n------ test success to get the followings ------')
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)

        print("response.data['followings'] ==> ", response.data['followings'])

        print('\n------ in reverse time order ------')
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'cosmo_following_2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'cosmo_following_1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'cosmo_following_0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.cosmo.id)

        # test fail to get followers with POST method
        response = self.anonymous_client.post(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

        # test success to get the followers
        print('\n------ test success to get the followers ------')
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)

        print("response.data['followers'] ==> ", response.data['followers'])

        # test in reverse time order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'cosmo_follower_1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'cosmo_follower_0',
        )