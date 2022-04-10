from django.contrib import admin
from django.urls import path, include
# from mizik.views import index
from mizik.api import RegisterAPI, LoginAPI, UserAPI
from knox import views as knox_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth', include('knox.urls')),
    path('api/auth/register', RegisterAPI.as_view()),
    path('api/auth/login', LoginAPI.as_view()),
    path('api/auth/user', UserAPI.as_view()),
    path('api/mizik/', include('mizik.urls')),
] + static(settings.STATIC_URL,
                           document_root=settings.STATIC_ROOT) 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Administration de MacheMizik"
admin.site.site_title = "MacheMizik"
admin.site.index_title = "Bienvenue Admin"