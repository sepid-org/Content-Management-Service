from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from rest_framework import serializers


class CustomTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No user found with this username.')

            refresh = RefreshToken.for_user(user)

            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            raise serializers.ValidationError('Username is required.')

    def get_token(self, user):
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        refresh["origin"] = user.origin
        access_token["origin"] = user.origin

        return {
            'refresh': str(refresh),
            'access': str(access_token),
        }
