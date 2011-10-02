from django.db import models
from django.core.exceptions import ValidationError

import re

class CustomPositiveSmallIntegerField(models.PositiveSmallIntegerField):
    def validate(self, value, model_instance):
        super(CustomPositiveSmallIntegerField, self).validate(value, model_instance)
        if value < 1: raise ValidationError(u'Убедитесь, что это значение больше ноля.')

class CustomGemCode(models.CharField):
    def validate(self, value, model_instance):
        super(CustomGemCode, self).validate(value, model_instance)
        if not re.match(ur"^\d{2}$", value): raise ValidationError(u'Код камня-вставки должен состоять из двух цифр.')
        if re.match(ur"99$", value): raise ValidationError(u'Код \'99\' зарезервирован для артикулов с несколькими камнями.')
        if re.match(ur"00$", value): raise ValidationError(u'Код \'00\' зарезервирован для артикулов без камня.')

class CustomJTypeCode(models.CharField):
    def validate(self, value, model_instance):
        super(CustomJTypeCode, self).validate(value, model_instance)
        if not re.match(ur"^[A-Z\u0410-\u042f]$", value): raise ValidationError(u'Код типа изделия должен состоять из одной заглавной буквы.')


CHOICES_ZODIAC = (
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
)


def create_article_code(instance):

    #Get model code:
    # - suites w/o model have full article_code set to empty string; return.
    # - articles w/o model have their model code part set as initial_model.
    model_code = u''
    if (not instance.model):
        if type(instance) == Suite:
            instance.article_code = u'Г-00-00000'
            return
        elif type(instance) == Article:
            model_code = instance.initial_model.model_code
    else: model_code = instance.model.model_code


    #Get type code:
    # - for j_types from db table.
    # - for suites by adding number to 'Г'. Check busy numbers for this model first.
    j_type_code = u''
    if type(instance) == Article:
        j_type_code = instance.j_type.j_type_code
    elif type(instance) == Suite:
        busy_numbers=[]
        for suite in instance.model.suite_set.all():
            if suite <> instance:
                number = re.match(ur"^Г(?P<number>\d+)-", suite.article_code).group('number')
                if number: busy_numbers.append(int(number))
        if not busy_numbers: j_type_code = u'Г1'
        else:
            for candidate, number in enumerate(busy_numbers):
                if candidate + 1 <> number: 
                    j_type_code = u'Г' + unicode(candidate + 1)
                    break
            if not j_type_code: j_type_code = u'Г' + unicode(candidate + 2)

    #Get gem code. For artictes check its gems. For suites merge articles' gems.
    # - 00 for no gems
    # - 99 if several major gems OR no major gems and several minor gems
    # - db gem code if single major or no majors and single minor
    gem_code = u''
    gem_list = []

    if type(instance) == Article:
        gem_list = list(SpecificGem.objects.filter(article=instance))
    elif type(instance) == Suite:
        for article in instance.articles.all():
            if list(SpecificGem.objects.filter(article=article)): gem_list += list(SpecificGem.objects.filter(article=article))

    for gem in gem_list:
        if gem.major: 
            gem_code = u'99' if gem_code else gem.gem.gem_code
    if not gem_code:
        for gem in gem_list:
            gem_code = u'99' if gem_code else gem.gem.gem_code

    if not gem_code: gem_code = u'00'

    article_code = j_type_code + u'-' +gem_code + u'-' + model_code
    instance.article_code = article_code
    return

def change_article_code_model(instance):
    if not instance.model:
        if type(instance) == Article: model = instance.initial_model.model_code
        elif type(instance) == Suite: model = u'00000'
    else: model = instance.model.model_code

    if instance.article_code: 
        codepiece = re.search(ur"^(?P<codepiece>.*-.*-).*$", instance.article_code).group('codepiece')
        instance.article_code = codepiece + model
    else: instance.article_code = u'--' + model
    return None

