from . import models
from django.contrib.auth.models import User

from . import wiki_fetcher as wf 

def get_or_create_article_from_title(title):
    if models.Article.objects.filter(title=title).exists():
        return models.models.Article.objects.get(title=title)
    try:
        wikicode = wf.parse(title)
        document = wf.wikicode_to_doc(wikicode)
        return models.Article.objects.create(title=title, description=document[0]["content"], content=document)
    except Exception as e:
        return e

def get_or_create_article_list_from_title(user, list_title, article_title=None):
    try:
        if article_title:
            try :
                article = get_or_create_article_from_title(article_title)
                article_list, created = models.ArticleList.objects.get_or_create(title=list_title, user=user)
                if not article_list.articles.filter(title=article_title).exists():
                    article_list.articles.add(article)
                return article_list, created
            except Exception as e:
                return e, False
        else:
            article_list, created = models.ArticleList.objects.get_or_create(title=list_title, user=user)
            return article_list, created
    except Exception as e:
        return e, False

def get_list(user, list_title):
    try:
        return models.ArticleList.objects.get(title=list_title, user=user)
    except models.ArticleList.DoesNotExist:
        return None

def get_user_list_titles(user):
    return models.ArticleList.objects.filter(user=user).values('title')

