from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('posts/', views.MyPostListView.as_view(), name='my_posts_list'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('posts/detail/<int:pk>/', views.PostDetailView.as_view(), name='posts_detail'),
    path('posts/<int:pk>/update/', views.PostUpdateView.as_view(), name='update'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete'),
    path('posts/create/', views.CreatePostView.as_view(), name='create'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('post/<int:pk>/like/', views.toggle_like, name='like_post'),
    path('comment/<int:pk>/like/', views.toggle_comment_like, name='like_comment'),
]