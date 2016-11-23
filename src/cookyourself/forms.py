from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from haystack.forms import SearchForm

from cookyourself.models import *

class PostForm(forms.ModelForm):
    content=forms.CharField(label='', widget=forms.Textarea(
			    attrs={ 'name': "item", 
			            'style':"resize: none",
			            'rows':"3", 
			            'cols':"40%",
			            'id':'post-content', 
			            'required': True, 
			            'placeholder': "How do you like the recipe?"}))
    class Meta:
        model=Post
        fields=('content', 'dish')
        widgets={'dish': forms.HiddenInput(attrs={'id':'post-dish'})}

    def createPostForm(init):
        return PostForm(initial=init, auto_id=False);

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

def process_raw_queries(raw):
    return raw
