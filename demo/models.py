from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils.crypto import get_random_string


def get_name_file(instance, filename):
    return '/'.join([get_random_string(length=5) + '_' + filename])


class User(AbstractUser):
    name = models.CharField(max_length=254, verbose_name='Имя', blank=False)
    surname = models.CharField(max_length=254, verbose_name='Фамилия', blank=False)
    patronymic = models.CharField(max_length=254, verbose_name='Отчество', blank=True)
    username = models.CharField(max_length=254, verbose_name='Логин', unique=True, blank=False)
    email = models.CharField(max_length=254, verbose_name='Почта', unique=True, blank=False)
    password = models.CharField(max_length=254, verbose_name='Пароль', blank=False)
    role = models.CharField(max_length=254, verbose_name='Роль',
                            choices=(('admin', 'Администратор'), ('user', 'Пользователь')), default='user')
    USERNAME_FIELD = 'username'

    def full_name(self):
        return ' '.join(self.name, self.patronymic, self.surname)


class Product(models.Model):
    name = models.CharField(max_length=254, verbose_name='Имя')
    datetime = models.DateTimeField(verbose_name='Дата добавления', auto_now=True)
    photo = models.ImageField(max_length=254, verbose_name='Фото', upload_to=get_name_file, blank=True, null=True,
                              validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg', 'webp'))])
    year = models.IntegerField(verbose_name='Год производства', blank=True)
    country = models.CharField(max_length=254, verbose_name='Страна', blank=True)
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2, blank=False, default=0.0)
    category = models.ForeignKey('Category', verbose_name='Категория', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество', default=1, blank=False)

    def get_absolute_url(self):
        return reverse('product',args=[str(self.id)])


class Category(models.Model):
    name = models.CharField(max_length=254, verbose_name='Наименование', blank=False)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтверждённый'),
        ('canceled', 'Отмененный'),
    ]

    date = models.DateTimeField(verbose_name='Дата заказа', auto_now=True)
    status = models.CharField(max_length=254, verbose_name='Статус заказа',
                              choices=STATUS_CHOICES,
                              default='new')
    user = models.ForeignKey('User', verbose_name='Пользователь', on_delete=models.CASCADE)
    refuse_reason = models.TextField(max_length=254, verbose_name='Причина отказа', blank=True)
    products = models.ManyToManyField('Product', through='ProductsInOrder', related_name='orders')

    def status_verbose(self):
        return dict(self.STATUS_CHOICES)[self.status]

    def count_product(self):
        k = 0
        for item in self.productsinorder_set.all():
            k += item.count
        return k


class ProductsInOrder(models.Model):
    order = models.ForeignKey('Order', verbose_name='Заказ', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', verbose_name='Товар', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество', default=1, blank=False)
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2, default=0.0, blank=False)


class ProductsInCart(models.Model):
    user = models.ForeignKey('User', verbose_name='Пользователь', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', verbose_name='Товар', on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name='Количество', default=1, blank=False)
