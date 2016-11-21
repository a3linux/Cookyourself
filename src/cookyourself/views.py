from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from cookyourself.models import *
from cookyourself.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.http import HttpResponse, Http404, JsonResponse
import urllib
import json
import random

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
                # unit=detail.unit
                # if unit:
                # uname=detail.unit.name
                # dic={'ingredient':ingredient,'amount':amount, 'unit': unit.name}
                # else:
                dic = {'ingredient': ingredient, 'amount': amount}
                ingre_sets.append(dic)
        posts = Post.objects.filter(dish=dish)
        init = {'dish': dish}
        form = PostForm.createPostForm(init)
        context = {'dish': dish, 'isets': ingre_sets, 'tutorial': tutorial, 'form': form,
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


@login_required
@transaction.atomic
def add_ingredient(request, id):
    errors = []
    user = request.user
    userProfile = UserProfile.objects.filter(user=user)
    if len(userProfile) == 0:
        errors.append('This user does not exist')
    else:
        userProfile = UserProfile.objects.get(user=user)
    cart = Cart.objects.filter(user=userProfile)
    if cart:
        cart = Cart.objects.get(user=userProfile)
    else:
        new_cart = Cart(user=userProfile)
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
        obj = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
        if not obj:
            continue
        detail = RelationBetweenCartIngredient.objects.get(cart=cart, ingredient=ingredient)
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
        obj = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
        if not obj:
            continue
        detail = RelationBetweenCartIngredient.objects.get(cart=cart, ingredient=ingredient)
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
    errors = []
    user = request.user
    userProfile = UserProfile.objects.filter(user=user)
    if len(userProfile) == 0:
        errors.append('User does not exist')
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
        ingre = {}
        obj = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
        if not obj:
            continue
        detail = RelationBetweenCartIngredient.objects.get(cart=cart, ingredient=ingredient)
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


@login_required
def logout_user(request):
    logout(request)
    return HttpResponse("")


@login_required
@csrf_exempt
def create_post(request):
    content = request.POST.get('content')
    dishid = request.POST.get('dish')
    dish = Dish.objects.get(id=dishid)
    author = UserProfile.objects.get(user=request.user)
    post = Post(dish=dish, author=author, content=content)
    post.save()
    response_data = json.dumps({"content": post.content})
    return HttpResponse(response_data, content_type="application/json")


@csrf_exempt
def update_posts(request):
    time = request.POST.get('time')
    max_time = Post.get_max_time()
    posts = Post.get_posts(time).order_by('-created_on')
    dishid = request.POST.get('dishid', None)
    if dishid:
        dish = Dish.objects.get(id=dishid)
        posts = posts.filter(dish=dish)
    userid = request.POST.get('userid', None)
    if userid:
        user = User.objects.get(id=userid)
        profile = UserProfile.objects.get(user=user)
        posts = posts.filter(author=profile)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')


def recommendation(request):
    last = Dish.objects.count() - 1
    index1 = random.randint(0, last)
    # Here's one simple way to keep even distribution for
    # index2 while still gauranteeing not to match index1.
    index2 = random.randint(0, last - 1)
    index3 = random.randint(0, last - 2)
    if index3 == index2: index3 = last - 1
    if index2 == index1: index2 = last
    if index3 == index1: index3 = last
    dishes = []
    dishes.append(Dish.objects.all()[index1])
    dishes.append(Dish.objects.all()[index2])
    dishes.append(Dish.objects.all()[index3])
    dishsets = []
    for dish in dishes:
        images = DishImage.objects.filter(dish=dish)
        if images:
            dic = {'dish': dish, 'image': images[0].image}
        else:
            dic = {'dish': dish}
        dishsets.append(dic)
    context = {'sets': dishsets}
    return render(request, 'recommendation.html', context)
