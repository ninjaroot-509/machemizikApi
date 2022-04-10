from mizik.models import *
from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import settings
import moncashify
import random
import string
from knox.models import AuthToken
from django.contrib.auth.signals import user_logged_out
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
# TODO: permissions: POST vs GET (ks https://stackoverflow.com/questions/55549786/how-to-set-different-permission-classes-for-get-and-post-requests-using-the-same)

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    # .order_by('?')
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = WalletSerializer
    filterset_fields = ('__all__')

class WalletTransactionViewSet(viewsets.ModelViewSet):
    queryset = WalletTransaction.objects.all()
    # .order_by('?')
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = WalletTransactionSerializer
    filterset_fields = ('__all__')

class RetraitViewSet(viewsets.ModelViewSet):
    queryset = Retrait.objects.all()
    # .order_by('?')
    permissions_classes = [
        permissions.AllowAny
    ]
    serializer_class = RetraitSerializer
    filterset_fields = ('__all__')

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _,token = AuthToken.objects.create(user) 
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
        }) 

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        _,token = AuthToken.objects.create(user) 
        login(request, user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token,
        }) 
        
class LogoutAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request._auth.delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class LogoutAllAPI(APIView):
    '''
    Log the user out of all sessions
    I.E. deletes all auth tokens for the user
    '''
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(None, status=status.HTTP_204_NO_CONTENT)

class UserAPI(generics.RetrieveAPIView):
    permission_classes = [ 
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user