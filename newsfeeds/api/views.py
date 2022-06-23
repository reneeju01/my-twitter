from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Self define the querset since get newsfeed has permission
        # Only can get the current login user's newsfeed
        # It is ok to use: self.request.user.newsfeed_set.all()
        # This is better and more clear to NewsFeed.objects.filter
        return NewsFeed.objects.filter(user=self.request.user)

    def list(self, request):
        serializer = NewsFeedSerializer(
            self.get_queryset(),
            context={'request': request},
            many=True,
        )
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)