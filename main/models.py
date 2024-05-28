from operator import mod
from django.core.files import images
from django.db import models
from django.db.models.fields import BlankChoiceIterator
from pywikibot.throttle import blake2b

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Article(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    content = models.TextField()
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def has_description(self):
        return self.description != ""

    def has_image(self):
        return self.image != None

class ArticleList(models.Model):
    title = models.CharField(max_length=100)
    articles = models.ManyToManyField(Article)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def num_articles(self):
        return self.articles.count()

    def get_articles(self):
        return self.articles.all()
