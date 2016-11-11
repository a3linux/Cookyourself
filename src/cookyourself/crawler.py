import requests
from bs4 import BeautifulSoup
from .parser import IngredientParser

DEBUG = False

# helper functions
def is_all_caps(input_str):
    return input_str == input_str.upper()

class AllRecipeCrawler:
    base_url = 'http://allrecipes.com/recipe/'

    def __init__(self):
        self.ing_parser = IngredientParser()

    def get_soup_text(self, soup, tag):
        tmp = soup.select(tag)
        return tmp[0].text.strip() if tmp else None

    def get_soup_attr(self, soup, tag, attr):
        tmp = soup.select(tag)
        return tmp[0].attrs.get(attr) if tmp else None

    def get_soup_list(self, soup, tag):
        tmp = soup.select(tag)
        return [a.text.strip() for a in tmp] if tmp else None

    def get_soup_first_child_text(self, soup, tag, child_tag):
        tmp = soup.select(tag + " > " + child_tag)
        return tmp[0].text.strip() if tmp else None

    def get_recipe_by_id(self, id):
        info = {}

        if not isinstance(id, int):
            return info
        url = AllRecipeCrawler.base_url + str(id)
        r = requests.get(url)
        if r.status_code != 200:
            return info

        soup = BeautifulSoup(r.text, "html.parser")

        des = self.get_soup_attr(soup, 'meta#metaDescription', 'content')
        name = self.get_soup_text(soup, 'h1.recipe-summary__h1')
        img = self.get_soup_attr(soup, 'img.rec-photo', 'src')

        # remove illustration after ',', remove categories, remove the last three non-ingredient items
        ingreds = self.ing_parser.parse([ingred.split(',')[0]
                    for ingred in self.get_soup_list(soup, 'span.recipe-ingred_txt')[:-3]
                    if not is_all_caps(ingred)])

        # remove empty instructions
        instrs = list(filter(None, self.get_soup_list(soup, 'span.recipe-directions__list--item')))
        styles = self.get_soup_list(soup, 'span.toggle-similar__title')[2:]
        prept = self.get_soup_attr(soup, 'time[itemprop="prepTime"]', 'datetime')
        cookt = self.get_soup_attr(soup, 'time[itemprop="cookTime"]', 'datetime')
        totalt = self.get_soup_attr(soup, 'time[itemprop="totalTime"]', 'datetime')
        cal = self.get_soup_first_child_text(soup, 'span[class="calorie-count"]', 'span')
        servings = self.get_soup_attr(soup, 'meta#metaRecipeServings', 'content')

        info['name'] = name
        info['description'] = des
        info['img'] = img
        info['styles'] = styles
        info['ingredients'] = ingreds
        info['instructions'] = instrs
        info['calories'] = cal
        info['prep_time'] = prept
        info['cook_time'] = cookt
        info['total_time'] = totalt
        info['servings'] = servings

        if DEBUG:
            print('=============================================================')
            print('ID: {:d}'.format(id))
            print('Name: {0}\nDes: {1}\nImg: {2}'.format(name, des, img))
            print('Ingreds: ' + str(ingreds))
            print('Instrs: ' + str(instrs))
            print('Styles: ' + str(styles))
            print('Prep: {0}\nCook: {1}\nTotal: {2}'.format(prept, cookt, totalt))
            print('Calorie: ' + str(cal))
            print('Servings: ' + str(servings))

        return info

if __name__ == '__main__':
    # for debug
    DEBUG = True
    crawler = AllRecipeCrawler()
    crawler.get_recipe_by_id(10000)
