from django import forms

class OrderForm(forms.Form):
    contact_name = forms.CharField(min_length=3, max_length=25)
    contact_phone = forms.CharField(min_length=7, max_length=25)
    delivery_address = forms.CharField(min_length=10, max_length=200)

#    def clean_gender(self):
#        cl_data = self.cleaned_data['gender']
#        if cl_data not in ['men', 'women', 'children', 'universal']:
#            raise forms.ValidationError(u'Неверный выбор пола')
#        return cl_data

#    def clean(self):
#        if not self.cleaned_data.get('price_min'): self.cleaned_data['price_min'] = 0
#        price_min=self.cleaned_data['price_min']
#        price_max=self.cleaned_data.get('price_max')

#        if price_max and (price_min > price_max):
#            raise forms.ValidationError(u'Минимальная цена больше максимальной')
#        return self.cleaned_data


