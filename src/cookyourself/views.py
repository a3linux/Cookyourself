from django.shortcuts import render
from django.http import HttpResponse
from cookyourself.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

# Create your views here.
def index(request):
    dishes = Dish.objects.all().order_by('-popularity') #default order
    dishsets=[]
    for dish in dishes:
        images=DishImage.objects.filter(dish=dish)
        if images:
            dic={'dish':dish, 'image':images[0].image}
        else:
            dic={'dish':dish}
        dishsets.append(dic)
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
                unit=detail.unit
                if unit:
                    uname=detail.unit.name
                    dic={'ingredient':ingredient,'amount':amount, 'unit': unit.name}
                else:
                    dic={'ingredient':ingredient,'amount':amount}
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

@csrf_exempt 
def add_ingredient(request, id):
    user=request.user
    cart=Cart.objects.filter(user=user)
    if cart:
        cart=Cart.objects.get(user=user)
    else:
        new_cart = Cart(user=request.user)
        new_cart.save()
    ingredient = ingredient.objects.get(id=id)
    cart_detail=RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
    if cart_detail:
        cart_detail=cart_detail[0]
        cart_detail.amount+=1
        cart_detail.save()
    else:
        cart_detail=RelationBetweenCartIngredient.objects.create(cart=cart, ingredient=ingredient, amount=0)
    return HttpResponse("")

@csrf_exempt 
def add_user(request):
    token=request.POST.get('t', None) 
    fuser=UserProfile.objects.filter(token=token)
    if not fuser:
        username=request.POST.get('usr', None)
        photo=request.POST.get('url', None)
        new_user = UserProfile(token=token, username=username, photo=photo)
        new_user.save()
    return HttpResponse("")
    