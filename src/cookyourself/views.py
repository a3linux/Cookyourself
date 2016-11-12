from django.shortcuts import render
from django.http import HttpResponse
from cookyourself.models import *

# Create your views here.
def index(request):
    #dishes = Dish.objects.all().order_by('-popularity') #default order
    #context = {'dishes': dishes}
    return render(request, 'main.html', context)

def dish(request, id=0):
    errors = []
    dish = Dish.objects.filter(id=id)
    if len(dish)==0:
        errors.append('This dish does not exist')
        context= {'errors': errors}
    else:
        dish= Dish.objects.get(id=id)
        tutorial= Tutorial.objects.get(dish=dish)
        instructions = instruction.objects.filter(tutorial=tutorial)
        # tutorial & instruction?
        posts= Post.objects.filter(dish=dish)
        Comments={}
        for post in posts:
            comment=Comment.objects.filter(post=post)
            Comments[post.id]=comment
        context = {'dish': dish, 'tutorial': tutorial, 
                   'instructions': instructions, 'posts': posts, 
                   'comments': Comments} 

    return render(request, 'dish.html', context)

def shoppinglist(request):
    return render(request, 'shoppinglist.html')

def recommendation(request):
    return render(request, 'recommendation.html')

def profile(request, id=0):
    errors = []
    user=User.objects.filter(id=id)
    if len(user)==0:
        errors.append('This user does not exist')
        context= {'errors': errors}
    else:
        user_of_profile= User.objects.get(id=id)
        profile=UserProfile.objects.get(user=user_of_profile)       
        context = {'profile': profile} 
    return render(request, 'profile.html', context)

def add_ingredient(request, id):
    user=request.user
    cart=Cart.objects.filter(user=user)
    if cart:
        cart=Cart.objects.get(user=user)
        ingredient = ingredient.objects.get(id=id)
        cart.ingredients.add(ingredient)
        cart.save()
    return HttpResponse("")