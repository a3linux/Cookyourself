import os
from cookyourself.crawler import AllRecipeCrawler
from cookyourself.models import *

CRAWLER_LOG = ".crawler_log"
NUM_PER_SEARCH = 100

def to_integer(s):
    try:
        res = int(s)
        return res
    except ValueError:
        return None

crawler = AllRecipeCrawler()

with open(CRAWLER_LOG, 'a+') as f:
    f.seek(0)
    last_id_str = f.read()

last_id = to_integer(last_id_str)+1 if last_id_str else 0

for i in range(0, NUM_PER_SEARCH):
    curr_id = last_id + i

    info = crawler.get_recipe_by_id(curr_id)
    if not info:
        continue

    print("Crawler: {:d}".format(curr_id))
    if not Dish.objects.filter(name=info['name']).exists():
        dish = Dish.objects.create(name=info['name'],
                description=info['description'],
                calories=info['calories'],)

        tutorial = Tutorial.objects.create(dish=dish)
        instrs = [Instruction.objects.create(content=instr, tutorial=tutorial)
                for instr in info['instructions']]

        # ingredient tuple (ingred object, amount, unit)
        ingreds = [(Ingredient.objects.create(name=ingred[0]), ingred[1], ingred[2])
                if not Ingredient.objects.filter(name=ingred[0]).exists()
                else (Ingredient.objects.get(name=ingred[0]), ingred[1], ingred[2])
                for ingred in info['ingredients']]

        styles = [Style.objects.create(name=style_name)
                if not Style.objects.filter(name=style_name).exists()
                else Style.objects.get(name=style_name)
                for style_name in info['styles']]

        prev = None
        for style in styles:
            if style.parent is None:
                style.parent = prev
            style.save()

        dish.style = styles[-1] if styles else None
        for ingred in ingreds:
            relation = RelationBetweenDishIngredient(dish=dish, ingredient=ingred[0])
            if ingred[1]:
                relation.amount = ingred[1]

                if ingred[2]:
                    if Unit.objects.filter(name=ingred[2]).exists():
                        relation.unit = Unit.objects.get(name=ingred[2])
                    elif ingred[2]:
                        relation.unit = Unit.objects.create(name=ingred[2])
                    relation.unit.save()

            ingred[0].save()
            relation.save()

        for instr in instrs:
            instr.tutorial = tutorial
            instr.save()
        tutorial.save()

        image = DishImage(dish=dish, image=info['img'], name=info['name'])
        image.save()
        dish.save()

    else:
        print(str(curr_id) + " is already in database.")


with open(CRAWLER_LOG, 'w+') as f:
    f.write(str(curr_id))