def change_article_code_gem(instance, gem_list):
    gem_code = u''
    for gem in gem_list:
        if gem['major'] and not gem['DELETE']: 
            gem_code = u'99' if gem_code else gem['gem'].gem_code
    if not gem_code:
        for gem in gem_list:
            if not gem['DELETE']: 
                gem_code = u'99' if gem_code else gem['gem'].gem_code
    if not gem_code: gem_code = u'00'

    if instance.article_code:
        codepieceone = re.search(ur"^(?P<codepieceone>.*-).*-.*$", instance.article_code).group('codepieceone')
        codepiecetwo = re.search(ur"^.*-.*(?P<codepiecetwo>-.*)$", instance.article_code).group('codepiecetwo')
        instance.article_code = codepieceone + gem_code + codepiecetwo
    else: instance.article_code = u'-' + gem_code + u'-'

    return None

def change_article_code_type(instance):
    
    j_type_code = u''
    if type(instance) == Article:
        j_type_code = instance.j_type.j_type_code
    elif type(instance) == Suite:
        busy_numbers=[]
        for suite in instance.model.suite_set.all():
            number = re.match(ur"^Г(?P<number>\d+)-", suite.article_code).group('number')
            if number: busy_numbers.append(int(number))
        if not busy_numbers: j_type_code = u'Г1'
        else:
            for candidate, number in enumerate(busy_numbers):
                if candidate + 1 <> number: 
                    j_type_code = u'Г' + unicode(candidate + 1)
                    break
            if not j_type_code: j_type_code = u'Г' + unicode(candidate + 2)

    if instance.article_code:
        codepiece = re.search(ur"^.*(?P<codepiece>-.*-.*)$", instance.article_code).group('codepiece')
        instance.article_code = j_type_code + codepiece
    else: instance.article_code = j_type_code + u'--'

    return None

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
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Тип изделий')
    name_eng = models.CharField(max_length=20, unique=True, verbose_name=u'Тип изделий (на английском)')
    j_type_code = CustomJTypeCode(max_length=1, unique=True, verbose_name=u'Код изделия', help_text=u'Состоит из одной буквы. Используется в артикуле.')


    class Meta:
        verbose_name = u'тип изделия'
        verbose_name_plural = u'типы изделий'

    def __unicode__(self):
        return self.name


class Gender(models.Model):
    gender_code = models.CharField (max_length=1, primary_key=True)
    name = models.CharField(max_length=15, unique=True, verbose_name=u'Пол')
    class Meta:
        verbose_name = u'пол'
        verbose_name_plural = u'таблица полов'

    def __unicode__(self):
        return self.name


class Gem(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name=u'Название')
    gem_code = CustomGemCode(max_length=2, unique=True, verbose_name=u'Код камня', help_text=u'Состоит из двух цифр. Используется в артикуле.')
    zodiac = models.CharField(max_length=11, choices=CHOICES_ZODIAC, blank=True, verbose_name=u'Знак Зодиака')
    class Meta:
        verbose_name = u'тип камня'
        verbose_name_plural = u'типы камней'

    def __unicode__(self):
        return self.name


class Metal(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name=u'Металл')
    zodiac = models.CharField(max_length=11, choices=CHOICES_ZODIAC, blank=True, verbose_name=u'Знак Зодиака')
    class Meta:
        verbose_name = u'металл'
        verbose_name_plural = u'металлы'

    def __unicode__(self):
        return self.name


class JewelryModel(models.Model):
#    model_code = models.CharField(default=create_model(), max_length=10, unique=True)
    model_code = models.CharField(max_length=10, unique=True)
    bound =  models.BooleanField(verbose_name=u'Связанная')
    gender = models.ForeignKey(Gender, verbose_name=u'Пол')
    metal = models.ForeignKey(Metal, verbose_name=u'Металл')
    supplier = models.ForeignKey(Supplier, verbose_name=u'Поставщик')

    def create_model(self):
        id = self.id
        model_code = str(id+100)
        if len(model_code) < 5: 
            # That's for better appearance
            model_code = "0"*(5-len(model_code)) + model_code

    def __unicode__(self):
        return self.model_code

#class Price(models.Model):
#    price = models.PositiveIntegerField()
#    date_effective = models.DateField()


class Article(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'Название')
    article_code = models.CharField(max_length=15, blank=True, verbose_name=u'Артикул')
