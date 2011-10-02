from django import forms
from jewelry_retail.data_storage.models import JewelryType,Gem

class JRAdvancedSearchForm(forms.Form):
    j_type = forms.ModelChoiceField(queryset=JewelryType.objects.all())
    gem = forms.ModelChoiceField(queryset=Gem.objects.all())
    price_min = forms.IntegerField(min_value=0, required=False)
    price_max = forms.IntegerField(min_value=0, required=False)


    def clean(self):
        price_min=self.cleaned_data.get('price_min', None)
        price_max=self.cleaned_data.get('price_max', None)
        if price_min and price_max and price_min > price_max:
            raise forms.ValidationError(u'Минимальная цена больше максимальной')
        return self.cleaned_data

