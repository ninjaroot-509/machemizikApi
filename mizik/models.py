from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.core.mail import send_mail, BadHeaderError, mail_admins
from django.utils.html import format_html
import random
import string
from django.db.models import F

class UserManager(BaseUserManager):
    """Define a model manager for User model with no first_name field."""

    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not phone:
            raise ValueError('The given phone must be set')
        self.phone = phone
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        """Create and save a regular User with the given phone and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password, **extra_fields):
        """Create and save a SuperUser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **extra_fields)

class User(AbstractUser):
    username = None
    phone = PhoneNumberField(unique=True)
    description = models.TextField(max_length=500, blank=True)
    photo = models.ImageField(default='logo.png', upload_to='profile_pics/', null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'phone'

    def photo_preview(self):
        return format_html('<img src="{}" width="100px" height="60px"/>',self.photo.url,)

    
    class Meta:
        verbose_name = 'User Liste'
        verbose_name_plural = 'Listes des utilisateurs'

    def __str__(self):
        return self.first_name

def create_ref_code():
    return 'MM-' + ''.join(random.choices(string.digits, k=6))

class Genre(models.Model):
    name = models.CharField(max_length = 100)
    description = models.CharField(blank=True, max_length = 200)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.CharField(max_length = 500)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='albums/')

    def __str__(self):
        return self.title + '-' + self.artist.first_name

class Song(models.Model):
    album =  models.ForeignKey(Album, related_name='song_album', on_delete = models.CASCADE)
    image = models.ImageField(upload_to='albums/', null=True, blank=True)
    file = models.FileField(upload_to='songs/')
    file_demo = models.FileField(upload_to='songs/')
    title = models.CharField(max_length = 100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def author(self):
        return self.album.artist.first_name + ' ' + self.album.artist.last_name
    
    def get_song_price(self):
        return self.price

    def get_discount_song_price(self):
        return self.discount_price

    def get_total_price(self):
        if self.discount_price:
            return self.get_discount_song_price()
        return self.get_song_price()

    def get_amount_saved(self):
        return self.get_song_price() - self.get_discount_song_price()
    
class OrderSong(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.song.title}"

    def get_total_song_price(self):
        return self.song.price

    def get_total_discount_song_price(self):
        return self.song.discount_price

    def get_amount_saved(self):
        return self.get_total_song_price() - self.get_total_discount_song_price()

    def get_final_price(self):
        if self.song.discount_price:
            return self.get_total_discount_song_price()
        return self.get_total_song_price()
    
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    songs = models.ManyToManyField(OrderSong)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField()
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.first_name

    def get_total(self):
        total = 0
        for order_song in self.songs.all():
            total += order_song.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code
    
    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    song =  models.ForeignKey(Song, on_delete = models.CASCADE)

    def __str__(self):
        return self.user.first_name
    
class ViewSong(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    song =  models.ForeignKey(Song, on_delete = models.CASCADE)

    def __str__(self):
        return self.user.first_name
    
class Download(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    song =  models.ForeignKey(Song, on_delete = models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    montant = models.FloatField(default=40)

    class Meta:
        verbose_name = 'Portefeuille Liste'
        verbose_name_plural = 'Listes des portefeuilles'

    def __str__(self):
        return '{} a {} Gourdes'.format(self.user.first_name, self.montant) # TODO

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_wallet(sender, instance, **kwargs):
    instance.wallet.save()


class WalletRequested(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    montant = models.FloatField(default=0)
    ref_code = models.CharField(max_length=6)
    is_complete = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recharge Liste'
        verbose_name_plural = 'Listes des recharges'

    def __str__(self):
        return self.user.first_name # TODO

class WalletTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    montant = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Transaction Liste'
        verbose_name_plural = 'Listes des transactions'

    def __str__(self):
        return '{} a recu {} Gourdes le {}'.format(self.user.first_name, self.montant, self.date) # TODO

    def send_new_ballance_wallet(sender, instance, *args, **kwargs):
        Wallet.objects.filter(user=instance.user).update(montant=F('montant') + instance.montant)



    
class Retrait(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    montant = models.FloatField(default=0)
    is_done = models.BooleanField(default=True)
    envoyer = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Retrait Liste'
        verbose_name_plural = 'Listes des retraits'
    
    def __str__(self):
        return '{} a retire {} Gourdes a son portefeuille le {}'.format(self.user.first_name, self.montant, self.date) # TODO

    def send_new_retrait_wallet(sender, instance, *args, **kwargs):
        Wallet.objects.filter(user=instance.user).update(montant=F('montant') - instance.montant)


post_save.connect(Retrait.send_new_retrait_wallet, sender=Retrait)	
post_save.connect(WalletTransaction.send_new_ballance_wallet, sender=WalletTransaction)	