#    model = models.ForeignKey(JewelryModel, editable=False, verbose_name=u'Модель. Вы не должны видеть это поле, обратитесь к разработчику.')
#    initial_model = models.ForeignKey(JewelryModel, related_name='article_set_initial', editable=False, verbose_name=u'Первичная модель. Вы не должны видеть это поле, обратитесь к разработчику.')
    initial_model = models.ForeignKey(JewelryModel, blank=True, null=True, related_name='article_set_initial', verbose_name=u'Первичная модель. Вы не должны видеть это поле, обратитесь к разработчику.')
    model = models.ForeignKey(JewelryModel, blank=True, null=True, verbose_name=u'Модель. Вы не должны видеть это поле, обратитесь к разработчику.')
    
    j_type = models.ForeignKey(JewelryType, verbose_name=u'Тип изделия')
    gender = models.ForeignKey(Gender, verbose_name=u'Пол')
    gems = models.ManyToManyField(Gem, through='SpecificGem', blank=True, verbose_name=u'Камни')
    metal = models.ForeignKey(Metal, verbose_name=u'Металл')
    site_description = models.TextField(verbose_name=u'Описание на сайте')
    price = models.PositiveIntegerField(verbose_name=u'Цена')
    date_on_sale = models.DateField(blank=True, null=True, verbose_name=u'Выставлено на продажу', help_text=u'Артикулы без даты или с будущей датой не будут отображаться на сайте.')
    supplier = models.ForeignKey(Supplier, verbose_name=u'Поставщик')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')
    image_one = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография')
    image_two = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография')
    image_three = models.ImageField(upload_to='articles/', blank=True, verbose_name=u'Фотография')


    class Meta:
        verbose_name = u'изделие'
        verbose_name_plural = u'изделия'

    def __unicode__(self):
        return u"%s" % (self.name)

    def gem_summary(self):
        g_list=[]
        for gem in self.specificgem_set.all():
            gem_props = []
            if gem.size: gem_props.append(u'%i карат' % (gem.size)) 
            if gem.quantity <> 1: gem_props.append(u'%s шт.' % (gem.quantity))
            to_return = u'%s (%s)' % (gem.gem.name, u', '.join(gem_props)) if gem_props else u'%s' % (gem.gem.name)
            g_list.append(to_return)
        return u', '.join(g_list)

    def thumbnail(self):
        thumb_path = self.image_one.url if self.image_one else u'/images/special/placeholder1.jpg'
        return thumb_path

class SpecificGem(models.Model):
    article = models.ForeignKey(Article, verbose_name=u'Артикул')
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
    article_code = models.CharField(max_length=15, blank=True, verbose_name=u'Артикул')
#    model = models.ForeignKey(JewelryModel, blank=True, editable=False, verbose_name=u'Модель. Вы не должны видеть это поле, обратитесь к разработчику.')
    articles = models.ManyToManyField(Article, blank=True, verbose_name=u'Изделия', help_text=u'Гарнитур может быть пустым для удобства последующего ввода данных.')
    gender = models.ForeignKey(Gender, blank=True, null=True, verbose_name=u'Пол', help_text=u'Определяется по входящим в гарнитур артикулам. Гарнитур с артикулами, предназначенными для разных полов, не сохранится.')
#    gems = models.ManyToManyField(Gem, through='SpecificGem', blank=True, editable=False, verbose_name=u'Камни')
#    metal = models.ForeignKey(Metal, blank=True, null=True, editable=False, verbose_name=u'Металл')
    site_description = models.TextField(verbose_name=u'Описание на сайте')
    price = models.PositiveIntegerField(verbose_name=u'Цена')
    date_on_sale = models.DateField(blank=True, null=True, verbose_name=u'Выставлено на продажу', help_text=u'Артикулы без даты или с будущей датой не будут отображаться на сайте.')
#    supplier = models.ForeignKey(Supplier, blank=True, null=True, editable=False, verbose_name=u'Поставщик')
    notes = models.TextField(blank=True, verbose_name=u'Заметки', help_text=u'Для служебного использования.')

    model = models.ForeignKey(JewelryModel, blank=True, null=True, verbose_name=u'Модель. Вы не должны видеть это поле, обратитесь к разработчику.')
    metal = models.ForeignKey(Metal, blank=True, null=True, verbose_name=u'Металл')
    supplier = models.ForeignKey(Supplier, blank=True, null=True, verbose_name=u'Поставщик')

    class Meta:
        verbose_name = u'гарнитур'
        verbose_name_plural = u'гарнитуры'

    def __unicode__(self):
        return u'%s' % (self.name)
