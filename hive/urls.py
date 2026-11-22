from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('flats/', views.flats, name='flats'),
    path('flats/<int:pk>/edit/', views.flats, name='flat_edit'),
    path('charges/', views.charges, name='charges'),
    path('charges/<int:pk>/pay/', views.payment, name='payment'),
    path('expenses/', views.expenses, name='expenses'),
]
