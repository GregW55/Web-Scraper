from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='Search for a product', max_length=255)