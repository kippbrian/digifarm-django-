from django.urls import path
from . import views
from . views import login, register
app_name = 'accounts'
urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),

]
