from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.urls import reverse

from haystack.forms import ModelSearchForm
from haystack.query import EmptySearchQuerySet
from django.core.paginator import InvalidPage

import urllib
import json
import random
import math

from cookyourself.models import *
from cookyourself.forms import *
from cookyourself import pdfgen

GLOBAL_LOADMORE_NUM = 18
GLOBAL_FILTER_START = 5
GLOBAL_RANK_LIST_NUM = 8  # update with rank_list
RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)


def check_id(id):
    if int(id) >= GLOBAL_RANK_LIST_NUM or int(id) < 0:
        return -1
    return 0


def check_get_request(request, list):
    if request.method != 'GET':
        return -1
    for item in list:
        if item not in request.GET:
            return -1
    return 0


def check_post_request(request, list):
    if request.method != 'POST':
        return -1
    for item in list:
        if item not in request.POST:
            return -1
    return 0


def get_rank_or_filter(id):
    ret = check_id(id)
    if (ret < 0):
        return ret
    rank_list = [
        "search",
        "-popularity",  # popularity descending
        "popularity",  # popularity ascending
        "-created_on", # created_on descending
        "created_on", # created_on ascending
        "American",  # style American
        "Scottish",  # style Indian
        "Russian",  # style Russian
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


def get_dishes(cookies, id=1):
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
    default_rank_id = 1  # popularity descending
    context = {'rank': default_rank_id}
    return render(request, 'main.html', context)


def loadmore(request, id=0):
    ret = check_id(id)
    if (ret < 0):
        return redirect(reverse('error'))
    context = {}
    if int(id) != 0:
        cookies = request.COOKIES.get('dishes')  # updated in refresh.jsx, used to maintain list of showing pic
        dishsets = get_dishes(cookies, id)
    else:
        list = ['query', 'page']
        if check_get_request(request, list) < 0:
            return redirect(reverse('error'))

        query = request.GET.get('query')
        page = request.GET.get('page')
        dishsets = search(req=query, page=page)
    context['sets'] = dishsets
    return HttpResponse(json.dumps(context), content_type='application/json')


def filter(request, id=0):
    query = ''
    ret = check_id(id)
    if (ret < 0):
        return redirect(reverse('error'))
    if int(id) == 0:
        query = get_query(request)
    context = {'rank': id, 'query': query}
    return render(request, 'main.html', context)


def get_query(request, load_all=True, form_class=ModelSearchForm, searchqueryset=None):
    query = ''
    if request.GET.get('q'):
        form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)
        if form.is_valid():
            query = form.cleaned_data['q']

    return query


def search(req, load_all=True,
           form_class=ModelSearchForm, searchqueryset=None, extra_context=None,
           results_per_page=None, page=1):
    # query = ''
    results = EmptySearchQuerySet()
    dishsets = []
    buf = dict()
    buf['q'] = req
    form = form_class(buf, searchqueryset=searchqueryset, load_all=load_all)
    if form.is_valid():
        # query = form.cleaned_data['q']
        results = form.search()
    else:
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)

    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)
    try:
        page = paginator.page(int(page))
    except InvalidPage:
        # raise Http404("No such page of results!")
        return dishsets
    cnt = 0
    for result in page.object_list:
        if cnt >= GLOBAL_LOADMORE_NUM:
            break
        dish = result.object
        img = DishImage.objects.filter(dish=dish)
        if not img:
            continue

        d = dict()
        d['url'] = urllib.parse.unquote(img[0].image.url)
        d['id'] = dish.id
        d['name'] = dish.name
        dishsets.append(d)
        cnt += 1
    return dishsets


def dish(request, id=0):
    dish = Dish.objects.filter(id=id)
    if len(dish) == 0:
        return redirect(reverse('error'))
    else:
        dish = Dish.objects.get(id=id)
        image = DishImage.objects.filter(dish=dish)[0].image
        tutorial = Tutorial.objects.get(dish=dish)
        instructions = Instruction.objects.filter(tutorial=tutorial)
        ingredients = dish.ingredients.all()
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
        
        styles = []
        if dish.style:
            p_style = dish.style.parent
            while (p_style):
                styles = [p_style.name] + styles
                p_style = p_style.parent
                styles = styles[-2:]

        posts = Post.objects.filter(dish=dish)
        length = len(posts)
        saved = 0
        can_save=0
        user = request.user
        if not user.is_anonymous:
            can_save = 1
            profile = UserProfile.objects.filter(user=user)
            if profile:
                favorites = profile[0].favorites
                if favorites.filter(id=dish.id):
                    saved = 1
        star = calc_star(id)
        stars = []
        for i in range(star):
            stars.append(1)
        no_stars = []
        if star != 5:
            for i in range(5 - star):
                no_stars.append(1)

        context = {'dish': dish, 'isets': ingre_sets, 'tutorial': tutorial,
                   'image': image, 'instructions': instructions,
                   'posts': posts, 'len': length, 'styles': styles,
                   'stars': stars,  'no_stars': no_stars,
                   'saved': saved, 'can_save': can_save }

    return render(request, 'dish.html', context)


