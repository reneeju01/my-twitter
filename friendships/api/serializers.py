from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User


# via source=xxx to get each model instance 's xxx
# model_instance.xxx to get the data
# Example: from friendships.models.Friendship model's from_user source
# to get all from_user for user_id=1
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can not follow yourself.',
            })

        # Another way to validate if to_user_id is exists or not is use
        # self.get_object() in views.py

        # if not User.objects.filter(id=attrs['to_user_id']).exists():
        #     raise ValidationError({
        #         'message': 'You can not follow a non-exist user.'
        #     })

        # The model serializer will check if the friendship exist or not before
        # the validate called. Raise 400 Bad Request
        # "errors": {
        #         "non_field_errors": [
        #             "The fields from_user_id, to_user_id must make a unique set."
        #         ]
        # }

        # if Friendship.objects.filter(
        #     from_user_id=attrs['from_user_id'],
        #     to_user_id=attrs['to_user_id'],
        # ).exists():
        #     raise ValidationError({
        #         'message': 'You already followed this user.'
        #     })
        return attrs

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )