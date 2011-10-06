from django import forms
from jewelry_retail.data_storage.models import JewelryType, Gem

CHOICES_J_TYPE = [("all", "Любой"), ("suite", "Гарнитур")]
for j_type in JewelryType.objects.all():
    CHOICES_J_TYPE.append((j_type.name_eng, j_type.name))

CHOICES_GEM = [("all", "Любая")]
for gem in Gem.objects.all():
    CHOICES_GEM.append((gem.id, gem.name))

class JRAdvancedSearchForm(forms.Form):
    j_type = forms.ChoiceField(choices=CHOICES_J_TYPE)
    gem = forms.ChoiceField(choices=CHOICES_GEM)
    price_min = forms.IntegerField(min_value=0, required=False)
    price_max = forms.IntegerField(min_value=0, required=False)
    gender = forms.CharField()

    def clean_gender(self):
        cl_data = self.cleaned_data['gender']
        if cl_data not in ['M', 'F', 'C', 'U']:
            raise forms.ValidationError(u'Неверный выбор пола')
        return cl_data

    def clean(self):
        if not self.cleaned_data.get('price_min'): self.cleaned_data['price_min'] = 0
        price_min=self.cleaned_data['price_min']
        price_max=self.cleaned_data.get('price_max')

        if price_max and (price_min > price_max):
            raise forms.ValidationError(u'Минимальная цена больше максимальной')
        return self.cleaned_data

