from rest_framework import serializers
from mizik.models import *
from mizik.models import User
from django.contrib.auth import authenticate, login
from mutagen.mp3 import MP3

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        # read_only_fields = ('user',)

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        # read_only_fields = ('user',)

class RetraitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retrait
        fields = '__all__'
        # read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = '__all__'
        
class GenreSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Genre
        fields = '__all__'
        
def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

class SongSerializer(serializers.ModelSerializer):
    get_total_price = serializers.CharField()
    author = serializers.CharField()
    img = serializers.SerializerMethodField()
    uri = serializers.SerializerMethodField()
    durationMillis = serializers.SerializerMethodField()
    
    class Meta: 
        model = Song
        exclude = ('image', 'album', 'file', 'file_demo', 'is_active')
        
    def get_img(self, song):
        request = self.context.get('request')
        if song.image:
            img = song.image.url
        else:
            img = song.album.image.url
        return request.build_absolute_uri(img)
    
    def get_uri(self, song):
        request = self.context.get('request')
        uri = song.file_demo.url
        return request.build_absolute_uri(uri)
    
    def get_durationMillis(self, song):
        if song.file_demo:
            audio = MP3(song.file_demo)
            durationMillis = audio.info.length * 1000
            hours, mins, seconds = convert(durationMillis)
            return '{}:{}'.format(mins, seconds)
        return None

class AuthorizeSongSerializer(serializers.ModelSerializer):
    get_total_price = serializers.CharField()
    get_amount_saved = serializers.CharField()
    author = serializers.CharField()
    img = serializers.SerializerMethodField()
    uri = serializers.SerializerMethodField()
    durationMillis = serializers.SerializerMethodField()
    
    class Meta: 
        model = Song
        exclude = ('image', 'album', 'file', 'file_demo', 'price', 'discount_price', 'is_active')
        
    def get_img(self, song):
        request = self.context.get('request')
        if song.image:
            img = song.image.url
        else:
            img = song.album.image.url
        return request.build_absolute_uri(img)
    
    def get_uri(self, song):
        request = self.context.get('request')
        uri = song.file.url
        return request.build_absolute_uri(uri)
    
    def get_durationMillis(self, song):
        if song.file:
            audio = MP3(song.file)
            durationMillis = audio.info.length * 1000
            return durationMillis
        return None
    
        
class AlbumSerializer(serializers.ModelSerializer):
    song_album = SongSerializer(read_only=True, many=True)
    class Meta: 
        model = Album
        fields = '__all__'


class LikeSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Like
        fields = '__all__'
        
class DownloadSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Download
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()
    # read_only_fields = ('id',)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Identifiants incorrects")

class WalletRequestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletRequested 
        fields = '__all__'

    