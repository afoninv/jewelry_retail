from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
import re

from jewelry_retail.data_storage.models import Supplier, Gem, Metal, Article, SpecificGem, Suite, JewelryType, JewelryModel, Collection, create_article_code, change_article_code_gem, change_article_code_model, change_article_code_type

class JRSuiteCustomAdminForm(forms.ModelForm):
    class Meta:
        model = Suite

    def clean_gender(self):
        return self.instance.gender

    def clean(self):
        super(JRSuiteCustomAdminForm, self).clean()

        # Can not validate relationships that do not exist in db: raise error if trying to submit form with articles added for nonexistant suite
        if (not self.instance.pk):
            if self.cleaned_data['articles']:
                raise ValidationError(u'Создайте сначала пустой гарнитур. Затем вы сможете отредактировать / добавить в него изделия.')
            else: return self.cleaned_data

        articles_to_add_bound, articles_to_add_unbound = [], []
        articles_to_delete = list(self.instance.articles.order_by('id'))
        for article in self.cleaned_data['articles']:
            if article in articles_to_delete: 
                articles_to_delete.remove(article)
            else:
                if article.model: articles_to_add_bound.append(article)
                else: articles_to_add_unbound.append(article)

        inherit, gender, metal, supplier = None, None, None, None
        if (not self.instance.model) or articles_to_delete == list(self.instance.articles.order_by('id')):
            # Look from whom to inherit model...
            for article in articles_to_add_bound:
                inherit, gender, metal, supplier = article.model, article.gender, article.metal, article.supplier
                break
            if not inherit:
                for article in articles_to_add_unbound:
                    inherit, gender, metal, supplier = article.initial_model, article.gender, article.metal, article.supplier
                    break
        else:
            # ...or inherit from self.
            inherit, gender, metal, supplier = self.instance.model, self.instance.gender, self.instance.metal, self.instance.supplier

        for article in articles_to_add_bound:
            if article.model <> inherit: 
                raise ValidationError(u'Выбранные изделия принадлежат к разным модельным рядам - нельзя включить все из них в один гарнитур.')

        for article in articles_to_add_unbound:
            if article.gender <> gender or article.metal <> metal or article.supplier <> supplier:
                raise ValidationError(u'Свойства \'Пол\', \'Металл\' или \'Поставщик\' выбранных изделий конфликтуют - нельзя включить все из них в один гарнитур.')

        # Inherit or set to None
        self.instance.model, self.instance.gender, self.instance.metal, self.instance.supplier = inherit, gender, metal, supplier
        create_article_code(self.instance)
        self.instance.save()

        for article in articles_to_add_unbound:
            article.model = inherit
            create_article_code(article)
            article.save()

        # Unbinding those articles that were members of current suite only
        for article in articles_to_delete:
            if article.suite_set.count() == 1: 
                article.model = None
                create_article_code(article)
                article.save()

        return self.cleaned_data


class JRArticleCustomAdminForm(forms.ModelForm):
    class Meta:
        model = Article

    def clean(self):
        super(JRArticleCustomAdminForm, self).clean()
        return self.cleaned_data

class SpecificGemInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super(SpecificGemInlineFormset, self).clean()

        # get forms that actually have valid data
        cl_list = []
        for form in self.forms:
            try:
                if form.cleaned_data:
                    cl_list.append(form.cleaned_data)
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass

        change_article_code_gem(self.instance, cl_list)

        return None

class SpecificGemInline(admin.TabularInline):
    formset = SpecificGemInlineFormset
    model = SpecificGem
    extra = 1

class SuiteInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super(SuiteInlineFormset, self).clean()

        try:
            # Now that's a workaround since I don't know how to check (from inline) if admin form's clean_fields() are successful
            self.instance.full_clean()
        except:
            raise ValidationError(u'Пожалуйста, исправьте ошибки выше.')
            return

        # get forms that actually have valid data
        cl_list = []
        for form in self.forms:
            try:
                if form.cleaned_data:
                    cl_list.append(form.cleaned_data)
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        
        # Check what to add and what to delete, plus check conflicts among to_add'ers
        suites_to_add = []
        suites_to_delete = []
        to_bound = False
        inherit = False
        for suite in cl_list:
            if suite['DELETE']: 
                suites_to_delete.append(suite['suite'])
            else: 
                suites_to_add.append(suite['suite'])
                to_bound = True
                if suite['suite'].model: 
                    if inherit and (inherit <> suite['suite'].model):
                        raise ValidationError(u'Модели выбранных гарнитуров не совпадают - невозможно включить изделие во все из них.')
                    elif not inherit:
                        inherit = suite['suite'].model

        if not self.instance.pk:
            # Create and save JewelryModel instance for empty Article instance
            initial_model = JewelryModel(model_code=u'00000', bound=False, gender=self.instance.gender, metal=self.instance.metal, supplier=self.instance.supplier)
            initial_model.save()
            id_for_code = initial_model.pk
            initial_model.model_code = "0"*(5 - len(str(id_for_code + 100))) + str(id_for_code + 100) if len(str(id_for_code + 100)) < 5 else str(id_for_code + 100)
            initial_model.save()

            self.instance.initial_model = initial_model
            self.instance.model = None

        if (not inherit) and to_bound: inherit = self.instance.initial_model
        if inherit:
            self.instance.model = inherit
            for suite in suites_to_add:
                if not suite.model:
                    suite.model, suite.gender, suite.metal, suite.supplier = self.instance.model, self.instance.gender, self.instance.metal, self.instance.supplier
                    create_article_code(suite)
                    suite.save()
        else: 
            self.instance.model = None

        change_article_code_model(self.instance)
        change_article_code_type(self.instance)

        for suite in suites_to_delete:
            # Unbind suites with 'DELETE' that contain only the current article instance
            if suite.articles.count() == 1 and suite.articles.get() == self.instance: 
                suite.model, suite.gender, suite.metal, suite.supplier = None, None, None, None
                suite.article_code = u'Г-00-00000'
                suite.save()

        return None


