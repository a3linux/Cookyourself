from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from cookyourself.models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.http import HttpResponse, Http404, JsonResponse
import urllib
import json

GLOBAL_LOADMORE_NUM = 18


# Create your views here.
def index(request):
    dishes = Dish.objects.all().order_by('-popularity')  # default order
    # dishsets = [{'dish': dish, 'image': DishImage.objects.filter(dish=dish)[0].image} for dish in dishes]
    dishsets = []
    cnt = 0
    for dish in dishes:
        if cnt >= GLOBAL_LOADMORE_NUM:
            break
        d = {}
        d['dish'] = dish
        obj = DishImage.objects.filter(dish=dish)
        if not obj:
            continue
        d['image'] = obj[0].image
        dishsets.append(d)
        cnt += 1
    context = {'sets': dishsets}
    return render(request, 'main.html', context)


def loadmore(request):
    cookies = request.COOKIES.get('dishes')  # updated in refresh.jsx, used to maintain list of showing pic
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
        obj = DishImage.objects.filter(dish=dish)
        if not obj:
            continue
        d['url'] = urllib.parse.unquote(obj[0].image.url)
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
    ingredient = Ingredient.objects.get(id=id)
    cart_detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
    if cart_detail:
        cart_detail = cart_detail[0]
        cart_detail.amount += 1
        cart_detail.save()
    else:
        cart_detail = RelationBetweenCartIngredient.objects.create(cart=cart, ingredient=ingredient, amount=0)
    return HttpResponse("")


@login_required
def shoppinglist(request):
    errors = []
    user = request.user
    userProfile = UserProfile.objects.filter(user=user)
    if len(userProfile) == 0:
        errors.append('This user does not exist')
    else:
        userProfile = UserProfile.objects.get(user=user)
    cart = Cart.objects.filter(user=userProfile)
    if len(cart) == 0:
        errors.append('The user cart does not exist')
    else:
        cart = Cart.objects.get(user=userProfile)

    ingredients = Ingredient.objects.all()
    if not ingredients:
        raise Http404

    ingredient_list = []
    total_price = 0
    for ingredient in ingredients:
        detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)[0]
        if not detail:
            continue
        unit = detail.unit
        rate = 1.0
        if unit:
            rate = unit.rate

        ingredient_list.append(ingredient)
        price = ingredient.price * detail.amount * rate
        total_price += price

    context = {
        "ingredients": ingredient_list,
        "price": total_price,
    }

    return render(request, 'shoppinglist.html', context)


@login_required
@transaction.atomic
def del_ingredient(request, id):
    errors = []
    user = request.user
    try:
        cart = Cart.objects.filter(user=user)
        ingredient_to_delete = Ingredient.objects.get(id=id)
        cart_detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient_to_delete)[0]
        cart_detail.amount = 0
        cart_detail.delete()
    except ObjectDoesNotExist:
        errors.append('The item does not exist in the cart of user:%s' % user.name)

    ingredients = Ingredient.objects.all()
    if not ingredients:
        raise Http404

    ingredient_list = []
    total_price = 0
    for ingredient in ingredients:
        detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)[0]
        if not detail:
            continue
        unit = detail.unit
        rate = 1.0
        if unit:
            rate = unit.rate
        amount = detail.amount
        ingredient_list.append(ingredient)
        price = ingredient.price * amount * rate
        total_price += price

    context = {
        "ingredients": ingredient_list,
        "price": total_price,
        "errors": errors
    }

    return render(request, 'shoppinglist.html', context)


@login_required
def get_shoppinglist(request):
    user = request.user
    userProfile = UserProfile.objects.filter(user=user)
    cart = userProfile.cart
    if not cart:
        raise Http404

    ingredients = Ingredient.objects.all()
    if not ingredients:
        raise Http404

    ingredient_list = []
    total_price = 0
    for ingredient in ingredients:
        ingre = {}
        detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)[0]
        if not detail:
            continue
        unit = detail.unit
        rate = 1.0
        if unit:
            rate = unit.rate
        ingre['name'] = ingredient.name
        ingre['id'] = ingredient.id
        ingredient_list.append(ingre)
        price = ingredient.price * detail.amount * rate
        total_price += price

    context = {
        "ingredients": ingredient_list,
        "price": total_price,
    }
    return HttpResponse(json.dumps(context), content_type='application/json')


@csrf_exempt
def add_user(request):
    uid = request.POST.get('uid', None)
    if uid is not None:
        fuser = UserProfile.objects.filter(userid=uid)
        if not fuser:
            username = request.POST.get('username', None)
            photo = request.POST.get('url', None)
            gender = request.POST.get('gender', None)
            location = request.POST.get('location', None)
            email = request.POST.get('email', None)
            new_user = User(username=username)
            if email:
                new_user.email = email
            new_user.save()
            new_user_profile = UserProfile(user=new_user, userid=uid, photo=photo, gender=gender, location=location)
            new_user_profile.save()
            login(request, new_user)
        else:
            fuser = UserProfile.objects.get(userid=uid)
            user = fuser.user
            login(request, user)

        response_text = json.dumps({"usrid": request.user.id})
        return HttpResponse(response_text, content_type="application/json")
    return HttpResponse("")


@csrf_exempt
def logout_user(request):
    logout(request)
    return HttpResponse("")