from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
)

class CommentViewSet(viewsets.GenericViewSet):
    """
    Only implement list, create, update, destroy
    no need retrieve ( any single comment) method

    POST /api/comments/  -> create
    GET  /api/comments/  -> list
    GET /api/comments/1/ -> retrieve
    DELETE /api/comments/1/ -> destroy
    PATCH /api/comments/1/  -> partial_update
    PUT /api/comments/1/    -> update

    """
    serializer_class = CommentSerializerForCreate
    # /api/comments/1/
    # self.get_object() from queryet get id=1
    # Comment.objects.all().get(id=1)
    queryset = Comment.objects.all()

    def get_permissions(self):
        # use the instance of AllowAny() / IsAuthenticated()
        # not a class name AllowAny / IsAuthenticated
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # Use 'data=' since the 1st parameter is instance as default
        # This is wrong: CommentSerializerForCreate(data):  instance <= data
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Plase check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save will trigle serializer create method
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )