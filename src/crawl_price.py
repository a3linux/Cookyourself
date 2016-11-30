import time
import traceback

from cookyourself.amazon import *
from cookyourself.myutil import *
from cookyourself.parser import PriceParser

from cookyourself.models import Ingredient


# unit to grams
unit = dict()
unit['oz'] = 28.3495
unit['lb'] = 453.592

amazon = AmazonProductAPI()
parser = PriceParser()

ingreds = Ingredient.objects.all()
for ingred in ingreds:
    query = ingred.name
    if '(' in query:
        query = query.split('(')[0]

    if ingred.price:
        continue

    while query:
        time.sleep(1)
        try:
            soup = BeautifulSoup(amazon.search(query), 'html.parser')

            products = [item.text for item in soup.select('itemattributes title')]
            urls = [item.text for item in soup.select('item detailpageurl')]
            prices = [to_float(item.text.replace('$','')) for item in soup.select('offersummary formattedprice')]
        except Exception as e:
            print(e)
            continue

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
            except Exception as e:
                print(e)
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
