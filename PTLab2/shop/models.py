from django.db import models


class PromoCode(models.Model):
    """Промокод магазина (вариант 6).

    Товар, закреплённый за промокодом, отображается в каталоге и
    доступен для покупки только после активации этого промокода.
    """
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, default='')

    def __str__(self):
        return self.code


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    promo_code = models.ForeignKey(PromoCode, null=True, blank=True,
                                   on_delete=models.SET_NULL,
                                   related_name='products')


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    person = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
