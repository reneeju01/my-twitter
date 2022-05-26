from .serializers import UserSerializer, LoginSerializer, SignupSerializer
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """
        signup with username, email, password
        """
        # create a new user SignupSerializer(data=request.data)
        # update a user SignupSerializer(instance=request.user,
        # data=request.data)

        # username, email or password is missing in the request
        serializer = SignupSerializer(data=request.data)
        # call validate in SignupSerializer
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data ={
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR']
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # get username and password from request
        serializer = LoginSerializer(data=request.data)

        # validate the data field defined in LoginSerializer
        # if username or password is missing in the request
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input.",
                'errors': serializer.errors,
            }, status=400)

        # username is case-insensitive
        username = serializer.validated_data['username'].lower()
        password= serializer.validated_data['password']

        # # debug
        # queryset = User.objects.filter(username=username)
        # print(queryset.query)
        #
        # if not User.objects.filter(username=username).exists():
        #     return Response({
        #         "success": False,
        #         "message": "User does not exists.",
        #     }, status=400)

        user = django_authenticate(username=username, password=password)

        # wrong username or password
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        # sucess login
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    def list(self, request):
        return Response({
            "accounts": "This will show Account List when GET /api/accounts/,"
                        " otherwise it will throw Page not found (404) error."
        })