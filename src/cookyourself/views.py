from django.shortcuts import render
from django.http import HttpResponse
from cookyourself.models import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404, JsonResponse
import urllib
import json

GLOBAL_LOADMORE_NUM = 18


# Create your views here.
def index(request):
    print ("enter index")
    dishes = Dish.objects.all().order_by('-popularity')  # default order
    # dishsets = [{'dish': dish, 'image': DishImage.objects.filter(dish=dish)[0].image} for dish in dishes]
    dishsets = []
    cnt = 0
    for dish in dishes:
        if cnt >= GLOBAL_LOADMORE_NUM:
            break
        d = {}
        d['dish'] = dish
        d['image'] = DishImage.objects.filter(dish=dish)[0].image
        dishsets.append(d)
        cnt += 1
    context = {'sets': dishsets}
    return render(request, 'main.html', context)


def loadmore(request):
    cookies = request.COOKIES.get('cookies')  # updated in refresh.jsx, used to maintain list of showing pic
    dishes = Dish.objects.all().order_by('-popularity')  # default order
    context = {}
    dishsets = []
    cnt = 0
    for dish in dishes:
        if cnt >= GLOBAL_LOADMORE_NUM:
            break
        if cookies is not None and str(dish.id) in cookies:
            continue
        d = {}
        d['id'] = dish.id
        d['name'] = dish.name
        cnt += 1
        # use unquote to fix colon's %3A expression
        d['url'] = urllib.parse.unquote(DishImage.objects.filter(dish=dish)[0].image.url)
        dishsets.append(d)

    context['sets'] = dishsets
    return HttpResponse(json.dumps(context), content_type='application/json')


def dish(request, id=0):
    errors = []
    dish = Dish.objects.filter(id=id)
    if len(dish) == 0:
        errors.append('This dish does not exist')
        context = {'errors': errors}
    else:
        dish = Dish.objects.get(id=id)
        image = DishImage.objects.filter(dish=dish)[0].image
        tutorial = Tutorial.objects.get(dish=dish)
        instructions = Instruction.objects.filter(tutorial=tutorial)
        ingredients = dish.ingredients.all()
        # tutorial & instruction?
        ingre_sets = []
        for ingredient in ingredients:
            detail = RelationBetweenDishIngredient.objects.filter(dish=dish, ingredient=ingredient)[0]
            if detail:
                amount = detail.amount
                unit = detail.unit
                if unit:
                    uname = detail.unit.name
                    dic = {'ingredient': ingredient, 'amount': amount, 'unit': unit.name}
                else:
                    dic = {'ingredient': ingredient, 'amount': amount}
                ingre_sets.append(dic)
        posts = Post.objects.filter(dish=dish)
        context = {'dish': dish, 'isets': ingre_sets, 'tutorial': tutorial,
                   'image': image, 'instructions': instructions, 'posts': posts}

    return render(request, 'dish.html', context)


def shoppinglist(request):
    return render(request, 'shoppinglist.html')


def recommendation(request):
    return render(request, 'recommendation.html')


def profile(request, id=0):
    errors = []
    user = User.objects.filter(id=id)
    if len(user) == 0:
        errors.append('This user does not exist')
        context = {'errors': errors}
    else:
        user_of_profile = User.objects.get(id=id)
        profile = UserProfile.objects.get(user=user_of_profile)
        context = {'profile': profile}
    return render(request, 'profile.html', context)


@csrf_exempt
def add_ingredient(request, id):
    user = request.user
    cart = Cart.objects.filter(user=user)
    if cart:
        cart = Cart.objects.get(user=user)
    else:
        new_cart = Cart(user=request.user)
        new_cart.save()
    ingredient = ingredient.objects.get(id=id)
    cart_detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
    if cart_detail:
        cart_detail = cart_detail[0]
        cart_detail.amount += 1
        cart_detail.save()
    else:
        cart_detail = RelationBetweenCartIngredient.objects.create(cart=cart, ingredient=ingredient, amount=0)
    return HttpResponse("")
