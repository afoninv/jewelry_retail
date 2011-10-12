from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.mail import send_mail

from jewelry_retail.data_storage.models import Article, Suite
from jewelry_retail.jr_cart.forms import OrderForm

def cart(request):
    cart = request.session.get('cart') or []
    if cart:

        order_list = []  #[cart[0]]

        for item in cart[1:]:
            for orderitem in order:
                if orderitem == item:
                    orderitem.quantity += 1
                    break


    else: request.session['order_list'] = None
    return render_to_response("jr_cart.html", {'items': request.session['cart']}, context_instance=RequestContext(request))

def cart_add(request, j_type=None, j_id=None):
# do input sanitization

    if j_type == u'suite': 
        item = Suite.objects.get(id=j_id)
    else: 
        item = Article.objects.get(id=j_id)

    items = request.session.get('cart') or []
    items.append(item)
    request.session['cart'] = items
    request.session['order_list'] = None

    return HttpResponseRedirect("/cart/")

def cart_clear(request):
    request.session['cart'] = []
    request.session['order_list'] = None
    return HttpResponseRedirect("/cart/")

def cart_message(request):
    send_mail(u'Test mail (тестовое письмо)', u'Это письмо не должно было быть отправлено, где-то ошибка.', 'jewelryretail@alwaysdata.net',
    ['kudryavtsev_alex@list.ru', 'afoninv@mail.ru'], fail_silently=False)
    return HttpResponse("mail should be sent; no exceptions are raised at least")

def cart_remove(request, j_type=None, j_id=None):
# do input sanitization

    if j_type == u'suite': 
        item = Suite.objects.get(id=j_id)
    else: 
        item = Article.objects.get(id=j_id)

    items = request.session.get('cart') or []
    if item in items: 
        items.remove(item)
        request.session['cart'] = items
    request.session['order_list'] = None

    return HttpResponseRedirect("/cart/")

def cart_order(request):

    if request.method == "POST" and request.POST:
        form = OrderForm(request.POST)

        if form.is_valid():
        #
        # Here we do db inserts and mailing
        #
            if not request.session.get['cart_validated']: return HttpResponseRedirect("/cart/")

#            return render_to_response('jr_search_results.html', {'results': search_results_paginated}, context_instance=RequestContext(request))
            return HttpResponse(u'Да! Отправлено.')

        else:
            return render_to_response('jr_order_form.html', {'form': form}, context_instance=RequestContext(request))

    form = OrderForm()
    return render_to_response('jr_order_form.html', {'form': form}, context_instance=RequestContext(request))


def cart_help(request):
    return HttpResponseRedirect("/cart/")
