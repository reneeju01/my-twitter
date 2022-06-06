from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.lucky = self.create_user('lucky')
        self.tweet = self.create_tweet(self.lucky)
        self.comment = self.create_comment(self.lucky, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.lucky, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.lucky, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        cosmo = self.create_user('cosmo')
        self.create_like(cosmo, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)