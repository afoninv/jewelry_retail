from jewelry_retail.forms import JRAdvancedSearchForm

def search_form_context(request):
    if request.method == "GET" and request.GET:
        s_form = JRAdvancedSearchForm(request.GET)
    else:
        s_form = JRAdvancedSearchForm()

    return {'s_form': s_form}