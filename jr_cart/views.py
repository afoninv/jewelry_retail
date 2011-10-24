from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.mail import send_mail
import datetime

from jewelry_retail.data_storage.models import Article, Suite, OrderItem, Order
from jewelry_retail.jr_cart.forms import OrderForm

def translate_to_orderitems(cart_item=None):
    #
    # Takes one Article instance or Suite instance. Returns list of OrderItem instances.
    # No special pricing here!
    # 
#    if not cart_item: return []
    
#    if cart_item.j_type_eng <> 'suite':
#        item = cart_item
#        order_items = [OrderItem(item_id=item.id, name=item.name, j_type=item.j_type, quantity=1, price=item.price, gender=item.gender, metal=item.metal, gems=u';'.join(list(item.specificgemarticle_set.all())) , supplier=item.supplier, site_description=item.site_description)]

#    else:
#        item = cart_item
#        order_items = [OrderItem(item_id=item.id, name=item.name, j_type=item.j_type(), quantity=1, price=item.price, gender=item.gender, metal=item.metal, gems=u';'.join(list(item.specificgemsuite_set.all())) , supplier=item.supplier, site_description=item.site_description)]

#        for item in cart_item.articles.all():
#            order_items.append(OrderItem(item_id=item.id, name=item.name, j_type=item.j_type, quantity=1, price=item.price, gender=item.gender, metal=item.metal, gems=u';'.join(list(item.specificgemarticle_set.all())) , supplier=item.supplier, site_description=item.site_description, part_of_suite=))

    return #what?

def cart(request):
    cart = request.session.get('cart') or []

    return render_to_response("jr_cart.html", {'items': cart}, context_instance=RequestContext(request))

def cart_add_suite(request, form, item):
    cart = request.session.get('cart') or []
    cart_sum = request.session.get('cart_sum') or 0
    cart_count = request.session.get('cart_count') or 0

    suite_price = 0
    suite_gems = []
    for article in form.cleaned_data['suite_contents']:
        suite_price += article.price
        if article.gem_summary(): suite_gems.append(article.gem_summary())
    suite_price = int(suite_price * (100.0 + item.get_factor()) / 100)
    suite = OrderItem(item_id=item.id, name=item.name, j_type=item.j_type(), quantity=1, price=suite_price, gender=item.gender, metal=item.metal, gems=u';'.join(suite_gems), supplier=item.supplier, site_description=item.site_description)
    suite.number = cart_count + 1
    cart.append(suite)

    for item in form.cleaned_data['suite_contents']:
        orderitem = OrderItem(item_id=item.id, name=item.name, j_type=item.j_type, quantity=1, price=item.price, gender=item.gender, metal=item.metal, gems=item.gem_summary(), supplier=item.supplier, site_description=item.site_description, part_of_suite=suite)
        if item.j_type_eng() == 'ring': orderitem.size = form.cleaned_data.get('size') 
        orderitem.number = suite.number
        cart.append(orderitem)

    request.session['cart'] = cart
    cart_sum += suite_price
    request.session['cart_sum'] = cart_sum
    request.session['cart_price'] = cart_sum if cart_sum < 10000 else int(cart_sum * 0.95)
    request.session['cart_count'] = cart_count + 1

    return

def cart_add_article(request, form, item):
    cart = request.session.get('cart') or []
    cart_sum = request.session.get('cart_sum') or 0
    cart_count = request.session.get('cart_count') or 0

    orderitem = OrderItem(item_id=item.id, name=item.name, j_type=item.j_type, quantity=1, price=item.price, gender=item.gender, metal=item.metal, gems=item.gem_summary(), supplier=item.supplier, site_description=item.site_description)
    if item.j_type_eng() == 'ring': orderitem.size = form.cleaned_data.get('size')
    orderitem.number = cart_count + 1
    cart.append(orderitem)

    request.session['cart'] = cart
    cart_sum += orderitem.price
    request.session['cart_sum'] = cart_sum
    request.session['cart_price'] = cart_sum if cart_sum < 10000 else int(cart_sum * 0.95)
    request.session['cart_count'] = cart_count + 1

    return

def cart_clear(request):
    request.session['cart'] = []
    request.session['cart_sum'] = 0
    request.session['cart_price'] = 0
    request.session['cart_count'] = 0

    return HttpResponseRedirect("/cart/")


def cart_remove(request, item_number = None):

    cart = request.session.get('cart') or []
    cart_sum = request.session.get('cart_sum') or 0
    cart_price = request.session.get('cart_price') or 0
    cart_count = request.session.get('cart_count') or 0

    item_number = int(item_number)
    item_to_remove = None

    to_pop = []
    for number, item in enumerate(cart):
        if item.number == item_number:
            to_pop.append(number)
            if not item.part_of_suite: item_to_remove = item

    if not item_to_remove: return HttpResponseRedirect("/cart/") 

    for i in to_pop[::-1]:
        cart.pop(i)

    for item in cart:
        if item.number > item_number: item.number -= 1

    request.session['cart'] = cart

    cart_sum -= item_to_remove.price
    request.session['cart_sum'] = cart_sum
    request.session['cart_price'] = cart_sum if cart_sum < 10000 else int(cart_sum * 0.95)
    request.session['cart_count'] = cart_count + 1

    return HttpResponseRedirect("/cart/")


def cart_order(request):

    cart = request.session.get('cart') or []
    cart_price = request.session.get('cart_price') or 0
    cart_count = request.session.get('cart_count') or 0

    if not cart: return HttpResponseRedirect("/cart/") 

    if request.method == "POST" and request.POST:
        form = OrderForm(request.POST)

        if form.is_valid():
        #
        # Here we do db inserts and mailing
        #
            cl_data = form.cleaned_data
            order = Order(order_datetime=datetime.datetime.now(), order_sum=cart_price, is_completed=False, contact_name=cl_data['contact_name'], contact_phone=cl_data['contact_phone'], delivery_address=cl_data['delivery_address'])
            order.save()

            for item in cart:
                item.save()
                order.items.add(item)
                if item.j_type == u'гарнитур':
                    suite_number = item.number
                    for article in cart:
                        if article.number == suite_number and article <> item: article.part_of_suite = item
            order.save()


            request.session['cart'] = []
            request.session['cart_price'] = 0
            request.session['cart_count'] = 0
        #
        #     send_mail(u'Заказ №%s' % (order.id), u'Здесь красивое-удобное описание заказа. А пока только сумма: %s' % (order.sum), 'jewelryretail@alwaysdata.net', ['kudryavtsev_alex@list.ru', 'afoninv@mail.ru'], fail_silently=False)
        #

            return render_to_response('jr_cart_thank_you.html', context_instance=RequestContext(request))

        else:
            return render_to_response('jr_order_form.html', {'form': form, 'items': cart}, context_instance=RequestContext(request))

    form = OrderForm()
    return render_to_response('jr_order_form.html', {'form': form, 'items': cart}, context_instance=RequestContext(request))


def cart_help(request):
    return HttpResponseRedirect("/cart/")
