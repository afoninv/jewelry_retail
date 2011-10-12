from django.db import models
from django.core.exceptions import ValidationError

import re

class CustomPositiveSmallIntegerField(models.PositiveSmallIntegerField):
    def validate(self, value, model_instance):
        super(CustomPositiveSmallIntegerField, self).validate(value, model_instance)
        if value < 1: raise ValidationError(u'Убедитесь, что это значение больше ноля.')


CHOICES_ZODIAC = [
    (u"Aries", u"Овен"), 
    (u"Taurus", u"Телец"), 
    (u"Gemini", u"Близнецы"), 
    (u"Cancer", u"Рак"), 
    (u"Leo", u"Лев"), 
    (u"Virgo", u"Дева"), 
    (u"Libra", u"Весы"), 
    (u"Scorpio", u"Скорпион"), 
    (u"Sagittarius", u"Стрелец"), 
    (u"Capricorn", u"Козерог"), 
    (u"Aquarius", u"Водолей"), 
    (u"Pisces", u"Рыбы")
]

CHOICES_P_TYPE = [
    (u"base", u"Базовая цена, руб."), 
    (u"percent", u"Скидка / наценка, %"), 
    (u"absolute", u"Скидка / наценка, руб."), 
    (u"unavailable", u"Снято с продажи")
]


class Supplier(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=u'Поставщик', help_text=u'Обязательно только название, остальные поля по желанию.')
    address = models.CharField(max_length=100, blank=True, verbose_name=u'Адрес')
    phone = models.CharField(max_length=100, blank=True, verbose_name=u'Телефон')
    email = models.EmailField(blank=True, verbose_name=u'Электронная почта')
    site = models.URLField(verify_exists=False, blank=True, verbose_name=u'Сайт')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    class Meta:
        verbose_name = u'поставщик'
        verbose_name_plural = u'поставщики'

    def __unicode__(self):
        return self.name


class JewelryType(models.Model):
    name_eng = models.CharField(primary_key=True, max_length=20, verbose_name=u'Тип изделия (на английском)', help_text=u'Одно слово английскими прописными буквами в единственном числе, например, \'tieclip\'. Используется при формировании адреса в браузере, например, \'/catalogue/tieclip\'.')
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Тип изделия', help_text=u'На русском языке с маленькой буквы')

    class Meta:
        verbose_name = u'тип изделия'
        verbose_name_plural = u'типы изделий'

    def __unicode__(self):
        return self.name


class Gender(models.Model):
    name_eng = models.CharField(primary_key=True, max_length=20, verbose_name=u'Пол (на английском)', help_text=u'Одно слово английскими прописными буквами, например, \'men\'.')
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Пол', help_text=u'На русском языке с маленькой буквы')
    class Meta:
        verbose_name = u'пол'
        verbose_name_plural = u'таблица полов'

    def __unicode__(self):
        return self.name


class Gem(models.Model):
    name_eng = models.CharField(primary_key=True, max_length=20, verbose_name=u'Название (на английском)', help_text=u'Одно слово английскими прописными буквами в единственном числе, например, \'tourmaline\'.')
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Название', help_text=u'На русском языке с маленькой буквы')
    zodiac = models.CharField(max_length=11, choices=CHOICES_ZODIAC, blank=True, verbose_name=u'Знак Зодиака')
    class Meta:
        verbose_name = u'тип камня'
        verbose_name_plural = u'типы камней'

    def __unicode__(self):
        return self.name


