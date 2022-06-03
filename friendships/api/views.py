from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)

from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # set serializer_class for POST request: follow or unfollow
    serializer_class = FriendshipSerializerForCreate
    # We use POST /api/friendship/1/follow to follow a user which user_id=1
    # so we need to set queryset to User.objects.all()
    # If we use Friendship.objects.all, it will throw error 404 Not Found
    # Because the actions of detail=True will excute get_object() which is
    # queryset.filter(pk=1) to check if object exists or not

    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        # pk=1,  get all follwers for user_id=1
        friendships = Friendship.objects.filter(to_user_id=pk)
        serializer = FollowerSerializer(friendships, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        # GET /api/friendships/1/followings/
        # pk=1,  get all follwings for user_id=1
        friendships = Friendship.objects.filter(from_user_id=pk)
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # duplicated follow requests
        # if Friendship.objects.filter(
        #     from_user=request.user,
        #     to_user=pk
        # ).exists():
        #     return Response({
        #         'success': True,
        #         'message': 'You already followed this user.',
        #         'duplicate': True,
        #     }, status=status.HTTP_201_CREATED)

        # follow_user = self.get_object(): take pk as an input id to get the
        # user from the queryset, throw 404 Not Found if pk is a non-exist user
        # so 'to_user_id': pk or follow_user.id

        # check if user with id=pk exists
        self.get_object()

        # POST /api/friendships/<pk>/follow/
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = serializer.save()
        return Response(
            FollowingSerializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        # raise 404 if user with id=pk does not exist
        unfollow_user = self.get_object()

        # pk is str, request.user.id == int(pk)
        if request.user.id == unfollow_user.id:
            return Response({
                "success": False,
                "message": "You cannot unfollow yourself.",
            }, status=status.HTTP_400_BAD_REQUEST)

        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # Queryset's delete performs an SQL delete query on all rows in the
        # QuerySet and returns 2 values:
        # 1. the number of objects deleted
        # 2. a dictionary with the number of deletions per object type.
        # By default, Django’s ForeignKey emulates the SQL constraint
        # ON DELETE CASCADE — in other words, any objects with foreign keys
        # pointing at the objects to be deleted will be deleted along with them.
        # So, we set on_delete=on_delete=models.SET_NULL
        # instead of on_delete=models.CASCADE
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})


    def list(self, request):
        return Response({'message': 'this is friendships home page'})