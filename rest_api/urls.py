
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('5g-mobility/', include('mobility_5g_rest_api.urls')),
]
