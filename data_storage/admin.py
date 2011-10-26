from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
import re, datetime

from jewelry_retail.data_storage.models import Supplier, JewelryType, Gender, Gem, Metal, Article, SpecificGemArticle, Suite, SpecificGemSuite, Collection, PricingArticle, PricingSuite, Order, OrderItem

def update_suite(instance):
    price = 0
    instance.gems.clear()
    for article in instance.articles.all():
        price += article.price
        for gem in article.specificgemarticle_set.all():
            SpecificGemSuite(product=instance, gem=gem.gem, size=gem.size, quantity=gem.quantity, major=gem.major).save()
    instance.price = price
    instance.gender, instance.metal, instance.supplier = article.gender, article.metal, article.supplier
    instance.save()

    return

class ArticleCustomAdminForm(forms.ModelForm):
#
# This custom form is for validation and auto-completion, done in clean() here and save_model in ArticleAdmin
#
# For new (not-in-db-yet) article:
#     1. check if there's conflict with existing articles with the same name:
#         a. check if the type is busy 
#         b. check if gender, metal, supplier are the same
#             (the idea is, can't have two 'Napoli' rings or 'Napoli' silver ring and 'Napoli' golden bracelet)
#     2. auto-create Pricing entry if price is supplied
#         (the idea is, when we enter new article we in most cases want to price it anyway)
#     3. auto-create suite if name is not unique
#         (the idea is, one name - one suite)
#
# For existing (in-db) article:
#     1. restict price to readonly
#         (all further pricing/availability should be done externally via Pricing table and assosiated utils)
#     2. if an article is a part of a suite: restrict name, gender, j_type, metal, supplier to readonly
#         (simplest way to ensure suite integrity; all necessary validations are done via admin actions that manage suite contents)

    class Meta:
        model = Article

    def clean_price(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            price = self.instance.price
        else:
            price = self.cleaned_data.get('price') or 0
        return price

    def clean(self):
        super(ArticleCustomAdminForm, self).clean()
        cl_data = self.cleaned_data
        instance = getattr(self, 'instance', None)

        #
        # articles that are part of suite have their fields readonly anyway, so no name change - no validation needed - get out of clean()
        # else we provide instance values to form.cleaned_data, since readonly fields didn't do this for us
        #
        if instance and instance.pk and instance.part_of_suite:
            if cl_data['name'] == instance.name: 
                return cl_data
            else: 
                cl_data['j_type'], cl_data['gender'], cl_data['metal'], cl_data['supplier'] = instance.j_type, instance.gender, instance.metal, instance.supplier

        #
        # See if we have articles with the same name. If no - get out of clean()
        #
        if instance and instance.pk:
            same_name_articles = Article.objects.filter(name=cl_data['name']).exclude(id=instance.id)
        else:
            same_name_articles = Article.objects.filter(name=cl_data['name'])
        try:
            s_n_article = same_name_articles[0]
        except IndexError:
            return cl_data

        #
        # Check metal, gender, supplier to be consistent, and type to be unique across name
        #
        for article in same_name_articles:
            if cl_data.get('j_type') == article.j_type: raise ValidationError(u'%s с названием %s уже существует' % (unicode(article.j_type).capitalize(), article.name))

        errormsgs=[]
        if cl_data.get('gender') <> s_n_article.gender: errormsgs.append(u'пол \'%s\'' % (s_n_article.gender))
        if cl_data.get('metal') <> s_n_article.metal: errormsgs.append(u'металл \'%s\'' % (s_n_article.metal))
        if cl_data.get('supplier') <> s_n_article.supplier: errormsgs.append(u' поставщик \'%s\'' % (s_n_article.supplier))
        if errormsgs: raise ValidationError(u'У других изделий с названием %s: %s.' % (s_n_article.name, u', '.join(errormsgs)))

        return cl_data

class SpecificGemArticleInline(admin.TabularInline):
    model = SpecificGemArticle
    extra = 1
    # no verbose_name since it's explicitly set in SpecificGemArticle

class SpecificGemSuiteInline(admin.TabularInline):
    model = SpecificGemSuite
    extra = 1
    readonly_fields = ('gem', 'size', 'quantity', 'major')
    # no verbose_name since it's explicitly set in SpecificGemSuite

class SuiteInline(admin.TabularInline):
    model = Suite.articles.through
    extra = 1
    verbose_name = u'Гарнитур'
    verbose_name_plural = u'Гарнитуры'

class CollectionInline(admin.TabularInline):
    model = Collection.articles.through
    extra = 1
    verbose_name = u'Коллекция'
    verbose_name_plural = u'Коллекции'


class ArticleAdmin(admin.ModelAdmin):
#
# This custom model is for validation and auto-completion, done in save_model() here and clean() in ArticleCustomAdminForm
#
#
# What's important here is overriden save_model method that alone deals with article/suite relationships and sets initial pricing
#

    form = ArticleCustomAdminForm
    inlines = (SpecificGemArticleInline, )
    list_display = ('name', 'j_type', 'gender', 'metal', 'specificgemarticle', 'part_of_suite', 'collection', 'on_sale', 'price')
        #'specificgemarticle' and 'collection' above (attributes of this admin model) execute separate SQL statements for each row. Consider removing in case of performance isues
    list_display_links = ('name', 'j_type')
    ordering = ('on_sale',)
    list_filter = ('j_type', 'gender', 'metal')
    search_fields = ('name', )

    fieldsets = (
        (None, {
            'fields': (('name', 'part_of_suite'), ('j_type', 'gender', 'metal'), ('price', 'on_sale'), 'supplier', 'site_description', 'notes', ('image_one', 'image_one_thumb', 'image_two', 'image_two_thumb', 'image_three', 'image_three_thumb'))
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['on_sale', 'part_of_suite']
        if obj:
            readonly_fields.append('price')
            if obj.pk and obj.part_of_suite:
                readonly_fields += ['j_type', 'gender', 'metal', 'supplier']
        return readonly_fields

    def specificgemarticle(self, obj):
        s = []
        for spec_gem in obj.specificgemarticle_set.order_by('-major', '-size'):
            gem_props = []
            if spec_gem.size: gem_props.append(u'%iк' % (spec_gem.size)) 
            if spec_gem.quantity <> 1: gem_props.append(u'x%s' % (spec_gem.quantity))
            spec_gem_string = u'%s (%s)' % (spec_gem.gem, u' '.join(gem_props)) if gem_props else u'%s' % (spec_gem.gem)
            s.append(spec_gem_string)
        return u"; ".join(s)

    def collection(self, obj):
        s = []
        for i in obj.collection_set.all():
            s.append(i.name)
        return u"; ".join(s)

    def save_model(self, request, instance, form, change):

        if instance and instance.pk:
        #
        # Case - article exists in db. 
        #

            self_id = instance.id
            old_name = Article.objects.get(id=self_id).name
            new_name = instance.name

            if old_name == new_name:
            #
            # Case - name unchanged, so relationships unchanged. Just update suite in case gems changed.
            #
                instance.save()
                if instance.part_of_suite: update_suite(name=new_name)
                return

            else:
            #
            # Case - name changed. Update self. See if we are leaving old suite. See if we are entering new suite.
            #
                same_new_name_articles = Article.objects.filter(name=new_name)
                same_old_name_articles = Article.objects.filter(name=old_name).exclude(id=self_id)
                
                instance.part_of_suite = False
                instance.save()

                if len(same_old_name_articles) == 1:
                    same_old_name_articles[0].part_of_suite = False
                    same_old_name_articles[0].save()
                    old_suite = Suite.objects.get(name=old_name)
                    old_suite.articles.clear()
                    old_suite.pricingsuite_set.all().delete()
                    old_suite.delete()

                elif len(same_old_name_articles) > 1:
                    old_suite = Suite.objects.get(name=old_name)
                    old_suite.articles.remove(instance)
                    update_suite(old_suite)

                if len(same_new_name_articles) == 2:
                    # same_new_name_articles is reevaluated,. As we saved instance with new name, we have two articles with new name instead of one
                    new_suite = Suite(name=new_name, price=0, on_sale=False, site_description=u'')
                    new_suite.save()
                    new_suite_init_pricing = PricingSuite(product=new_suite, start_date=datetime.date.today(), amount=-5, p_type='factor')
                    new_suite_init_pricing.save()
                    for article in same_new_name_articles:
                        article.part_of_suite = True
                        article.save()
                        new_suite.articles.add(article)
                    update_suite(new_suite)



                elif len(same_new_name_articles) > 2:
                    instance.part_of_suite = True
                    instance.save()
                    new_suite = Suite.objects.get(name=new_name)
                    new_suite.articles.add(instance)
                    update_suite(new_suite)

        else:
        #
        # Case - article does not yet exist in db.
        #
            new_name = form.cleaned_data['name']
            same_new_name_articles = Article.objects.filter(name=new_name)

            if len(same_new_name_articles) == 1:
                new_suite = Suite(name=new_name, price=0, on_sale=False, site_description=u'Гарнитур %s' % (new_name))
                new_suite.save()
                new_suite_init_pricing = PricingSuite(product=new_suite, start_date=datetime.date.today(), amount=-5, p_type='factor')
                new_suite_init_pricing.save()
                instance.part_of_suite = True
                instance.save()
                new_suite.articles.add(instance)
                for article in same_new_name_articles:
                    article.part_of_suite = True
                    article.save()
                    new_suite.articles.add(article)
                update_suite(new_suite)

            elif len(same_new_name_articles) > 1:
                instance.part_of_suite = True
                instance.save()
                new_suite = Suite.objects.get(name=new_name)
                new_suite.articles.add(instance)
                update_suite(new_suite)

            else:
                instance.part_of_suite = False
                instance.save()


        #
        # Do initial pricing for article
        #

        if instance.price:
            article_init_pricing = PricingArticle(product=instance, start_date=datetime.date.today(), amount=instance.price, p_type='base')
            article_init_pricing.save()

class SuiteAdmin(admin.ModelAdmin):
    inlines = (SpecificGemSuiteInline,)
    list_display = ('name', 'gender', 'metal', 'specificgemsuite', 'on_sale', 'price')
    fieldsets = (
        (None, {
            'fields': (('name', 'articles'), ('gender', 'metal'), ('price', 'on_sale'), 'supplier', 'site_description', 'notes', ('image_one', 'image_one_thumb', 'image_two', 'image_two_thumb', 'image_three', 'image_three_thumb'))
        }),
    )
    filter_horizontal = ('articles',)
    readonly_fields = ('name', 'gender', 'metal', 'supplier', 'articles', 'price', 'on_sale')

    def specificgemsuite(self, obj):
        s = []
        for spec_gem in obj.specificgemsuite_set.order_by('-major', '-size'):
            gem_props = []
            if spec_gem.size: gem_props.append(u'%iк' % (spec_gem.size)) 
            if spec_gem.quantity <> 1: gem_props.append(u'x%s' % (spec_gem.quantity))
            spec_gem_string = u'%s (%s)' % (spec_gem.gem, u' '.join(gem_props)) if gem_props else u'%s' % (spec_gem.gem)
            s.append(spec_gem_string)
        return u"; ".join(s)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_datetime', 'is_completed', 'order_sum', 'order_items')
    list_display_links = ('id', 'order_datetime')
    list_filter = ('order_datetime', 'is_completed')
    list_editable = ('is_completed',)
    ordering = ('-order_datetime',)
    fieldsets = (
        (None, {
            'fields': (('id',), ('order_datetime', 'order_sum', 'is_completed'), ('items',), ('customer',), ('contact_name', 'contact_phone', 'delivery_address'))
        }),
    )
    filter_horizontal = ('items',)
    readonly_fields = ('id', 'order_datetime', 'order_sum', 'items', 'customer',)

    def order_items(self, obj):
        order_items = []
        for item in obj.items.all():
            order_items.append(item.__unicode__())
        return u'%i шт.: %s' % (len(order_items), u', '.join(order_items))

class CollectionAdmin(admin.ModelAdmin):
    readonly_fields = ('articles', )

admin.site.register(Supplier)
admin.site.register(Gem)
admin.site.register(Metal)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Suite, SuiteAdmin)
admin.site.register(PricingArticle)
admin.site.register(PricingSuite)
admin.site.register(Order, OrderAdmin)