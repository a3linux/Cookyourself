import re
import requests
from bs4 import BeautifulSoup

from cookyourself.models import Unit

BASE_URL = 'http://www.convertunits.com/'
reg0 = r"^if \(unit1\.value\*([0-9\.]+)"


# the returned result equals num of unit1 in unit2
def convert(unit1, unit2, num):
    r = requests.get(BASE_URL+'from/'+unit1+'/to/'+unit2)
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
    pattern = re.compile(reg0)
    m = pattern.match(constant)
    if m:
        factor = float(m.group(1))
        return num*factor
    return None


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
