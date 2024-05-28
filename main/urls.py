from os import name
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('article_list/create/', create_article_list, name='create_article_list'),
    path('article_list/add_article/', add_article_to_list, name='add_article_to_list'),
    path('article_list/get/', retrieve_article_list, name='retrieve_article_list'),
    path('article_list/get/all/', retrieve_user_article_lists, name='retrieve_user_article_lists'),
    path('article_list/get/count/', get_num_lists, name='get_num_lists'),
    path('user/create/', create_user, name='create_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserCreateView.as_view(), name='user_register'),
]


