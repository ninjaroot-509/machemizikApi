from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from numpy import True_
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
    description = models.CharField(max_length = 200)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    artist = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.CharField(max_length = 500)
    image = models.ImageField(upload_to='albums/')

    def __str__(self):
        return self.album_title + '-' + self.artist.first_name

class Song(models.Model):
    album =  models.ForeignKey(Album, related_name='song_album', on_delete = models.CASCADE)
    image = models.ImageField(upload_to='albums/', null=True, blank=False)
    file = models.FileField(upload_to='songs/')
    title = models.CharField(max_length = 100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class Like(models.Model):
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