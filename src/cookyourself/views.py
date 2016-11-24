from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.urls import reverse

from haystack.forms import ModelSearchForm
from haystack.query import EmptySearchQuerySet

import urllib
import json
import random

from cookyourself.models import *
from cookyourself.forms import *
from cookyourself import pdfgen

GLOBAL_LOADMORE_NUM = 18
GLOBAL_FILTER_START = 2
GLOBAL_RANK_LIST_NUM = 8 #update with rank_list
RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)


def check_id(id):
    if int(id) >= GLOBAL_RANK_LIST_NUM or int(id) < 0:
        return -1
    return 0

def get_rank_or_filter(id):
    ret = check_id(id)
    if (ret < 0):
        return ret
    rank_list = [
        # popularity
        "-popularity",  # popularity ascending
        "popularity",  # popularity descending
        # category
        "Cookies",
        "Chocolate",
        "Pies",
        # the style id shall be maintained the same with the value defined in main.html
        "American",  # style American
        "Scottish",  # style Indian
        "Russian",  # style Russian
        # "-price",  # price ascending
        # "price",  # price descending
    ]
    return rank_list[int(id)]


def get_dish_objects(id):
    ret = check_id(id)
    if (ret < 0):
        return -1
    target = get_rank_or_filter(id)
    if int(id) < GLOBAL_FILTER_START:
        dishes = Dish.objects.all().order_by(target)  # default order
    else:
        dishes = Dish.objects.filter(style__name__icontains=target)
    return dishes


def make_view(id=0):
    dishsets = []
    dishes = get_dish_objects(id)
    if not dishes or dishes == -1:
        return dishsets
    # dishsets = [{'dish': dish, 'image': DishImage.objects.filter(dish=dish)[0].image} for dish in dishes]
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
    return dishsets


def get_dishes(cookies, id=0):
    dishsets = []
    dishes = get_dish_objects(id)
    if not dishes or dishes == -1:
        return dishsets
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
    return dishsets


# Create your views here.
def index(request):
    dishsets = make_view(0)  # default is popularity ascending
    context = {'sets': dishsets}
    return render(request, 'main.html', context)


def loadmore(request, id=0):
    ret = check_id(id)
    if (ret < 0):
        raise Http404
    context = {}
    cookies = request.COOKIES.get('dishes')  # updated in refresh.jsx, used to maintain list of showing pic
    dishsets = get_dishes(cookies, id)
    context['sets'] = dishsets
    return HttpResponse(json.dumps(context), content_type='application/json')


def search(request, template='main.html', load_all=True,
        form_class=ModelSearchForm, searchqueryset=None, extra_context=None,
        results_per_page=None):
    query = ''
    results = EmptySearchQuerySet()
    dishsets = []
    if request.GET.get('q'):
        form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)

        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
    else:
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)

    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)
    try:
        page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("No such page of results!")

    for result in page.object_list:
        dish = result.object
        img = DishImage.objects.filter(dish=dish)
        if not img:
            continue

        d = dict()
        d['url'] = urllib.parse.unquote(img[0].image.url)
        d['id'] = dish.id
        d['name'] = dish.name
        dishsets.append(d)

    print(dishsets)
    context = {
        # 'form': form,
        # 'page': page,
        # 'paginator': paginator,
        # 'query': query,
        # 'suggestion': None,
        'sets': dishsets,
    }
    return render(request, template, context)


def search_debug(request, template='search/search.html', load_all=True,
        form_class=ModelSearchForm, searchqueryset=None, extra_context=None,
        results_per_page=None):

    query = ''
    results = EmptySearchQuerySet()
    if request.GET.get('q'):
        form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)

        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
    else:
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)

    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)
    try:
        page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("No such page of results!")

    context = {
        'form': form,
        'page': page,
        'paginator': paginator,
        'query': query,
        'suggestion': None,
    }

    if results.query.backend.include_spelling:
        context['suggestion'] = form.get_suggestion()
    if extra_context:
        context.update(extra_context)
    return render(request, template, context)

def filter(request, id=0):
    ret = check_id(id)
    if (ret < 0):
        raise Http404
    dishsets = make_view(id)
    context = {'sets': dishsets, 'rank': id}
    return render(request, 'main.html', context)


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
                unit=detail.unit
                if unit:
                    uname=detail.unit.name
                    dic={'ingredient':ingredient,'amount':amount, 'unit': unit.name}
                else:
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
def add_ingredient(request, iid): #did: dish id, iid: ingredient id
    errors = []
    user = request.user
    if request.method != 'POST' or 'dishid' not in request.POST:
        return HttpResponse("")
    else:
        did = request.POST['dishid']

    userProfile = UserProfile.objects.filter(user=user)
    if len(userProfile) == 0:
        errors.append('This user does not exist')
    else:
        userProfile = UserProfile.objects.get(user=user)
    cart = Cart.objects.filter(user=userProfile)
    if cart:
        cart = Cart.objects.get(user=userProfile)
    else:
        cart = Cart(user=userProfile)
        cart.save()
    dish = get_object_or_404(Dish, id=did)
    ingredient = get_object_or_404(Ingredient, id=iid)
    dish_detail = RelationBetweenDishIngredient.objects.filter(dish=dish, ingredient=ingredient)
    ingre_amount = 0 # default
    if dish_detail:
        dish_detail = dish_detail[0]
        unit = dish_detail.unit
        rate = 1
        if unit:
            rate = dish_detail.unit.rate
        ingre_amount = rate * dish_detail.amount
    cart_detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient)
    if cart_detail:
        cart_detail = cart_detail[0]
        cart_detail.amount += ingre_amount
        cart_detail.save()
    else:
        RelationBetweenCartIngredient.objects.create(cart=cart, ingredient=ingredient, amount=ingre_amount)
    target = "/cookyourself/dish/" + str(did)
    return redirect(target)


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
        ingredient_list.append(ingredient)
        price = ingredient.price * detail.amount
        total_price += price
    total_price=float("{0:.2f}".format(total_price))
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

    return redirect(reverse('shoppinglist'))


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
        ingre['name'] = ingredient.name
        ingre['id'] = ingredient.id
        ingre_price = ingredient.price * detail.amount
        ingre['price'] = float("{0:.2f}".format(ingre_price))
        ingre['amount'] = detail.amount
        ingredient_list.append(ingre)
        price = ingredient.price * detail.amount
        total_price += price
    total_price=float("{0:.2f}".format(total_price))
    context = {
        "ingredients": ingredient_list,
        "price": total_price,
    }
    return HttpResponse(json.dumps(context), content_type='application/json')

@login_required
def print_list(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="shoppinglist.pdf"'

    if False:
        products = [('name', 10) for i in range(10)]

    products = []
    userProfile = UserProfile.objects.get(user=request.user)
    cart = userProfile.cart
    rel = RelationBetweenCartIngredient.objects.filter(cart=cart).select_related()
    for r in rel:
        rate = r.unit.rate if r.unit else 1.0
        if rate != 1:
            raise ValueError(str(r))
        products.append((r.ingredient.name, r.ingredient.price*r.amount*rate))

    pdfgen.gen_shoplist_pdf(response, products)
    return response

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