class Metal(models.Model):
    name_eng = models.CharField(primary_key=True, max_length=20, verbose_name=u'Название (на английском)', help_text=u'Одно слово английскими прописными буквами в единственном числе, например, \'melchior\'.')
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Металл', help_text=u'На русском языке с маленькой буквы')
    zodiac = models.CharField(max_length=11, choices=CHOICES_ZODIAC, blank=True, verbose_name=u'Знак Зодиака')
    class Meta:
        verbose_name = u'металл'
        verbose_name_plural = u'металлы'

    def __unicode__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'Название')
    j_type = models.ForeignKey(JewelryType, verbose_name=u'Тип изделия')
    part_of_suite = models.BooleanField(verbose_name=u'Входит в гарнитур')

    gender = models.ForeignKey(Gender, verbose_name=u'Пол')
    gems = models.ManyToManyField(Gem, through='SpecificGemArticle', blank=True, verbose_name=u'Камни')
    metal = models.ForeignKey(Metal, verbose_name=u'Металл')

    price = models.PositiveIntegerField(verbose_name=u'Цена', blank=True)
    on_sale = models.BooleanField(verbose_name=u'В продаже')
    supplier = models.ForeignKey(Supplier, verbose_name=u'Поставщик')

    site_description = models.TextField(verbose_name=u'Описание на сайте')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    image_one = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 1')
    image_one_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 1 (маленькая)')
    image_two = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 2')
    image_two_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 2 (маленькая)')
    image_three = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 3')
    image_three_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 3 (маленькая)')

    class Meta:
        verbose_name = u'изделие'
        verbose_name_plural = u'изделия'

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.j_type)

    def gem_summary(self):
        g_list=[]
        for gem in self.specificgemarticle_set.all():
            gem_props = []
            if gem.size: gem_props.append(u'%i карат' % (gem.size)) 
            if gem.quantity <> 1: gem_props.append(u'%s шт.' % (gem.quantity))
            to_return = u'%s (%s)' % (gem.gem.name, u', '.join(gem_props)) if gem_props else u'%s' % (gem.gem.name)
            g_list.append(to_return)
        return u', '.join(g_list)

    def thumbnail(self):
        thumb_path = self.image_one_thumb.url if self.image_one_thumb else u'/images/special/placeholder1.jpg'
        return thumb_path

    def j_type_eng(self):
        return self.j_type.name_eng

    def article_code(self):
        return u'артикул'

    def get_absolute_url(self):
        return "/catalogue/%s/%i/" % (self.j_type.name_eng, self.id)


class SpecificGemArticle(models.Model):
    product = models.ForeignKey(Article, verbose_name=u'Изделие')
    gem = models.ForeignKey(Gem, verbose_name=u'Камень')
    size = CustomPositiveSmallIntegerField(blank=True, null=True, verbose_name=u'Размер (карат)')
    quantity = CustomPositiveSmallIntegerField(verbose_name=u'Количество')
    major = models.BooleanField(verbose_name=u'Основной', help_text=u'В изделии может быть несколько основных камней. При поиске по сайту приоритет отдаётся совпадениям по основным камням.')

    class Meta:
        verbose_name = u'камень'
        verbose_name_plural = u'камни'

    def __unicode__(self):
        gem_props = []
        if self.size: gem_props.append(u'%i карат' % (self.size)) 
        if self.quantity <> 1: gem_props.append(u'%s шт.' % (self.quantity))

        to_return = u'%s (%s)' % (self.gem, u', '.join(gem_props)) if gem_props else u'%s' % (self.gem)
        return to_return


class Suite(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name=u'Название')
    articles = models.ManyToManyField(Article, blank=True, verbose_name=u'Изделия')
    gender = models.ForeignKey(Gender, blank=True, null=True, verbose_name=u'Пол', help_text=u'Определяется по входящим в гарнитур артикулам. Гарнитур с артикулами, предназначенными для разных полов, не сохранится.')
    metal = models.ForeignKey(Metal, blank=True, null=True, verbose_name=u'Металл')
    gems = models.ManyToManyField(Gem, through='SpecificGemSuite', blank=True, verbose_name=u'Камни')

    price = models.PositiveIntegerField(verbose_name=u'Цена')
    on_sale = models.BooleanField(verbose_name=u'В продаже')
    supplier = models.ForeignKey(Supplier, blank=True, null=True, verbose_name=u'Поставщик')

    site_description = models.TextField(verbose_name=u'Описание на сайте')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    image_one = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 1')
    image_one_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 1 (маленькая)')
    image_two = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 2')
    image_two_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 2 (маленькая)')
    image_three = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 3')
    image_three_thumb = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография 3 (маленькая)')

    class Meta:
        verbose_name = u'гарнитур'
        verbose_name_plural = u'гарнитуры'

    def __unicode__(self):
        return u'%s (гарнитур)' % (self.name)

    def thumbnail(self):
        thumb_path = self.image_one_thumb.url if self.image_one_thumb else u'/images/special/placeholder1.jpg'
        return thumb_path

    def j_type(self):
        return u'Гарнитур'

    def j_type_eng(self):
        return u'suite'

    def article_code(self):
        return u'артикул'

    def get_absolute_url(self):
        return "/catalogue/%s/%i/" % (self.j_type_eng(), self.id)


