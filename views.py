from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from jewelry_retail.data_storage.models import JewelryType, Article, SpecificGem, Gem, Suite
from jewelry_retail.forms import JRAdvancedSearchForm


def mainpage(request):

    search_results = Article.objects.order_by('-date_on_sale')[0:10]
    search_pages = Paginator(search_results, 10)
    page = request.GET.get('page', 1)
    try:
        search_results_paginated = search_pages.page(page)
    except PageNotAnInteger:
        search_results_paginated = search_pages.page(1)
    except EmptyPage:
        search_results_paginated = search_pages.page(search_pages.num_pages)

    return render_to_response("jr_mainpage.html", {'results': search_results_paginated})

def catalogue(request):
    return render_to_response("jr_catalogue.html")

def catalogue_view(request, j_type, j_id=None):

    # Check if url contains proper english alias for jewelry type
    # SANITIZATION!
    if j_type <> u'suites': j_type = JewelryType.objects.get(name_eng=j_type[0:-1])
    if not j_type: return HttpResponseRedirect("/catalogue/")

    if j_id:

        if j_type == u'suites': 
            item = Suite.objects.get(id=j_id)
            j_type_eng = u'suite'
        else: 
            item = Article.objects.get(id=j_id)
            j_type_eng = j_type.name_eng
        return render_to_response("jr_catalogue_id.html", {"item": item, 'j_type_eng': j_type_eng})

    else:

        if j_type == u'suites': 
            search_results = Suite.objects.all()
            j_type_eng = u'suite'
        else: 
            search_results = Article.objects.filter(j_type=j_type)
            j_type_eng = j_type.name_eng
        search_pages = Paginator(search_results, 10)
        page = request.GET.get('page', 1)
        try:
            search_results_paginated = search_pages.page(page)
        except PageNotAnInteger:
            search_results_paginated = search_pages.page(1)
        except EmptyPage:
            search_results_paginated = search_pages.page(search_pages.num_pages)

        return render_to_response('jr_search_results.html', {'results': search_results_paginated, 'j_type_eng': j_type_eng})


def catalogue_search(request):

    if request.method == "GET" and request.GET:
        form = JRAdvancedSearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            price_min = cd.get('price_min')
            price_max = cd.get('price_max')
            gem = cd.get('gem')

            if not price_min: price_min = 0
            search_results = Article.objects.filter(j_type=cd['j_type'], price__gte=price_min)

            if price_max: search_results = search_results.filter(price__lte=price_max)

            gem_filter = SpecificGem.objects.filter(gem=Gem.objects.get(name=gem)).values('article').query
            search_results = search_results.filter(id__in=gem_filter)

            search_pages = Paginator(search_results, 10)
            page = request.GET.get('page', 1)
            try:
                search_results_paginated = search_pages.page(page)
            except PageNotAnInteger:
                search_results_paginated = search_pages.page(1)
            except EmptyPage:
                search_results_paginated = search_pages.page(search_pages.num_pages)

            return render_to_response('jr_search_results.html', {'results': search_results_paginated})
        else:
            return render_to_response('jr_search_form.html', {'form': form})
    form = JRAdvancedSearchForm()
    return render_to_response('jr_search_form.html', {'form': form})

