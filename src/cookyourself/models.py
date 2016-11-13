from django.db import models
from django.contrib.auth.models import User
# from django.contrib.contenttypes.fields import GenericRelation
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rank = models.IntegerField()
    photo = models.ImageField(upload_to='img/', blank=True, null=True)

    def __str__(self):
        return str(self.user)


# One-to-many-image-field reference:
# https://www.quora.com/What-is-the-best-way-to-implement-one-to-many-image-field-in-Django
class DishImage(models.Model):
    name = models.CharField(max_length=128)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey('content_type', 'object_id')
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE, related_name='image', blank=True, null=True)
    image = models.ImageField(upload_to='img/', blank=True, null=True)

    def __str__(self):
        return "IMG_" + self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    price = models.IntegerField(blank=True, null=True)
    # images = GenericRelation(Image)

    def __str__(self):
        return self.name

class Style(models.Model):
    name = models.CharField(max_length=128)
    parent = models.ForeignKey("self", blank=True, null=True)

    def __str__(self):
        return "Style" + self.name

class Dish(models.Model):
    name = models.CharField(max_length=128)
    desciption = models.CharField(max_length=256, blank=True, null=True)
    style = models.ForeignKey(Style, blank=True, null=True)
    popularity = models.IntegerField(default=0)
    # Not sure whether it should be optinal field (Posts)
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RelationBetweenDishIngredient',
                                         blank=True)
    calories = models.IntegerField(blank=True, null=True)
    # images = GenericRelation(Image)
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
        return "Post: " + content + ", by " + str(author)

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
    converted_units = models.ManyToManyField("self")

    def __str__(self):
        return self.name

class RelationBetweenDishIngredient(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='dish')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient')
    amount = models.IntegerField(blank=True, null=True)
    unit = models.ForeignKey(Unit, blank=True)

    def __str__(self):
        return str(self.dish) + " requires {:d} ".format(self.amount) + \
        str(self.unit.name) + ' of ' + str(self.ingredient)

class RelationBetweenUnits(models.Model):
    one_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='one_unit')
    converted_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='converted_unit')
    rate = models.FloatField(blank=True, null=True)

class CrawlerRecord(models.Model):
    url = models.URLField()
    # Current date & time will be added EVERY time the record is saved.
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return url + ", Last updated on " + str(self.pdated_on)
