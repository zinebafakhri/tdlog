from django.urls import path
from . import views  # Importez vos vues locales

urlpatterns = [
    path('', views.login_view, name='login'),
    path('itinerary/', views.itinerary_view, name='itinerary'),
    path('finalize_routes/', views.finalize_routes, name='finalize_routes'),
    path('update_routes/', views.update_routes, name='update_routes'),
    path('recalculate_routes/', views.recalculate_routes, name='recalculate_routes'),
    path('signup/', views.signup_view, name='signup'),  # Ajout de l'URL pour l'inscription
]
