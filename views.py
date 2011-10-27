from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext

from jewelry_retail.data_storage.models import JewelryType, Article, SpecificGemArticle, SpecificGemSuite, Gem, Suite, Gender
from jewelry_retail.forms import JRAdvancedSearchForm, JRIdSuiteForm, JRIdArticleForm
from jewelry_retail.jr_cart.views import cart_add_suite, cart_add_article

def empty(request):

#    form = JRAdvancedSearchForm()
    return render_to_response("jr_base.html", context_instance=RequestContext(request))


def mainpage(request):

    search_results = Article.objects.order_by('-on_sale')[0:10]
    search_pages = Paginator(search_results, 10)
    page = request.GET.get('page', 1)
    try:
        search_results_paginated = search_pages.page(page)
    except PageNotAnInteger:
        search_results_paginated = search_pages.page(1)
    except EmptyPage:
        search_results_paginated = search_pages.page(search_pages.num_pages)

    return render_to_response("jr_mainpage.html", {'results': search_results_paginated}, context_instance=RequestContext(request))

def catalogue(request):
    return render_to_response("jr_catalogue.html", context_instance=RequestContext(request))

def catalogue_view(request, j_type, j_id=None):

    if j_type <> u'suites': 
        try:
            j_type = JewelryType.objects.get(name_eng=j_type[0:-1])
        except JewelryType.DoesNotExist:
            return HttpResponseRedirect("/")

    search_results = Suite.objects.all() if j_type == u'suites' else Article.objects.filter(j_type=j_type)

    search_pages = Paginator(search_results, 10)
    page = request.GET.get('page', 1)
    try:
        search_results_paginated = search_pages.page(page)
    except PageNotAnInteger:
        search_results_paginated = search_pages.page(1)
    except EmptyPage:
        search_results_paginated = search_pages.page(search_pages.num_pages)

    return render_to_response('jr_search_results.html', {'results': search_results_paginated}, context_instance=RequestContext(request))

def id_suite_view(request, j_id=0):

    try:
        item = Suite.objects.get(id=j_id)
    except (Suite.DoesNotExist):
        return HttpResponseRedirect("/catalogue/suites/")

    if request.method == "POST" and request.POST:
        form = JRIdSuiteForm(item.articles.all(), request.POST)
        if form.is_valid():
            cart_add_suite(request=request, form=form, item=item)
            return HttpResponseRedirect("/cart/")

        else:
        # form not valid; redraw
            return render_to_response('jr_catalogue_id_suite.html', {"item": item, 'form': form}, context_instance=RequestContext(request))

    form = JRIdSuiteForm(item.articles.all())
    return render_to_response("jr_catalogue_id_suite.html", {"item": item, 'form': form}, context_instance=RequestContext(request))


def id_article_view(request, j_type, j_id=0):

    try:
        j_type = JewelryType.objects.get(name_eng=j_type)
    except JewelryType.DoesNotExist:
        return HttpResponseRedirect("/")

    try:
        item = Article.objects.get(id=j_id, j_type=j_type)
    except (Article.DoesNotExist):
        return HttpResponseRedirect("/catalogue/%ss" % j_type.name_eng)


    if request.method == "POST" and request.POST:
        form = JRIdArticleForm(request.POST)
        if form.is_valid():
            cart_add_article(request=request, form=form, item=item)
            return HttpResponseRedirect("/cart/")

        else:
        # form not valid; redraw
            return render_to_response('jr_catalogue_id_article.html', {"item": item, 'form': form}, context_instance=RequestContext(request))

    form = JRIdArticleForm()
    return render_to_response("jr_catalogue_id_article.html", {"item": item, 'form': form}, context_instance=RequestContext(request))


def catalogue_search(request):

    if request.method == "GET" and request.GET:
        s_form = JRAdvancedSearchForm(request.GET)

        if s_form.is_valid():

            cl_data = s_form.cleaned_data
            gender = Gender.objects.get(name_eng=cl_data.get('gender'))
            gem = cl_data.get('gem')

            filter_kwargs = {'price__gte': cl_data['price_min'], 'gender': gender}
            if cl_data.get('price_max'): filter_kwargs['price__lte'] = cl_data['price_max']

            #
            # different cases for articles, suites or mix; kind of creepy
            #
            if cl_data['j_type'] == 'suite':
                search_results = Suite.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGemSuite.objects.filter(gem=Gem.objects.get(name_eng=gem)).values('product').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)

            elif cl_data['j_type'] == 'all':
                search_results = Article.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGemArticle.objects.filter(gem=Gem.objects.get(name_eng=gem)).values('product').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)

                search_results2 = Suite.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGemSuite.objects.filter(gem=Gem.objects.get(name_eng=gem)).values('product').query
                    search_results2 = search_results2.filter(id__in=gem_filter)
                search_results2 = list(search_results2)

                search_results = search_results + search_results2

            else:
                j_type = JewelryType.objects.get(name_eng=cl_data['j_type'])
                filter_kwargs['j_type'] = j_type
                search_results = Article.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGemArticle.objects.filter(gem=Gem.objects.get(name_eng=gem)).values('product').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)

            # paginate whatever list we've got and render
            search_pages = Paginator(search_results, 10)
            page = request.GET.get('page', 1)
            try:
                search_results_paginated = search_pages.page(page)
            except PageNotAnInteger:
                search_results_paginated = search_pages.page(1)
            except EmptyPage:
                search_results_paginated = search_pages.page(search_pages.num_pages)

            return render_to_response('jr_search_results.html', {'results': search_results_paginated}, context_instance=RequestContext(request))

        else:
        # form not valid; redraw
            return render_to_response('jr_search_results.html', {'results': None}, context_instance=RequestContext(request))

    return HttpResponseRedirect("/")

