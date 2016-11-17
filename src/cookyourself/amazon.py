import os, sys
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# AWS API credentials
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
ASSOCIATE_TAG = os.environ['AWS_ASSOCIATE_TAG']

class AmazonProductAPI:

    def __init__(self):
        # UTC format example: 2014-08-18T12:00:00Z
        self.timestamp = (str(datetime.utcnow().isoformat()).split('.')[0]+'Z').replace(':', '%3A')

    # Helper functions
    def aws_gen_sorted_param_str(self, param_pair):
        return "&".join(sorted(param_pair))

    def aws_gen_str_to_sign(self, sorted_param_str):
        # generate string to be signed
        return """GET
webservices.amazon.com
/onca/xml
{}""".format(sorted_param_str)

    def aws_gen_signature(self,input_str):
        dig = hmac.new(AWS_SECRET_KEY.encode('utf-8'),
                       msg=input_str.encode('utf-8'),
                       digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def aws_gen_signed_request(self, sorted_param_str, signature):
        return 'http://webservices.amazon.com/onca/xml?' + sorted_param_str + '&Signature=' + signature.replace('+', '%2B').replace('=', '%3D')

    def aws_param_pair_to_signed_request(self, param_pair):
        sorted_param_str = self.aws_gen_sorted_param_str(param_pair)
        string_to_sign = self.aws_gen_str_to_sign(sorted_param_str)
        signature = self.aws_gen_signature(string_to_sign)
        return self.aws_gen_signed_request(sorted_param_str, signature)

    def aws_item_lookup(self, keyword=None):
        if not keyword:
            return None

        param_pair = [
            'Service=AWSECommerceService',
            'AWSAccessKeyId={}'.format(AWS_ACCESS_KEY_ID),
            'AssociateTag={}'.format(ASSOCIATE_TAG),
            'Operation=ItemLookup',
            'ItemId=0679722769',
            'ResponseGroup=Images%2CItemAttributes%2COffers%2CReviews',
            'Version=2013-08-01',
            'Timestamp={}'.format(self.timestamp),
        ]
        signed_request = self.aws_param_pair_to_signed_request(param_pair);
        r = requests.get(signed_request)
        return r.text

    def search(self, keyword=None):
        if not keyword:
            return None

        param_pair = [
            'Service=AWSECommerceService',
            'AWSAccessKeyId={}'.format(AWS_ACCESS_KEY_ID),
            'AssociateTag={}'.format(ASSOCIATE_TAG),
            'Operation=ItemSearch',
            'SearchIndex=GourmetFood',
            'Keywords={}'.format(keyword.replace(' ', '%20')),
            'ResponseGroup=Images%2CItemAttributes%2COffers',
            'Version=2013-08-01',
            'Timestamp={}'.format(self.timestamp),
        ]
        signed_request = self.aws_param_pair_to_signed_request(param_pair);
        r = requests.get(signed_request)
        return r.text

if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     print('Usage:')
    #     print('    python amazon.py item_name')
    #     sys.exit(0)
    #
    # query = ' '.join(sys.argv[1:])

    query = 'curry'
    amazon = AmazonProductAPI()
    soup = BeautifulSoup(amazon.search(query), 'html.parser')

    products = [item.text for item in soup.select('itemattributes title')]
    urls = [item.text for item in soup.select('item detailpageurl')]
    sizes = [item.text for item in soup.select('itemattributes size')]
    prices = [float(item.text.replace('$','')) for item in soup.select('offersummary formattedprice')]

    results = list(zip(products, sizes, prices))

    displays = ["{}: {}, {}".format(result[0], result[1], result[2]) for result in results]
    print("Keyword: {}\n".format(query) + "\n".join(displays) + "\n")
