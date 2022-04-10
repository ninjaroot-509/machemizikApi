from django.contrib import admin
from .models import *
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = [
        'phone',
        'first_name',
        'last_name',
        'photo_preview',
    ]
admin.site.register(User, UserAdmin)

class WalletAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'montant',
    ]
    search_fields = ['montant', 'user__first_name']
admin.site.register(Wallet, WalletAdmin)


class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'montant',
    ]
    list_filter = ['date', 'user']
    search_fields = ['montant', 'user__first_name']
admin.site.register(WalletTransaction, WalletTransactionAdmin)

class RetraitAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'montant',
        'envoyer',
        'is_done'
    ]
    list_editable = ['is_done',]
    list_filter = ['date', 'user', 'envoyer', 'is_done']
    search_fields = ['montant', 'user__first_name']
admin.site.register(Retrait, RetraitAdmin)

class WalletRequestedAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'montant',
        'is_complete',
        'date'
    ]
    list_filter = ['date', 'user', 'is_complete']
    search_fields = ['montant', 'user__first_name']
admin.site.register(WalletRequested, WalletRequestedAdmin)

admin.site.register(Album)
admin.site.register(Song)
admin.site.register(Like)
admin.site.register(Download)
admin.site.register(Genre)