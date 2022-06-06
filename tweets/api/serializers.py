from accounts.api.serializers import UserSerializer, UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerWithComments(TweetSerializer):
    user = UserSerializer()
    comments = CommentSerializer(source='comment_set', many=True)

    # 2. Implement serializers.SerializerMethodField to get comments
    # comments = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')

    # 2. Implement serializers.SerializerMethodField to get comments
    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet