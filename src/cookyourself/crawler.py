import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from nltk.stem.porter import *
from .parser import IngredientParser, PriceParser

# helper functions
def is_all_caps(input_str):
    return input_str == input_str.upper()

def compute_match_score(name, queries):
    # get a Porter stemmer
    stemmer = PorterStemmer()
    # remove information after periods
    name = name.split(',')[0]
    # split the name in to tokens
    name_tokens = [stemmer.stem(token) for token in name.split()]

    len_name_tokens = len(name_tokens)
    penalty = -1 if 'and' in name_tokens else 0
    score = sum([10-(len_name_tokens-name_tokens.index(q)) for q in queries if q in name_tokens])
    return score + penalty

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
    max_page = 1

    def __init__(self):
        self.driver = webdriver.PhantomJS()
        self.wait = WebDriverWait(self.driver, 10)
        self.price_parser = PriceParser()

    def search_price_by_string(self, query):
        stemmer = PorterStemmer()
        query = query.lower()
        queries = [stemmer.stem(token) for token in query.split()]

        products = []
        for i in range(CVSCrawler.max_page):
            temp = CVSCrawler.query_url + query.replace(' ', '+') + '&pageNum=' + str(i)
            r = requests.request('GET', temp)
            if r.status_code != 200:
                break;

            self.driver.get(temp)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'plp-productName')))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            names = [(self.price_parser.parse(item.findChild('span').text.strip().lower())) for item in soup.select('div.plp-productGridItem .plp-productName')]
            prices = [float(item.findChild('span').text.strip().replace('$', '')) for item in soup.select('div.plp-productGridItem .plp-productPrice')]
            new_product = [item[0] + (item[1],) for item in list(zip(names, prices))]
            products = products + new_product
            if not new_product:
                break

        max_score = -1
        target = None
        for product in products:
            score = compute_match_score(product[0], queries)
            # print(product[0] + ": " + str(score))

            if score == max_score and target[2] and product[2]:
                if product[2] < target[2]:
                    max_score = score
                    target = product
            elif score > max_score:
                max_score = score
                target = product

        print(target)
        if target == None:
            return None

        if target[1]:
            return target[2]/target[1]
        return target[2]

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
        query = query.lower()
        queries = query.split()

        if not DGCrawler.headers.get('Cookie'):
            DGCrawler.headers['Cookie'] = self.fetch_cookie_for_first_time()

        r = requests.get(DGCrawler.query_url + query, headers=DGCrawler.headers)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        items = self.get_soup_list(soup, 'div.product-item-details')
        products = [(self.price_parser.parse(item.findChild('a', attrs={'class':'product-item-link'}).text.strip().lower())) +
                    (float(item.findChild('span', attrs={'class':'price'}).text.strip().replace('$', '')),)
                    for item in items]

        max_score = -1
        target = None
        for product in products:
            score = compute_match_score(product[0], queries)
            if score > max_score:
                max_score = score
                target = product

        print(target)
        if target == None:
            return None

        if target[1]:
            return target[2]/target[1]
        return target[2]

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
        stemmer = PorterStemmer()

        des = self.get_soup_attr(soup, 'meta#metaDescription', 'content')
        name = self.get_soup_text(soup, 'h1.recipe-summary__h1')
        img = self.get_soup_attr(soup, 'img.rec-photo', 'src')
        if 'nophoto' in img:
            return info

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

# for debug
if __name__ == '__main__':
    crawler = CVSCrawler()
    price = crawler.search_price_by_string('cake')