def calc_star(id):
    dish = Dish.objects.get(id=id)
    max_pop = Dish.objects.all().aggregate(Max('popularity'))['popularity__max']
    if not max_pop:
        return 0
    else:
        pop = dish.popularity
        star = math.ceil(pop / max_pop * 5)
        return star


def upvote_dish(request):
    list = ['dishid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")

    did = request.POST.get('dishid')
    dish = get_object_or_404(Dish, id=did)
    dish.popularity += 1
    dish.save()
    context = {
        "popularity": dish.popularity
    }
    return HttpResponse(json.dumps(context), content_type='application/json')


@login_required
def save_dish(request):
    list = ['dishid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    did = request.POST.get('dishid')
    dish=Dish.objects.filter(id=did)
    if len(dish)==0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    dish = Dish.objects.get(id=did)
    user = request.user
    profile = UserProfile.objects.filter(user=user)
    if len(profile) == 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    profile = UserProfile.objects.get(user=user)
    favorites = profile.favorites.all()
    if not favorites.filter(id=did):
        profile.favorites.add(dish)
        profile.save()
    return HttpResponse("")


def profile(request, id=0):
    user = User.objects.filter(id=id)
    if len(user) == 0:
        return redirect(reverse('error'))
    else:
        user_of_profile = User.objects.get(id=id)
        profile = UserProfile.objects.get(user=user_of_profile)
        favorites = profile.favorites.all()
        dishsets = []
        for dish in favorites:
            images = DishImage.objects.filter(dish=dish)
            if images:
                dic = {'dish': dish, 'image': images[0].image}
            else:
                dic = {'dish': dish}
            dishsets.append(dic)
        context = {'profile': profile, 'sets': dishsets}
    return render(request, 'profile.html', context)


@login_required
@transaction.atomic
def add_ingredient(request, iid):  # did: dish id, iid: ingredient id
    list = ['dishid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")

    user = request.user
    did = request.POST.get('dishid')
    userProfile = UserProfile.objects.get(user=user)
    cart = Cart.objects.filter(user=userProfile)
    if cart:
        cart = Cart.objects.get(user=userProfile)
    else:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    dish = get_object_or_404(Dish, id=did)
    ingredient = get_object_or_404(Ingredient, id=iid)
    dish_detail = RelationBetweenDishIngredient.objects.filter(dish=dish, ingredient=ingredient)
    ingre_amount = 0  # default
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
    return HttpResponse("")


@login_required
def shoppinglist(request):
    return render(request, 'shoppinglist.html')


@login_required
@transaction.atomic
def del_ingredient(request):
    list = ['iid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    user = request.user
    try:
        userProfile = UserProfile.objects.get(user=user)
        cart = Cart.objects.filter(user=userProfile)
        if len(cart) == 0:
            return redirect(reverse('error'))
        else:
            cart = Cart.objects.get(user=userProfile)
        iid= request.POST.get('iid')
        ingredient_to_delete = Ingredient.objects.filter(id=iid)
        if len(ingredient_to_delete)==0:
            response_data = json.dumps({"redirect": '/cookyourself/error'})
            return HttpResponse(response_data, content_type="application/json")
        ingredient_to_delete = Ingredient.objects.get(id=iid)
        cart_detail = RelationBetweenCartIngredient.objects.filter(cart=cart, ingredient=ingredient_to_delete)[0]
        cart_detail.amount = 0
        cart_detail.delete()
    except ObjectDoesNotExist:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    return HttpResponse("")


@login_required
def get_shoppinglist(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=user)
    cart = userProfile.cart
    rel = RelationBetweenCartIngredient.objects.filter(cart=cart).select_related()
    ingredient_list = []
    total_price = 0
    for r in rel:
        ingre = {}
        ingre['name'] = r.ingredient.name
        ingre['id'] = r.ingredient.id
        ingre_price = r.ingredient.price * r.amount
        ingre['price'] = float("{0:.2f}".format(ingre_price))
        ingre['amount'] = r.amount
        ingredient_list.append(ingre)
        price = r.ingredient.price * r.amount
        total_price += price
    total_price = float("{0:.2f}".format(total_price))
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
        products.append((r.ingredient.name, r.ingredient.price * r.amount * rate))

    pdfgen.gen_shoplist_pdf(response, products)
    return response


def add_user(request):
    list = ['uid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")

    uid = request.POST.get('uid')
    fuser = UserProfile.objects.filter(userid=uid)
    if not fuser:
        username = request.POST.get('username', None)
        url = request.POST.get('url', None)
        gender = request.POST.get('gender', None)
        location = request.POST.get('location', None)
        email = request.POST.get('email', None)
        new_user = User(username=username)
        if email:
            new_user.email = email
        new_user.save()
        new_user_profile = UserProfile(user=new_user, userid=uid, url=url, gender=gender, location=location)
        new_user_profile.save()
        cart = Cart(user=new_user_profile)
        cart.save()
        login(request, new_user)
    else:
        fuser = UserProfile.objects.get(userid=uid)
        user = fuser.user
        login(request, user)

    response_text = json.dumps({"usrid": request.user.id})
    return HttpResponse(response_text, content_type="application/json")


@login_required
def logout_user(request):
    logout(request)
    response_data = json.dumps({"redirect": '/cookyourself/'})
    return HttpResponse(response_data, content_type="application/json")


def create_post(request):
    response_data=''
    list = ['content', 'dish']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    content=request.POST.get('content')
    dic={'content': content}
    form = PostForm(dic)
    if form.is_valid():
        u=request.user
        content = form.cleaned_data['content']
        dishid=request.POST.get('dish')
        dish = Dish.objects.filter(id=dishid)
        if len(dish)==0:
            response_data = json.dumps({"redirect": '/cookyourself/error'})
            return HttpResponse(response_data, content_type="application/json")
        dish = Dish.objects.get(id=dishid)
        if not u.is_anonymous:
           author=UserProfile.objects.get(user=request.user)
           post = Post(dish=dish, author=author, content=content)
        else:        
           post = Post(dish=dish, content=content)
        post.save()
        response_data = json.dumps({"content": post.content})
    return HttpResponse(response_data, content_type="application/json")


def create_message(request):
    response_data=''
    list = ['content', 'ownerid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    u=request.user
    content=request.POST.get('content')
    ownerid=request.POST.get('ownerid')
    user=User.objects.filter(id=ownerid)
    if len(user)==0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    user=User.objects.get(id=ownerid)
    owner=UserProfile.objects.get(user=user)
    if not u.is_anonymous:
        author=UserProfile.objects.get(user=request.user)
        message=Message(owner=owner, author=author, content=content)
    else:        
        message=Message(owner=owner, content=content)
    message.save()
    response_data = json.dumps({"content": message.content})
    return HttpResponse(response_data, content_type="application/json")


def update_posts(request):
    list = ['time', 'dishid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    max_time = Post.get_max_time()
    time = request.POST.get('time', None)
    posts = Post.get_posts(time).order_by('-created_on')
    dishid = request.POST.get('dishid', None)
    if dishid:
        dish = Dish.objects.filter(id=dishid)
        if len(dish)==0:
            response_data = json.dumps({"redirect": '/cookyourself/error'})
            return HttpResponse(response_data, content_type="application/json")
        dish = Dish.objects.get(id=dishid)
        posts = posts.filter(dish=dish)
    context = {"max_time": max_time, "posts": posts}
    return render(request, 'posts.json', context, content_type='application/json')


def update_messages(request):
    list = ['time', 'ownerid']
    if check_post_request(request, list) < 0:
        response_data = json.dumps({"redirect": '/cookyourself/error'})
        return HttpResponse(response_data, content_type="application/json")
    max_time = Message.get_max_time()
    time = request.POST.get('time', None)
    messages = Message.get_messages(time).order_by('-created_on')
    ownerid = request.POST.get('ownerid', None)
    if ownerid:
        user = User.objects.filter(id=ownerid)
        if len(user)==0:
            response_data = json.dumps({"redirect": '/cookyourself/error'})
            return HttpResponse(response_data, content_type="application/json")
        user = User.objects.get(id=ownerid)
        owner = UserProfile.objects.get(user=user)
        messages = messages.filter(owner=owner)
    context = {"max_time": max_time, "posts": messages}
    return render(request, 'posts.json', context, content_type='application/json')


def recommendation(request):
    return render(request, 'recommendation.html')


def change_recommend(request):
    num = request.POST.get('num', None)
    if not num:
        num = 3
    else:
        num=int(num)
    dishes = randomDish(num)
    dishsets = []
    for dish in dishes:
        images = DishImage.objects.filter(dish=dish)
        if images:
            dic = {'dish': dish, 'image': images[0].image}
        else:
            dic = {'dish': dish}
        dishsets.append(dic)
    context = {'sets': dishsets}
    return render(request, 'recommends.json', context, content_type='application/json')


def randomDish(num):
    last = Dish.objects.count() - 1
    part = int(last / num) - 1
    indexes = []
    for i in range(num):
        index = random.randint(i * part, (i + 1) * part)
        indexes.append(index)
    dishes = []
    for index in indexes:
        dishes.append(Dish.objects.all()[index])
    return dishes


# error page
def error(request):
    return render(request, 'error.html')
