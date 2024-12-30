from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('', include('delivery_app.urls')),  # Include all delivery_app URLs
]
