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

class SongInline(admin.TabularInline):
    """Tabular Inline View for Songs"""
    model = Song

class AlbumAdmin(admin.ModelAdmin):
    inlines = [
        SongInline,
    ]
    list_display = ['artist', 'title', 'genre', 'get_count_songs']
    list_filter = ['artist', 'genre']
    search_fields = ['title', 'artist__first_name', 'artist__last_name']
    def get_count_songs(self, obj):
        a = Song.objects.filter(album=obj.id).count()
        return a
    get_count_songs.short_description = 'Nombres de musiques'
admin.site.register(Album, AlbumAdmin)

admin.site.register(ViewSong)
admin.site.register(Like)
admin.site.register(Download)
admin.site.register(Genre)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'coupon'
    ]
    list_filter = ['user',
                   'ordered',]
    search_fields = [
        'user__first_name',
        'ref_code'
    ]

admin.site.register(Order, OrderAdmin)

class SongAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'get_price',
        'is_active'
    ]
    list_filter = ['title', 'is_active']
    search_fields = ['title',]
    def get_price(self, obj):
        if obj.discount_price:
            return obj.discount_price
        return obj.price
    get_price.short_description = 'Prix'
admin.site.register(Song, SongAdmin)

admin.site.register(OrderSong)
admin.site.register(Coupon)