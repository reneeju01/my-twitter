from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to create, list tweets
    """
    # queryset will be called in self.get_queryset()
    #     def list(self):
    #         self.get_queryset()
    # queryset = Tweet.objects.all()

    # use when create a new tweet
    serializer_class = TweetSerializerForCreate

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """
        Override the list method, do not list all tweets, must specify
        user_id as a filter condition
        """
        if 'user_id' not in request.query_params:
            return Response(
                'missing user_id',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_id = request.query_params['user_id']

        #This query will be translated as
        #
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        #
        # This SQL query will use the compound index of user and created_at
        # A simple user index is not enough
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')

        # many=True will return a list of dict
        serializer = TweetSerializer(tweets, many=True)
        # Return response in json format
        return Response({'tweets': serializer.data})

    def create(self, request):
        """
        Override the create method, because need to use the currently logged in
        user as tweet.user by default, pass the requested user in context to
        serializer.
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        return Response(
            TweetSerializer(tweet).data,
            status=status.HTTP_201_CREATED,
        )
