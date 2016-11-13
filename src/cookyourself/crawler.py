import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from .parser import IngredientParser, PriceParser


# helper functions
def is_all_caps(input_str):
    return input_str == input_str.upper()

def compute_match(str1, target):
    if not str1:
        return 0
    tokens = target.split(' ')
    return sum([1 if token in str1 else 0 for token in tokens])

class Crawler:
    def get_soup_text(self, soup, tag):
        tmp = soup.select(tag)
        return tmp[0].text.strip() if tmp else None

    def get_soup_attr(self, soup, tag, attr):
        tmp = soup.select(tag)
        return tmp[0].attrs.get(attr) if tmp else None

    def get_soup_list(self, soup, tag):
        return soup.select(tag)

    def get_soup_list_text(self, soup, tag):
        tmp = soup.select(tag)
        return [a.text.strip() for a in tmp] if tmp else None

    def get_soup_first_direct_child_text(self, soup, tag, child_tag):
        tmp = soup.select(tag + ' > ' + child_tag)
        return tmp[0].text.strip() if tmp else None

    def get_soup_child_list(self, soup, tag, child_tag):
        tmp = soup.select(tag + ' ' + child_tag)
        return [item.text.strip() for item in tmp]

class CVSCrawler(Crawler):
    query_url = 'http://www.cvs.com/search/N-0?pt=product&searchTerm='
    max_page = 3

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.price_parser = PriceParser()

    def search_price_by_string(self, query):
        query = query.lower()
        for i in range(CVSCrawler.max_page):
            temp = CVSCrawler.query_url + query + '&pageNum=' + str(i+1)
            r = requests.request('GET', temp)
            if r.status_code != 200:
                break;

            self.driver.get(temp)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            names = [(self.price_parser.parse(item.findChild('span').text.strip().lower())) for item in soup.select('div.plp-productGridItem .plp-productName')]
            prices = [float(item.findChild('span').text.strip().replace('$', '')) for item in soup.select('div.plp-productGridItem .plp-productPrice')]
            products = [item[0] + (item[1],) for item in list(zip(names, prices)) if query in item[0][0]]
            print(products)


class DGCrawler(Crawler):
    base_url = 'http://www.dollargeneral.com/'
    query_url = 'http://www.dollargeneral.com/catalogsearch/result/?q='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    }

    def __init__(self):
        self.price_parser = PriceParser()

    def fetch_cookie_for_first_time(self):
        r = requests.get(DGCrawler.base_url, headers=DGCrawler.headers)
        tokens = next(token for token in r.headers['Set-Cookie'].split(';') if 'visid_incap' in token)
        if not tokens:
            return None
        cookie = next(token.strip() for token in tokens.split(',') if 'visid_incap' in token)
        return cookie

    def search_price_by_string(self, query):
        if not DGCrawler.headers.get('Cookie'):
            DGCrawler.headers['Cookie'] = self.fetch_cookie_for_first_time()

        r = requests.get(DGCrawler.query_url + query,
                          headers=DGCrawler.headers)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        items = self.get_soup_list(soup, 'div.product-item-details')
        products = [(self.price_parser.parse(item.findChild('a', attrs={'class':'product-item-link'}).text.strip().lower())) +
                    (item.findChild('span', attrs={'class':'price'}).text.strip().replace('$', ''),)
                    for item in items]

        print(products)
        scores = [(compute_match(name, query.lower()), amount, price) for name, amount, price in products]
        best = sorted(scores, lambda x: x[0], reverse=True)
        return best

class AllRecipeCrawler(Crawler):
    base_url = 'http://allrecipes.com/recipe/'

    def __init__(self):
        self.ing_parser = IngredientParser()

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
        ingreds = self.ing_parser.parse_list([ingred.split(',')[0]
                    for ingred in self.get_soup_list_text(soup, 'span.recipe-ingred_txt')[:-3]
                    if not is_all_caps(ingred)])

        # remove empty instructions
        instrs = list(filter(None, self.get_soup_list_text(soup, 'span.recipe-directions__list--item')))
        styles = self.get_soup_list_text(soup, 'span.toggle-similar__title')[2:]
        prept = self.get_soup_attr(soup, 'time[itemprop="prepTime"]', 'datetime')
        cookt = self.get_soup_attr(soup, 'time[itemprop="cookTime"]', 'datetime')
        totalt = self.get_soup_attr(soup, 'time[itemprop="totalTime"]', 'datetime')
        cal = self.get_soup_first_direct_child_text(soup, 'span[class="calorie-count"]', 'span')
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

        return info

if __name__ == '__main__':
    # for debug
    DEBUG = True
    crawler = CVSCrawler()
    crawler.search_price_by_string('cheese')