class SpecificGemSuite(models.Model):
    product = models.ForeignKey(Suite, verbose_name=u'Гарнитур')
    gem = models.ForeignKey(Gem, verbose_name=u'Камень')
    size = CustomPositiveSmallIntegerField(blank=True, null=True, verbose_name=u'Размер (карат)')
    quantity = CustomPositiveSmallIntegerField(verbose_name=u'Количество')
    major = models.BooleanField(verbose_name=u'Основной', help_text=u'В гарнитуре может быть несколько основных камней. При поиске по сайту приоритет отдаётся совпадениям по основным камням.')

    class Meta:
        verbose_name = u'камень'
        verbose_name_plural = u'камни'

    def __unicode__(self):
        gem_props = []
        if self.size: gem_props.append(u'%i карат' % (self.size)) 
        if self.quantity <> 1: gem_props.append(u'%s шт.' % (self.quantity))

        to_return = u'%s (%s)' % (self.gem, u', '.join(gem_props)) if gem_props else u'%s' % (self.gem)
        return to_return


class Collection(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name=u'Название')
    articles = models.ManyToManyField(Article, blank=True, verbose_name=u'Изделия')
    site_description = models.TextField(verbose_name=u'Описание на сайте')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    class Meta:
        verbose_name = u'коллекция'
        verbose_name_plural = u'коллекции'

    def __unicode__(self):
        return u'%s' % (self.name)


class PricingArticle(models.Model):
    product = models.ForeignKey(Article, verbose_name=u'Изделие')
    start_date = models.DateField(verbose_name=u'Дата начала')
    end_date = models.DateField(verbose_name=u'Дата конца')
    amount = models.IntegerField(verbose_name=u'Значение')
    p_type = models.CharField(max_length=11, choices=CHOICES_P_TYPE, verbose_name=u'Тип шаблона')

    class Meta:
        verbose_name = u'ценовой шаблон изделия'
        verbose_name_plural = u'ценовые шаблоны изделий'

    def __unicode__(self):
        return u'%s' % (self.product.name)

class PricingSuite(models.Model):
    product = models.ForeignKey(Suite, verbose_name=u'Гарнитур')
    start_date = models.DateField(verbose_name=u'Дата начала')
    end_date = models.DateField(verbose_name=u'Дата конца')
    amount = models.IntegerField(verbose_name=u'Значение')
    p_type = models.CharField(max_length=11, choices=CHOICES_P_TYPE[1:4], verbose_name=u'Тип шаблона')

    class Meta:
        verbose_name = u'ценовой шаблон гарнитура'
        verbose_name_plural = u'ценовые шаблоны гарнитуров'

    def __unicode__(self):
        return u'%s' % (self.product.name)

class Customer(models.Model):
    name = models.CharField(max_length=20, verbose_name=u'Имя')

    class Meta:
        verbose_name = u'клиент'
        verbose_name_plural = u'клиенты'

    def __unicode__(self):
        return u'%s (%s)' % (self.name)


class OrderItem(models.Model):
    item_id = CustomPositiveSmallIntegerField(verbose_name=u'Код товара')
    name = models.CharField(max_length=30, verbose_name=u'Название')
    j_type = models.CharField(max_length=20, verbose_name=u'Тип')
    part_of_suite = models.ForeignKey('self', blank=True, null=True, verbose_name=u'Входит в гарнитур')
    quantity = CustomPositiveSmallIntegerField(verbose_name=u'Количество')
    price = CustomPositiveSmallIntegerField(verbose_name=u'Цена')
    gender = models.ForeignKey(Gender, verbose_name=u'Пол')
    metal = models.ForeignKey(Metal, verbose_name=u'Металл')
    gems = models.TextField(verbose_name=u'Камни')
    supplier = models.ForeignKey(Supplier, verbose_name=u'Поставщик')
    site_description = models.TextField(verbose_name=u'Описание на сайте')

    class Meta:
        verbose_name = u'товар'
        verbose_name_plural = u'товары'

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.j_type)

class Order(models.Model):
    order_datetime = models.DateTimeField(verbose_name=u'Дата и время заказа')
    order_sum = CustomPositiveSmallIntegerField(verbose_name=u'Сумма заказа')
    is_completed = models.BooleanField(verbose_name=u'Заказ выполнен')
    items = models.ManyToManyField(OrderItem, verbose_name=u'Товары')
    customer = models.ForeignKey(Customer, blank=True, null=True, verbose_name=u'Клиент')
    contact_name = models.CharField(max_length=25, verbose_name=u'Контактное имя')
    contact_phone = models.CharField(max_length=25, verbose_name=u'Контактный телефон')
    delivery_address = models.TextField(verbose_name=u'Адрес доставки')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    class Meta:
        verbose_name = u'заказ'
        verbose_name_plural = u'заказы'

    def __unicode__(self):
        return u'%s шт., %s руб (%s)' % (self.items.count(), self.order_sum, self.order_date)


