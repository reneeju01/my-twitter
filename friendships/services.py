from friendships.models import Friendship


class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # Wrong approach 1
        # This will cause the N + 1 Queries problem
        # That is, it run a query to filter out all friendships
        # And in the for loop, it runs N queries to get the from_user
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # Wrong approach 2
        # This use the JOIN operation，join friendship table and user
        # table by from_user. join operation is febitions in large-scale user
        # web because it is very slow.
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # The correct approach 1: filter id，use IN Query
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # The correct approach 2:，use prefetch_related，it will be automatically
        # executed into 2 queries same as the above，use In Query
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]