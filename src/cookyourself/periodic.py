import os, sys
import time
import re
import requests
from bs4 import BeautifulSoup

from .models import *
from .myutil import *
from .crawler import AllRecipeCrawler
from .youtube import YoutubeAPI
from .amazon import AmazonProductAPI
from .parser import PriceParser

CRAWLER_LOG = 'crawl_recipe.log'
YT_URL = 'https://www.youtube.com/embed/'
UNIT_URL = 'http://www.convertunits.com/'
BEGINNING_INDEX_OF_RECIPE = 10000
NUM_PER_SEARCH = 100

reg = r"^if \(unit1\.value\*([0-9\.]+)"

def periodical_debug():
    print("DEBUG")

def periodical_crawler():
    print("CRAWL START!")
    # collect recipes
    recipe_crawler()
    # collect prices
    price_crawler()
    # collect unit conversion
    unit_crawler()
    print("CRAWL END!")

def unit_crawler():
    unit2 = 'g'
    num = 1
    try:
        g_object = Unit.objects.get(name='g')
    except Unit.DoesNotExist:
        print("First time creat gram unit")
        g_object = Unit.objects.create(name='g', rate=1)
        g_object.save()

    units = Unit.objects.all()
    for u in units:
        if u.rate:
            continue

        unit1 = u.name
        res = convert(unit1, unit2, 1)
        if res:
            print(str(num) + ' ' + unit1 + ' = ' + str(res) + ' ' + unit2)
            u.rate = res
            u.save()
        else:
            print('Can not convert {} to {}'.format(unit1, unit2))

def price_crawler():
    # instantiate amazon product API
    amazon = AmazonProductAPI()

    # instantiate price parser
    parser = PriceParser()

    # unit to grams
    unit = dict()
    unit['oz'] = 28.3495
    unit['lb'] = 453.592

    ingreds = Ingredient.objects.all()
    for ingred in ingreds:
        # if there is paranthesis in product name, trim characters
        # after the left paranthesis
        query = ingred.name
        if '(' in query:
            query = query.split('(')[0]
        
        if ':' in query:
            query = query.split(':')[0]

        if ingred.price:
            continue

        # if the query not found, drop words one by one from the beginning
        while query:
            time.sleep(1)
            soup = BeautifulSoup(amazon.search(query), 'html.parser')

            products = [item.text for item in soup.select('itemattributes title')]
            urls = [item.text for item in soup.select('item detailpageurl')]
            try:
                prices = [to_float(item.text.replace('$','')) for item in soup.select('offersummary formattedprice')]
            except Exception as e:
                print(e)
                continue

            # get the lowest price
            target = None
            min_ppu = 100
            results = list(zip(products, prices))
            for i, result in enumerate(results):
                name = result[0]
                price = result[1]

                # info[0]: name, info[1]: weight, info[2]:packs, info[3]: unit
                info = parser.parse(name)
                factor = 1
                if info[3] == 'oz':
                    factor = factor*unit['oz']
                if info[3] == 'lb':
                    factor = factor*unit['lb']

                if info[1]:
                    factor = factor*info[1]
                if info[2]:
                    factor = factor*info[2]

                try:
                    tmp = price/factor
                    ppu = tmp
                except TypeError as e:
                    continue

                if ppu < min_ppu:
                    min_ppu = ppu
                    target = result

            if target:
                print(query.encode('ascii', 'ignore').decode('ascii') + ": " + str(min_ppu))

                ingred.price = min_ppu
                ingred.save()
                break
            else:
                print(query.encode('ascii', 'ignore').decode('ascii') + ": price info is not found.")
                query = " ".join(query.split(' ')[1:])

def recipe_crawler():
    # instantiate the crawler for AllRecipeCrawler
    crawler = AllRecipeCrawler()
    youtube = YoutubeAPI()

    # check the crawler log for the last index it had visited
    with open(CRAWLER_LOG, 'a+') as f:
        f.seek(0)
        tmp = f.read()
    last_id = integer(tmp)+1 if tmp else BEGINNING_INDEX_OF_RECIPE

    # iterate from last_id + 1 to last_id + NUM_PER_SEARCH
    for i in range(0, NUM_PER_SEARCH):
        curr_id = last_id + i
        info = crawler.get_recipe_by_id(curr_id)
        if not info:
            continue

        # if the dish is already in database, skip it
        if Dish.objects.filter(name=info['name']).exists():
            print("Recipe: {:d} is already in database".format(curr_id))
            continue

        print("Recipe: {:d}".format(curr_id))
        dish = Dish.objects.create(name=info['name'],
                                   description=info['description'],
                                   calories=info['calories'],)

        tutorial = Tutorial.objects.create(dish=dish)
        instrs = [Instruction.objects.create(content=instr, tutorial=tutorial)
                    for instr in info['instructions']]

        # ingredient tuple (Ingredient object, amount, unit)
        ingreds = [(Ingredient.objects.create(name=ingred[0]), ingred[1], ingred[2], ingred[3], ingred[4])
                    if not Ingredient.objects.filter(name=ingred[0]).exists()
                    else (Ingredient.objects.get(name=ingred[0]), ingred[1], ingred[2], ingred[3], ingred[4])
                    for ingred in info['ingredients']]

        styles = [Style.objects.create(name=style_name)
                    if not Style.objects.filter(name=style_name).exists()
                    else Style.objects.get(name=style_name)
                    for style_name in info['styles']]

        prev_style = None
        for style in styles:
            if style.parent is None:
                style.parent = prev_style
            prev_style = style
            style.save()

        dish.style = styles[-1] if styles else None
        for ingred in ingreds:
            relation = RelationBetweenDishIngredient(dish=dish, ingredient=ingred[0])

            # ingred[3], ingred[4] is the weight of ingredients (ounce),
            # store weight information first. if there is no weight information
            # store check ordinary unit form
            if ingred[3]:
                relation.amount = ingred[3]
                if not Unit.objects.filter(name='oz').exists():
                    unit = Unit.objects.create(name='oz')
                    unit.save()
                relation.unit = Unit.objects.get(name='oz')
            else:
                # ingred[1] for amount
                if ingred[1]:
                    relation.amount = ingred[1]
                # ingred[2]
                if ingred[2]:
                    if not Unit.objects.filter(name=ingred[2]).exists():
                        unit = Unit.objects.create(name=ingred[2])
                        unit.save()
                    relation.unit = Unit.objects.get(name=ingred[2])
            ingred[0].save()
            relation.save()

        for instr in instrs:
            instr.tutorial = tutorial
            instr.save()

        video = youtube.youtube_search(dish.name)
        if video:
            tutorial.video = video
        tutorial.save()

        image = DishImage(dish=dish, image=info['img'], name=info['name'])
        image.save()

        dish.save()

    with open(CRAWLER_LOG, 'w+') as f:
        f.write(str(curr_id))

# the returned result equals num of unit1 in unit2
def convert(unit1, unit2, num):
    r = requests.get(UNIT_URL+'from/'+unit1+'/to/'+unit2)
    soup = BeautifulSoup(r.text, 'html.parser')

    checks = soup.select('font > strong')
    for check in checks:
        if check.text.strip() == 'Error:':
            return None

    res = soup.select('div#EchoTopic > script')
    tokens = res[0].text.split('\n') if res else None
    if not tokens:
        return None

    filtered = [token.strip() for token in tokens if token]
    constant = next(token for token in filtered if token.startswith('if'))
    pattern = re.compile(reg)
    m = pattern.match(constant)
    if m:
        factor = float(m.group(1))
        return num*factor
    return None
