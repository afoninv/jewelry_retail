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

    # j_type needs to be 'suites' or JewelryType.object.name_eng plural
    if j_type <> u'suites': 
        try:
            j_type = JewelryType.objects.get(name_eng=j_type[0:-1])
        except JewelryType.DoesNotExist:
            return HttpResponseRedirect("/")

    # render page for individual product...
    if j_id:

        try:
            item = Suite.objects.get(id=j_id) if j_type == u'suites' else Article.objects.get(id=j_id)
        except (Suite.DoesNotExist, Article.DoesNotExist):
            return HttpResponseRedirect("/")

        return render_to_response("jr_catalogue_id.html", {"item": item}, context_instance=RequestContext(request))

    # ...or for a whole j_type
    else:

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


def catalogue_search(request):

    if request.method == "GET" and request.GET:
        form = JRAdvancedSearchForm(request.GET)

        if form.is_valid():

            cl_data = form.cleaned_data
            gender = Gender.objects.get(gender_code=cl_data.get('gender'))
            gem = cl_data.get('gem')

            filter_kwargs = {'price__gte': cl_data['price_min'], 'gender': gender}
            if cl_data.get('price_max'): filter_kwargs['price__lte'] = cl_data['price_max']

            # different cases for articles, suites or mix; kind of creepy
            if cl_data['j_type'] == 'suite':
                search_results = Suite.objects.filter(**filter_kwargs)
                search_results = list(search_results)
                if gem <> 'all': 
                    for item in search_results[:]:
                        if gem not in item.gems(): search_results.remove(item)

            elif cl_data['j_type'] == 'all':
                search_results = Article.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGem.objects.filter(gem=Gem.objects.get(id=gem)).values('article').query
                    search_results = search_results.filter(id__in=gem_filter)
                search_results = list(search_results)

                search_results2 = Suite.objects.filter(**filter_kwargs)
                search_results2 = list(search_results2)
                if gem <> 'all': 
                    for item in search_results2[:]:
                        if gem not in item.gems(): search_results2.remove(item)

                search_results = search_results + search_results2

            else:
                j_type = JewelryType.objects.get(name_eng=cl_data['j_type'])
                filter_kwargs['j_type'] = j_type
                search_results = Article.objects.filter(**filter_kwargs)
                if gem <> 'all': 
                    gem_filter = SpecificGem.objects.filter(gem=Gem.objects.get(id=gem)).values('article').query
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
            return render_to_response('jr_search_form.html', {'form': form}, context_instance=RequestContext(request))

    form = JRAdvancedSearchForm()
    return render_to_response('jr_search_form.html', {'form': form}, context_instance=RequestContext(request))

