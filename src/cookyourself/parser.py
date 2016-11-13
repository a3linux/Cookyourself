import re

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

input_strs = ['Betty Crocker Cream Cheese Frosting 16oz',
             'Knorr Pasta Sides Alfredo 4.4oz',
             'Kraft Easy Mac Original - 2.05 oz',
             'Combos Snacks, 6.3 OZ',
             "Kay's Naturals Protein Puffs 1.2 OZ, 6CT",]

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

class PriceParser:
    reg0 = r"(.*?)[-, ]+([0-9\.]+) ?[oO][zZ]"
    # reg1 = r"([^0-9]*)"

    def parse_list(self, input_strs):
        return [self.parse(input_str) for input_str in input_strs]

    def parse(self, input_str):
        pattern = re.compile(PriceParser.reg0)
        m = pattern.match(input_str)
        if m:
            return (m.group(1), float(m.group(2)))

        return (input_str, None)

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
                    ingred_set.append((m.group(3), eval(m.group(1)), m.group(2), None, None))
                    continue

            pattern = re.compile(IngredientParser.reg4)
            m = pattern.match(input_str)
            if m:
                ingred_set.append((m.group(2), eval(m.group(1)), None, None, None))
                continue

            pattern = re.compile(IngredientParser.reg5)
            m = pattern.match(input_str)
            if m:
                ingred_set.append((m.group(1), None, None, None, None))
                continue
        return ingred_set

if __name__ == '__main__':
    parser = PriceParser()
    res = parser.parse_list(input_strs)
    print(res)
