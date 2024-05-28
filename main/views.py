from rest_framework import generics
from django.shortcuts import render
from pywikibot.exceptions import TitleblacklistError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Article, ArticleList
from .serializers import ArticleSerializer, ArticleListSerializer, ArticleListTitleSerializer, UserSerializer
from .functions import *

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_article_list(request):
    list_title = request.data.get('list_title')
    article_title = request.data.get('article_title')
    if list_title and article_title:
        try:
            _, created = get_or_create_article_list_from_title(request.user, list_title, article_title)
        except Exception as e:
            return Response({'status': 'error', 'message': "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        if created:
            return Response({'status': 'success', 'message': 'List created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'success', 'message': 'List existed - Article added to list'}, status=status.HTTP_200_OK)
    elif list_title:
        try:
            _, created = get_or_create_article_list_from_title(request.user, list_title)
        except Exception as e:
            return Response({'status': 'error', 'message': "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        if created:
            return Response({'status': 'success', 'message': 'List created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'success', 'message': 'List exists'}, status=status.HTTP_200_OK)
    return Response({'status': 'error', 'message': 'List title is required'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_article_to_list(request):
    list_title = request.data.get('list_title')
    article_title = request.data.get('article_title')
    if not list_title or not article_title:
        return Response({'status': 'error', 'message': 'List title and article title are required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        article = get_or_create_article_from_title(article_title)
    except Exception as e:
        error_message = str(e)
        return Response({'status': 'error', 'message': error_message}, status=status.HTTP_400_BAD_REQUEST)
    try:
        article_list = get_list(request.user, list_title)
        if article_list is None:
            return Response({'status': 'error', 'message': 'List does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        article_list.articles.add(article)
        return Response({'status': 'success', 'message': 'Article added to list'}, status=status.HTTP_200_OK)
    except Exception as e:
        error_message = str(e)
        return Response({'status': 'error', 'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_article_list(request):
    list_title = request.query_params.get('list_title')
    if not list_title:
        return Response({'status': 'error', 'message': 'List title is required'}, status=status.HTTP_400_BAD_REQUEST)
    article_list = get_list(request.user, list_title)
    if article_list is None:
        return Response({'status': 'error', 'message': 'List does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ArticleListSerializer(article_list)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_user_article_lists(request):
    article_lists = ArticleList.objects.filter(user=request.user)
    serializer = ArticleListTitleSerializer(article_lists, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_num_lists(request):
    article_lists = ArticleList.objects.filter(user=request.user)
    return Response({'num_lists': article_lists.count()}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_user(request):
    _, created = get_or_create_article_list_from_title(request.user, "Viewed")
    _, created = get_or_create_article_list_from_title(request.user, "Saved")
    return Response({'status': 'success', 'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

class UserCreateView(generics.CreateAPIView):
        serializer_class = UserSerializer