class SuiteInline(admin.TabularInline):
    formset = SuiteInlineFormset
    model = Suite.articles.through
    extra = 1
    verbose_name = u'Гарнитур'
    verbose_name_plural = u'Гарнитуры'

class CollectionInline(admin.TabularInline):
    model = Collection.articles.through
    extra = 1
    verbose_name = u'Коллекция'
    verbose_name_plural = u'Коллекции'

"""
Won't work - SimpleListFilter is in Django dev version, can't import def lookups(self, request, model_admin):

class SpecificGemListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = u'Камень'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'decade'


        
        #Returns a list of tuples. The first element in each
        #tuple is the coded value for the option that will
        #appear in the URL query. The second element is the
        #human-readable name for the option that will appear
        #in the right sidebar.
        to_return = []
        gems = Gem.objects.order_by('name')
        for gem in gems:
            to_return.append((gem.id, gem.name))
        return to_return

    def queryset(self, request, queryset):
        
        #Returns the filtered queryset based on the value
        #provided in the query string and retrievable via
        #`self.value()`.
        
        # Compare the requested value
        # to decide how to filter the queryset.
        gem_id_to_lookup = self.value()
        inner_queryset = SpecificGem.objects.filter(gem=gem_id_to_lookup).values('article')
        return queryset.filter(id__in=inner_queryset)
"""

class ArticleAdmin(admin.ModelAdmin):
    form = JRArticleCustomAdminForm
    inlines = (SpecificGemInline, SuiteInline, CollectionInline, )
    list_display = ('article_code', 'name', 'j_type', 'gender', 'metal', 'specificgem', 'suite', 'collection', 'date_on_sale', 'price')
        #'specificgem', 'collection' and 'suite' above (attributes of this admin model) execute separate SQL statements for each row. Consider removing in case of performance isues
    list_display_links = ('article_code', 'name', 'j_type')
    ordering = ('date_on_sale',)
    list_filter = ('j_type', 'gender', 'metal')
    search_fields = ('article_code', 'name')
    fieldsets = (
        (None, {
            'fields': (('name', 'article_code'), ('j_type', 'gender', 'metal'), ('price', 'supplier', 'date_on_sale'), 'site_description', 'notes', 'image_one', 'image_two', 'image_three')
        }),
    )
    readonly_fields = ('article_code', )


    def specificgem(self, obj):
        s = []
        spec_gems = SpecificGem.objects.filter(article=obj.id).order_by('-major', '-size')
        for spec_gem in spec_gems:
            gem_props = []
            if spec_gem.size: gem_props.append(u'%iк' % (spec_gem.size)) 
            if spec_gem.quantity <> 1: gem_props.append(u'x%s' % (spec_gem.quantity))
            spec_gem_string = u'%s (%s)' % (spec_gem.gem, u' '.join(gem_props)) if gem_props else u'%s' % (spec_gem.gem)
            s.append(spec_gem_string)
        return u"; ".join(s)

    def suite(self, obj):
        s = []
        for i in obj.suite_set.all():
            s.append(i.name)
        return u"; ".join(s)

    def collection(self, obj):
        s = []
        for i in obj.collection_set.all():
            s.append(i.name)
        return u"; ".join(s)

class SuiteAdmin(admin.ModelAdmin):
    form = JRSuiteCustomAdminForm
    fields = ('name', 'article_code', 'articles', 'gender', 'metal', 'price', 'date_on_sale', 'supplier', 'site_description', 'notes', 'image_one')
    filter_horizontal = ('articles',)
    readonly_fields = ('gender', 'metal', 'model', 'supplier', 'article_code')

class JewelryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_eng', 'j_type_code')


admin.site.register(Supplier)
admin.site.register(Gem)
admin.site.register(Metal)
admin.site.register(Collection)
admin.site.register(JewelryType, JewelryTypeAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Suite, SuiteAdmin)