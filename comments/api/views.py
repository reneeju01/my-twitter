from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


class CommentViewSet(viewsets.GenericViewSet):
    """
    Only implement list, create, update, destroy
    no need retrieve ( any single comment) method

    POST /api/comments/  -> create
    GET  /api/comments/  -> list
    GET /api/comments/1/ -> retrieve (Not Implemented)
    DELETE /api/comments/1/ -> destroy
    PATCH /api/comments/1/  -> partial_update (Not Implemented)
    PUT /api/comments/1/    -> update

    """
    serializer_class = CommentSerializerForCreate
    # /api/comments/1/
    # self.get_object() from queryet get id=1
    # Comment.objects.all().get(id=1)
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        # use the instance of AllowAny() / IsAuthenticated()
        # not a class name AllowAny / IsAuthenticated
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        # GET /api/comments/
        if 'tweet_id' not in request.query_params:
            return Response({
                'message': 'missing tweet_id in request',
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)

        # it works but not the best way
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)

        queryset = self.get_queryset()
        comments = self.filter_queryset(queryset).\
            prefetch_related('user').\
            order_by('created_at')

        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        # POST /api/comments/
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

    def update(self, request, *args, **kwargs):
        # get_object will raise 404 error if id is not exist
        # PUT /api/comments/1/
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save will trigger the update method in serializer,
        # click on the specific implementation of save to see
        # save decides whether to trigger create or update based on whether the
        # instance parameter is passed or not
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # DELETE /api/comments/1/
        comment = self.get_object()
        comment.delete()
        # In DRF, the default status code for destroy is 204 status
        # code = 204 no content
        # Here success=True is returned, which is more intuitive for the front
        # end, so return 200 is more appropriate
        return Response({'success': True}, status=status.HTTP_200_OK)
