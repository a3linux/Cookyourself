from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from django.db.models import Max
from django.template import Template, Context, loader

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user',blank=True, null=True, on_delete=models.CASCADE)
    userid = models.CharField(max_length=1024, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='img/', blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    join_in = models.DateTimeField(default=timezone.now, blank=True)
    location = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return str(self.user)

class DishImage(models.Model):
    name = models.CharField(max_length=128)
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='image', blank=True, null=True)
    image = models.ImageField(upload_to='img/', blank=True, null=True)

    def __str__(self):
        return "IMG_" + self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    price = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

class Style(models.Model):
    name = models.CharField(max_length=128)
    parent = models.ForeignKey("self", blank=True, null=True)

    def __str__(self):
        return "Style" + self.name

class Dish(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256, blank=True, null=True)
    style = models.ForeignKey(Style, blank=True, null=True)
    popularity = models.IntegerField(default=0)
    # Not sure whether it should be optinal field (Posts)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RelationBetweenDishIngredient',
                                         blank=True)
    calories = models.IntegerField(blank=True, null=True)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Tutorial(models.Model):
    dish = models.OneToOneField(Dish, related_name='tutorial')
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Tutorial for " + str(self.dish)

class Instruction(models.Model):
    content = models.CharField(max_length=1024)
    tutorial = models.ForeignKey(Tutorial, blank=True, null=True)

    def __str__(self):
        return self.content

class Post(models.Model):
    author = models.ForeignKey(UserProfile)
    # Posts are related to particular dish
    dish = models.ForeignKey(Dish)
    content = models.TextField(max_length=1024)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Post: " + self.content + ", by " + str(self.author)

    # Returns all recent additions and deletions to the to-do list.
    @staticmethod
    def get_posts(time="1970-01-01T00:00+00:00"):
        return Post.objects.filter(created_on__gt=time).distinct()

    # Generates the HTML-representation of a single to-do list item.
    @property
    def html(self):
        template= loader.get_template('post-list.html')
        #data = {'postid': self.id, 'content':''}
        #form=CreateNewCommentForm(initial=data)
        context=Context({'post': self})
        return template.render(context).replace('\"','\'').replace('\n','')

    @staticmethod
    def get_max_time():
        return Post.objects.all().aggregate(Max('created_on'))['created_on__max'] or "1970-01-01T00:00+00:00"

class Comment(models.Model):
    author = models.ForeignKey(UserProfile)
    content = models.TextField(max_length=1024)
    # One post may come with many comments
    post = models.ForeignKey(Post)
    # current date & time will be added.
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Comment: " + content + ", by " + str(author)

class Unit(models.Model):
    name = models.CharField(max_length=128)
    rate = models.FloatField(blank=True, null=True)

    def __str_(self):
        return self.name

class RelationBetweenDishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='dish')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient')
    amount = models.FloatField(blank=True, null=True)
    unit = models.ForeignKey(Unit, blank=True, null=True)

    def __str__(self):
        return str(self.dish) + " requires {:d} ".format(self.amount) + \
        str(self.unit) + ' of ' + str(ingredient)

class CrawlerRecord(models.Model):
    url = models.URLField()
    # Current date & time will be added EVERY time the record is saved.
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return url + ", Last updated on " + str(self.pdated_on)

class Cart(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='cart')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RelationBetweenCartIngredient',
                                         blank=True)

class RelationBetweenCartIngredient(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingre')
    amount = models.IntegerField(blank=True, null=True)
    unit = models.ForeignKey(Unit, blank=True, null=True)

    def __str__(self):
        return str(self.cart) + " has {:d} ".format(self.amount) + \
        str(self.unit.name) + ' of ' + str(self.ingredient)
