from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from django.http import HttpResponseRedirect
from django.conf import settings
import moncashify
import random
import string
from mizik.serializers import *
from mizik.models import *
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.views import APIView
from django.core.mail import send_mail, BadHeaderError, mail_admins
from time import gmtime, strftime
from django.db.models import F
from knox.models import AuthToken
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.db.models import Q 
from rest_framework import status
from django.contrib.auth.models import update_last_login
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from knox.auth import TokenAuthentication
from datetime import datetime, timedelta


def view_404(request, exception=None):
    # make a redirect to homepage
    # you can use the name of url or just the plain link
    return redirect('/') # or redirect('name-of-index-url')

def index(request):
    return render(request, "build/index.html")

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

class AllSongView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        songs = Song.objects.filter(is_active=True)
        serializer = SongSerializer(songs, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
class AllAlbumView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        albums = Album.objects.all()
        serializer = AlbumSerializer(albums, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
class AllGenreView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
class MySongView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        songs = Song.objects.filter(album__artist=user)
        serializer = SongSerializer(songs, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request, format=None):
        user = self.request.user
        title = request.data.get("title")
        audio = request.data.get("audio")
        image = request.data.get("image")
        album_id = request.data.get("album_id")
        album = get_object_or_404(Album, id=album_id)
        Song.objects.create(album=album, title=title, audio=audio, image=image)
        songs = Song.objects.filter(album__artist=user)
        serializer = SongSerializer(songs, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
        

class MySongDownloadView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        songs = []
        downloads = Download.objects.filter(user=user, is_active=True)
        for download in downloads:
            songs.append(download.song)
        serializer = SongSerializer(songs, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request, format=None):
        user = self.request.user
        song_id = request.data.get("song_id")
        song = get_object_or_404(Song, id=song_id)
        Download.objects.get_or_create(user=user, song=song)
        songs = []
        downloads = Download.objects.filter(user=user, is_active=True)
        for download in downloads:
            songs.append(download.song)
        serializer = SongSerializer(songs, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)


class MyAlbumView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        albums = Album.objects.filter(artist=user)
        serializer = AlbumSerializer(albums, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request, format=None):
        user = self.request.user
        title = request.data.get("title")
        image = request.data.get("image")
        genre_id = request.data.get("genre_id")
        genre = get_object_or_404(Genre, id=genre_id)
        Album.objects.create(genre=genre, artist=user, title=title, image=image)
        alums = Album.objects.filter(artist=user)
        serializer = AlbumSerializer(alums, many=True, context={"request": request})
        return JsonResponse(serializer.data, safe=False)

class UserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request, format=None):
        user = self.request.user
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        description = request.data.get("description")
        email = request.data.get("email", None)
        photo = request.data.get("photo", None)
        user.first_name = first_name
        user.last_name = last_name
        user.description = description
        if photo:
            user.photo = photo
        if email:
            user.email = email
        user.is_complete = True
        user.save()
        serializer = UserSerializer(user, context={"request": request})
        return JsonResponse(serializer.data, safe=False)


class WalletView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        user = self.request.user
        wallet = get_object_or_404(Wallet, user=user)
        serializer = WalletSerializer(wallet)
        return JsonResponse(serializer.data, safe=False)


class WalletFormView(APIView):
    def post(self, request, format=None):
        token = request.META.get('HTTP_AUTHORIZATION', '').split()
        key = token[1].lower()[0:8]
        user = get_object_or_404(AuthToken, token_key=key).user
        montant = request.data.get("montant")
        order_id = create_ref_code()
        WalletRequested.objects.filter(is_complete=False).delete()
        WalletRequested.objects.create(user=user, montant=int(montant), ref_code=order_id)
        moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=True)
        payment = moncash.payment(order_id, int(montant))
        moncash_link = payment.redirect_url
        return JsonResponse({'lien_moncash': moncash_link})

class MoncashView(APIView):
    def post(self, request, format=None):
        transaction_id = request.GET['transactionId']
        moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=True)
        transaction = moncash.transaction_details_by_transaction_id(transaction_id)
        if transaction:
            montant = transaction["payment"]["cost"]
            order_id = transaction["payment"]["reference"]
            wallet_transaction = get_object_or_404(WalletRequested, ref_code=order_id, is_complete=False)
            WalletTransaction.objects.create(user=wallet_transaction.user, montant=montant)
            WalletRequested.objects.filter(user=wallet_transaction.user, ref_code=order_id).update(is_complete=True)
            return JsonResponse({'status': 1, 'message': 'wallet success'})
        else:
            return JsonResponse({'status': 0, 'message': 'wallet error'}, status=status.HTTP_400_BAD_REQUEST)

class RetraitView(APIView):
    def get(self, request, format=None):
        # token = request.META.get('HTTP_AUTHORIZATION', '')
        token = request.META.get('HTTP_AUTHORIZATION', '').split()
        key = token[1].lower()[0:8]
        tokenview = get_object_or_404(AuthToken, token_key=key).user.id
        # tokenview = AuthToken.objects.get(token_key=key).user
        user = User.objects.get(pk=tokenview)
        retrait = Retrait.objects.get(user=user)
        if not retrait:
            return JsonResponse({'status': 0, 'message': 'retrait with this id not found'}, status=status.HTTP_400_BAD_REQUEST)

        # You have a serializer that you specified which fields should be available in fo
        serializer = RetraitSerializer(retrait, many=True)
        # And here we send it those fields to our react component as json
        # Check this json data on React side, parse it, render it as form.
        return JsonResponse(serializer.data, safe=False)
    
    def post(self, request, format=None):
        user = self.request.user
        wallet = Wallet.objects.get(user=user)
        montant = request.data.get("montant")
        moncash_numero = request.data.get("phone")
        if wallet.montant >= int(montant):
            Retrait.objects.create(user=user, montant=montant)
            subject = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            messageadmin = "L'utilisateur %s veut faire un retrait de (%s Gourdes) a son compte moncash (%s) \n veuillez etre sure apres chaque retrait envoyer \n que vous activerez le button envoyer en True" % (user.username, montant, moncash_numero)
            mail_admins(subject, messageadmin)
            return JsonResponse({'status': 1, 'message': 'wallet success'})
        else:
            return JsonResponse({'status': 0, 'message': 'depot error'}, status=status.HTTP_400_BAD_REQUEST)