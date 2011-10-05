from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext

from jewelry_retail.data_storage.models import JewelryType, Article, SpecificGem, Gem, Suite, Gender
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

    return render_to_response("jr_mainpage.html", {'results': search_results_paginated}, context_instance=RequestContext(request))

def catalogue(request):
    return render_to_response("jr_catalogue.html", context_instance=RequestContext(request))

def catalogue_view(request, j_type, j_id=None):

    # Check if url contains proper english alias for jewelry type
    # SANITIZATION!
    if j_type <> u'suites': j_type = JewelryType.objects.get(name_eng=j_type[0:-1])
    if not j_type: return HttpResponseRedirect("/catalogue/")

    if j_id:

        if j_type == u'suites': 
            item = Suite.objects.get(id=j_id)
            item.j_type_eng = u'suite'
        else: 
            item = Article.objects.get(id=j_id)
            item.j_type_eng = j_type.name_eng
        return render_to_response("jr_catalogue_id.html", {"item": item}, context_instance=RequestContext(request))

    else:

        if j_type == u'suites': 
            search_results = list(Suite.objects.all())
            j_type_eng = u'suite'
            for item in search_results:
                item.j_type_eng = u'suite'
        else: 
            search_results = list(Suite.objects.all())
            search_results = Article.objects.filter(j_type=j_type)
            for item in search_results:
                item.j_type_eng = j_type.name_eng

        search_pages = Paginator(search_results, 10)
        page = request.GET.get('page', 1)
        try:
            search_results_paginated = search_pages.page(page)
        except PageNotAnInteger:
            search_results_paginated = search_pages.page(1)
        except EmptyPage:
            search_results_paginated = search_pages.page(search_pages.num_pages)

        return render_to_response('jr_search_results.html', {'results': search_results_paginated}, context_instance=RequestContext(request))


def catalogue_search(request):

    if request.method == "GET" and request.GET:
        form = JRAdvancedSearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            price_min = cd.get('price_min')
            price_max = cd.get('price_max')
            gem = cd.get('gem')
            gender = Gender.objects.get(gender_code=cd.get('gender'))
            if not price_min: price_min = 0

            if cd.get('j_type') == 'suite':
                search_results = Suite.objects.filter(price__gte=price_min, gender=gender)
                if price_max: search_results = search_results.filter(price__lte=price_max)
                search_results = list(search_results)
                if gem <> 'all': 
                    for item in search_results[:]:
                        if gem not in item.gems: search_results.remove(item)
                for item in search_results:
                    item.j_type_eng = u'suite'

            elif cd.get('j_type') == 'all':
                search_results = Article.objects.filter(price__gte=price_min, gender=gender)
                if price_max: search_results = search_results.filter(price__lte=price_max)
                if gem <> 'all': 
                    gem_filter = SpecificGem.objects.filter(gem=Gem.objects.get(id=gem)).values('article').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)
                for item in search_results:
                    item.j_type_eng = item.j_type.name_eng

                search_results2 = Suite.objects.filter(price__gte=price_min, gender=gender)
                if price_max: search_results2 = search_results2.filter(price__lte=price_max)
                search_results2 = list(search_results2)
                if gem <> 'all': 
                    for item in search_results2[:]:
                        if gem not in item.gems: search_results2.remove(item)
                for item in search_results2:
                    item.j_type_eng = u'suite'

                search_results = search_results + search_results2

            else:
                j_type= JewelryType.objects.get(name_eng=cd.get('j_type'))
                search_results = Article.objects.filter(j_type=j_type, price__gte=price_min, gender=gender)
                if price_max: search_results = search_results.filter(price__lte=price_max)
                if gem <> 'all': 
                    gem_filter = SpecificGem.objects.filter(gem=Gem.objects.get(id=gem)).values('article').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)
                for item in search_results:
                    item.j_type_eng = item.j_type.name_eng


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
            return render_to_response('jr_search_form.html', {'form': form}, context_instance=RequestContext(request))
    form = JRAdvancedSearchForm()
    return render_to_response('jr_search_form.html', {'form': form}, context_instance=RequestContext(request))

