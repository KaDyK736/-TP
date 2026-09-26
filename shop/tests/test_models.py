from django.test import TestCase
from shop.models import Product, PromoCode, Purchase
from datetime import datetime

class ProductTestCase(TestCase):
    def setUp(self):
        Product.objects.create(name="book", price="740")
        Product.objects.create(name="pencil", price="50")

    def test_correctness_types(self):                   
        self.assertIsInstance(Product.objects.get(name="book").name, str)
        self.assertIsInstance(Product.objects.get(name="book").price, int)
        self.assertIsInstance(Product.objects.get(name="pencil").name, str)
        self.assertIsInstance(Product.objects.get(name="pencil").price, int)        

    def test_correctness_data(self):
        self.assertTrue(Product.objects.get(name="book").price == 740)
        self.assertTrue(Product.objects.get(name="pencil").price == 50)

    def test_product_without_promo_code(self):
        self.assertIsNone(Product.objects.get(name="book").promo_code)


class PurchaseTestCase(TestCase):
    def setUp(self):
        self.product_book = Product.objects.create(name="book", price="740")
        self.datetime = datetime.now()
        Purchase.objects.create(product=self.product_book,
                                person="Ivanov",
                                address="Svetlaya St.")

    def test_correctness_types(self):
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).person, str)
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).address, str)
        self.assertIsInstance(Purchase.objects.get(product=self.product_book).date, datetime)

    def test_correctness_data(self):
        self.assertTrue(Purchase.objects.get(product=self.product_book).person == "Ivanov")
        self.assertTrue(Purchase.objects.get(product=self.product_book).address == "Svetlaya St.")
        self.assertTrue(Purchase.objects.get(product=self.product_book).date.replace(microsecond=0) == \
            self.datetime.replace(microsecond=0))


class PromoCodeTestCase(TestCase):
    def setUp(self):
        self.promo = PromoCode.objects.create(
            code="GAMER", description="Игровые аксессуары")
        self.locked_product = Product.objects.create(
            name="Игровое кресло", price=24000, promo_code=self.promo)
        self.plain_product = Product.objects.create(
            name="Ноутбук", price=45000)

    def test_promo_code_str(self):
        self.assertEqual(str(self.promo), "GAMER")

    def test_product_with_promo_code(self):
        self.assertEqual(self.locked_product.promo_code, self.promo)

    def test_product_without_promo_code(self):
        self.assertIsNone(self.plain_product.promo_code)

    def test_promo_code_reverse_relation(self):
        self.assertEqual(self.promo.products.count(), 1)
        self.assertEqual(self.promo.products.first(), self.locked_product)

    def test_deleting_promo_code_keeps_product(self):
        self.promo.delete()
        product = Product.objects.get(pk=self.locked_product.pk)
        self.assertIsNone(product.promo_code)
