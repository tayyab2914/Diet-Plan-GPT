from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('saveddiets', views.saveddiets, name="saveddiets"),
    path('signout', views.signout, name="signout"),
    path('creatediet', views.creatediet, name="creatediet"),
    path('dietplan/<slug>', views.dietplan, name="dietplan"),
]