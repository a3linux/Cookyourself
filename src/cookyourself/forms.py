from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from haystack.forms import SearchForm

from cookyourself.models import *

class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=('content',)


# template for customize our own search form
# ref: http://django-haystack.readthedocs.io/en/v2.4.1/views_and_forms.html
class DishSearchForm(SearchForm):
    style = forms.CharField(required=False)
    raw_queries = forms.CharField()

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(DishSearchForm, self).search()

        if not self.is_valid():
                        return self.no_query_found()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['raw_queries']:
            queries = process_raw_queries(self.cleaned_data['raw_queries'])
            sqs = sqs.filter(discription=queries)

        return sqs

class MessageForm(forms.ModelForm):
	content=forms.CharField(max_length = 200, label='')
	class Meta:	
		model=Message
		fields=('content',)

def process_raw_queries(raw):
    return raw
