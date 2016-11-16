import re
from .myutil import *

input_strs = ['1 (16 ounce) package egg noodles',
              '1 pound lean ground beef',
              '1 (.75 ounce) packet dry brown gravy mix',
              '1 (8 ounce) package cream cheese',
              '1 (6 ounce) can chopped mushrooms, with liquid',
              '1/2 cup milk',
              '1 (8 ounce) container sour cream',
              '2 (10.75 ounce) cans condensed cream of mushroom soup',
              '1 3/4 cups plain yogurt',
              '6 cubes ice',
              '1 1/2 cups ice water',
              '2 teaspoons white sugar',
              '1 pinch salt']

input_strs = ['VeganEgg by Follow Your Heart, 4-Ounce Carton Egg Replacer',
             "Kauffman's Hand-Picked Fresh Stayman Winesap Apples (Box of 16 Apples)",
             'Pink Lady Apples - 4 lbs - The Fruit Company',
             'Gala Apples Fresh Produce Fruit, 3 LB Bag',
             "Zatarain's New Orleans Style Mixes, Smothered Chicken Rice Mix, 8-Ounce Boxes (Pack of 12)",
             'KRAFT PHILADELPHIA CREAM CHEESE BRICK ORIGINAL 8 OZ PACK OF 4',
             'Kraft Philadelphia Cream Cheese (8 oz. pkg., 6 ct.)',
             'Kraft Philadelphia Original Cream Cheese Spread - Pouch, 1 Ounce -- 100 per case.',
             ]

def generate_unit_set():
    units = set()
    units.add('cup')
    units.add('jar')
    units.add('package')
    units.add('teaspoon')
    units.add('pound')
    units.add('packet')
    units.add('can')
    units.add('container')
    units.add('tablespoon')
    units.add('loaf')
    units.add('loaves')
    units.add('ounce')
    units.add('bottle')
    units.add('cube')
    units.add('pinch')
    return units

def convert_str_to_float(input_str):
    pass

class PriceParser:
    reg00 = r".*?[ \(]?[pP][aA][cC][kK] [oO][fF] (?P<pack>[0-9]+)\)?"
    reg01 = r".*?[ \(]?[bB][oO][xX] [oO][fF] (?P<pack>[0-9]+)"
    reg1 = r"(?P<name>.*?)[-, ]+\(?(?P<amount>[0-9\./]+) ?[oO][zZ]"
    reg2 = r"(?P<name>.*?)[-, ]+\(?(?P<amount>[0-9\./]+)[- ]?[oO][uU][nN][cC][eE]"
    reg3 = r"(?P<name>.*?)[-, ]+\(?(?P<amount>[0-9\/]+) ?[lL][bB]"
    reg4 = r"(?P<name>.*?)[-, ]+\(?(?P<amount>[0-9\./]+) ?[kK]?[gG]"

    def parse_list(self, input_strs):
        return [self.parse(input_str) for input_str in input_strs]

    def parse(self, input_str):
        pack = None
        # get pack of item first
        pattern = re.compile(PriceParser.reg00)
        m = pattern.match(input_str)
        if m:
            pack = to_float(m.group(1))

        pattern = re.compile(PriceParser.reg01)
        m = pattern.match(input_str)
        if m:
            pack = to_float(m.group(1))

        # get weight of item
        pattern = re.compile(PriceParser.reg1)
        m = pattern.match(input_str)
        unit = None
        if m:
            unit = to_float(m.group(2))
            return (m.group(1), unit, pack, 'oz')

        pattern = re.compile(PriceParser.reg2)
        m = pattern.match(input_str)
        if m:
            unit = to_float(m.group(2))
            return (m.group(1), unit, pack, 'oz')

        pattern = re.compile(PriceParser.reg3)
        m = pattern.match(input_str)
        if m:
            unit = to_float(m.group(2))
            return (m.group(1), unit, pack, 'lb')

        pattern = re.compile(PriceParser.reg4)
        m = pattern.match(input_str)
        if m:
            unit = to_float(m.group(2))
            return (m.group(1), unit, pack, 'g')

        return (input_str, None, pack, None)

class IngredientParser:
    units = generate_unit_set()
    reg0 = r"^(?P<num1>[/0-9]+) (?P<num1_1>[/0-9]+) \((?P<num2>[\.0-9]+) (?P<unit2>[^)]+)\) (?P<unit1>[a-zA-Z]+) (?P<name>.*)"
    reg1 = r"^(?P<num1>[/0-9]+) \((?P<num2>[\.0-9]+) (?P<unit2>[^)]+)\) (?P<unit1>[a-zA-Z]+) (?P<name>.*)"
    reg2 = r"^(?P<num1>[/0-9]+) (?P<num1_1>[/0-9]+) (?P<unit1>[a-zA-Z]+) (?P<name>.*)"
    reg3 = r"^(?P<num1>[/0-9]+) (?P<unit1>[a-zA-Z]+) (?P<name>.*)"
    reg4 = r"^(?P<num1>[/0-9]+) (?P<name>.*)"
    reg5 = r"^(?P<name>[^0-9]*)"

    def parse_list(self, input_strs):
        ingred_set = []
        for input_str in input_strs:
            pattern = re.compile(IngredientParser.reg0)
            m = pattern.match(input_str)
            if m:
                ingred_set.append((m.group(6), eval(m.group(1))+eval(m.group(2)), m.group(5), eval(m.group(3)), m.group(4)))
                continue

            pattern = re.compile(IngredientParser.reg1)
            m = pattern.match(input_str)
            if m:
                ingred_set.append((m.group(5), eval(m.group(1)), m.group(4), eval(m.group(2)), m.group(3)))
                continue

            # check whether there is an unit in the string
            check = sum([1 if input_str.find(unit) != -1 else 0 for unit in IngredientParser.units])
            if check != 0:
                pattern = re.compile(IngredientParser.reg2)
                m = pattern.match(input_str)
                if m:
                    ingred_set.append((m.group(4), eval(m.group(1))+eval(m.group(2)), m.group(3), None, None))
                    continue

                pattern = re.compile(IngredientParser.reg3)
                m = pattern.match(input_str)
                if m:
                    # check whether the parsed unit is what we target
                    unit = m.group(2)
                    if unit in IngredientParser.units:
                        ingred_set.append((m.group(3), eval(m.group(1)), m.group(2), None, None))
                    else:
                        ingred_set.append((m.group(3), eval(m.group(1)), None, None, None))
                    continue

            pattern = re.compile(IngredientParser.reg4)
            m = pattern.match(input_str)
            if m:
                ingred_set.append((m.group(2), eval(m.group(1)), None, None, None))
                continue

            # no unit is found
            ingred_set.append((m.group(1), None, None, None, None))

        return ingred_set

if __name__ == '__main__':
    parser = PriceParser()
    res = parser.parse_list(input_strs)
    print(res)
