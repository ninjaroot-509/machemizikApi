from rest_framework import routers
from .api import *
from django.urls import path
from . import views

urlpatterns = [
    path('genres', views.AllGenreView.as_view()),
    path('songs', views.AllSongView.as_view()),
    path('albums', views.AllAlbumView.as_view()),
    path('my-songs', views.MySongView.as_view()),
    path('my-albums', views.MyAlbumView.as_view()),
    path('my-downloads', views.MySongDownloadView.as_view()),
    path('user', views.UserView.as_view()),
    path('wallet', views.WalletView.as_view()),
    path('depot', views.WalletFormView.as_view()),
    path('retrait', views.RetraitView.as_view()),
    path('trasaction/success', views.MoncashView.as_view()),
]