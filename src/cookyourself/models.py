from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rank = models.IntegerField()
    photo = models.ImageField(upload_to='img/', blank=True, null=True)

    def __str__(self):
        return str(self.user)

class Post(models.Model):
    author = models.ForeignKey(UserProfile)
    # Posts are related to particular dish
    dish = models.ForeignKey(Dish)
    content = models.TextField(max_length=1024)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Post: " content + ", by " + str(author)

class Comment(models.Model):
    author = models.ForeignKey(UserProfile)
    content = models.TextField(max_length=1024)
    # One post may come with many comments
    post = models.ForeignKey(Post)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Comment: " content + ", by " + str(author)

class Image(models.Model):
    name = models.CharField(max_length=128)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to='img/', blank=True, null=True)

    def __str__(self):
        return "IMG_" + self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    price = models.IntegerField(blank=True, null=True)
    images = GenericRelation(Image)

    def __str__(self):
        return self.name

class Instruction(models.Model):
    content = models.CharField(max_length=1024)
    tutorial = models.ForeignKey(Tutorial, blank=True, null=True)

    def __str__(self):
        return self.content

class Tutorial(models.Model):
    dish = models.OneToOneField(Dish, related_name='tutorial')
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Tutorial for " + str(self.dish)

class Dish (models.Model):
    name = models.CharField(max_length=128)
    style = models.CharField(max_length=128, blank=True, null=True)
    popularity = models.IntegerField(default=0)
    # Not sure whether it should be optinal field (Posts)
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    calories = models.IntegerField(blank=True, null=True)
    images = GenericRelation(Image)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CrawlerRecord(models.Model):
    url = models.URLField()
    # Current date & time will be added EVERY time the record is saved.
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return url + ", Last updated on " + str(self.pdated_on)
