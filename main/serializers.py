from mwparserfromhell.nodes import extras
from rest_framework import serializers
from .models import Article, ArticleList
from .functions import *
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class ArticleListSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = ArticleList
        fields = '__all__'

class ArticleListTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleList
        fields = ['title']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extras_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
            )
        get_or_create_article_list_from_title(user, "Viewed")
        get_or_create_article_list_from_title(user, "Saved")
        return user

