from django.urls import path
from . import views

urlpatterns = [

    # User
    path('create/', views.create_blog, name='create_blog'),
    path('list/', views.blog_list, name='blog_list'),
    path('view/<int:id>/', views.view_blog, name='view_blog'),
    path('edit/<int:id>/', views.edit_blog, name='edit_blog'),
    path('delete/<int:id>/', views.delete_blog, name='delete_blog'),
    path('search/', views.search_blog, name='search_blog'),
    path('tag/<str:tag>/', views.tag_filter, name='tag_filter'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Admin
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-createblog/', views.admin_createblog, name='admin_createblog'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),
    path('manage-blogs/', views.manage_blogs, name='manage_blogs'),
]