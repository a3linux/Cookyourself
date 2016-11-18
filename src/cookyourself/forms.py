from django import forms
from django.forms import ModelForm
from cookyourself.models import *
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
	content=forms.CharField(label='', widget=forms.Textarea(
			    attrs={ 'name': "item", 
			            'style':"resize: none",
			            'rows':"3", 
			            'cols':"45%",
			            'id':'post-content', 
			            'required': True, 
			            'placeholder': "How do you like the recipe?"}))
	class Meta:	
		model=Post
		fields=('content', 'dish')
		widgets={'dish': forms.HiddenInput(attrs={'id':'post-dish'})}

	def createPostForm(init):
		return PostForm(initial=init, auto_id=False);

