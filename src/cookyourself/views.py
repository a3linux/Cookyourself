from django.shortcuts import render
from django.http import HttpResponse
from cookyourself.models import *

# Create your views here.
def index(request):
    dishes = Dish.objects.all().order_by('-popularity') #default order    
    dishsets = [{'dish':dish, 'image':DishImage.objects.filter(dish=dish)[0].image} for dish in dishes]
    context={'sets': dishsets}
    return render(request, 'main.html', context)

def dish(request, id=0):
    errors = []
    dish = Dish.objects.filter(id=id)
    if len(dish)==0:
        errors.append('This dish does not exist')
        context= {'errors': errors}
    else:
        dish= Dish.objects.get(id=id)
        image=DishImage.objects.filter(dish=dish)[0].image
        tutorial= Tutorial.objects.get(dish=dish)
        instructions = Instruction.objects.filter(tutorial=tutorial)
        ingredients=dish.ingredients.all()
        # tutorial & instruction?
        ingre_sets=[]
        for ingredient in ingredients:
            detail=RelationBetweenDishIngredient.objects.filter(dish=dish,ingredient=ingredient)[0]
            if detail:
                amount=detail.amount
                #gitter=detail.gitter
                #unit=detail.unit
                #uname=detail.unit.name
                dic={'ingredient':ingredient,'detail': detail}
                ingre_sets.append(dic)
        posts= Post.objects.filter(dish=dish)
        context = {'dish': dish, 'isets':ingre_sets, 'tutorial': tutorial, 
                   'image': image, 'instructions': instructions, 'posts': posts} 

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