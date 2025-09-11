from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('categories/', views.catergory_list, name='category_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('update/<int:pk>/', views.update_transaction, name='update_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),


    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/update/<int:pk>/', views.update_budget, name='update_budget'),
    path('budgets/delete/<int:pk>/', views.delete_budget, name='delete_budget'),
]
