from django.test import TestCase, Client
from shop.models import Product, PromoCode
from shop.views import PurchaseCreate, PROMO_SESSION_KEY

class PurchaseCreateTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_webpage_accessibility(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class PromoCodeViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.promo = PromoCode.objects.create(
            code="GAMER", description="Игровые аксессуары")
        self.plain_product = Product.objects.create(
            name="Ноутбук Lenovo", price=45000)
        self.locked_product = Product.objects.create(
            name="Игровое кресло", price=24000, promo_code=self.promo)

    def activate(self, code):
        return self.client.post('/', {'promo_code': code})

    def test_index_shows_plain_product_without_promo(self):
        response = self.client.get('/')
        self.assertContains(response, "Ноутбук Lenovo")

    def test_index_hides_locked_product_without_promo(self):
        response = self.client.get('/')
        self.assertNotContains(response, "Игровое кресло")

    def test_valid_promo_code_unlocks_product(self):
        self.activate("GAMER")
        response = self.client.get('/')
        self.assertContains(response, "Игровое кресло")
        self.assertContains(response, "GAMER")

    def test_invalid_promo_code_shows_error(self):
        response = self.activate("WRONG_CODE")
        self.assertTrue(response.context['promo_error'])
        self.assertNotContains(response, "Игровое кресло")

    def test_promo_code_is_case_insensitive(self):
        response = self.activate("gamer")
        self.assertFalse(response.context['promo_error'])
        self.assertContains(self.client.get('/'), "Игровое кресло")

    def test_activating_promo_code_saves_it_to_session(self):
        self.activate("GAMER")
        session = self.client.session
        self.assertEqual(session[PROMO_SESSION_KEY], ["GAMER"])

    def test_reactivating_same_promo_code_is_not_error(self):
        self.activate("GAMER")
        response = self.activate("GAMER")
        self.assertFalse(response.context['promo_error'])
        self.assertEqual(
            self.client.session[PROMO_SESSION_KEY], ["GAMER"])

    def test_empty_promo_code_is_error(self):
        response = self.activate("")
        self.assertTrue(response.context['promo_error'])

    def test_several_promo_codes_work_independently(self):
        second_promo = PromoCode.objects.create(code="STUDENT")
        second_product = Product.objects.create(
            name="Учебный нетбук", price=21000, promo_code=second_promo)
        self.activate("STUDENT")
        response = self.client.get('/')
        self.assertContains(response, "Учебный нетбук")
        self.assertNotContains(response, "Игровое кресло")
        self.activate("GAMER")
        response = self.client.get('/')
        self.assertContains(response, "Учебный нетбук")
        self.assertContains(response, "Игровое кресло")

    def test_buy_locked_product_without_promo_returns_404(self):
        response = self.client.get(
            f'/buy/{self.locked_product.id}/')
        self.assertEqual(response.status_code, 404)

    def test_buy_locked_product_after_promo_is_available(self):
        self.activate("GAMER")
        response = self.client.get(f'/buy/{self.locked_product.id}/')
        self.assertEqual(response.status_code, 200)

    def test_buy_plain_product_is_available(self):
        response = self.client.get(f'/buy/{self.plain_product.id}/')
        self.assertEqual(response.status_code, 200)

    def test_purchase_locked_product_after_promo(self):
        self.activate("GAMER")
        response = self.client.post(f'/buy/{self.locked_product.id}/', {
            'product': self.locked_product.id,
            'person': 'Иванов',
            'address': 'Svetlaya St.',
        })
        self.assertContains(response, 'Спасибо за покупку, Иванов!')
        purchase = self.locked_product.purchase_set.get()
        self.assertEqual(purchase.person, 'Иванов')

    def test_purchase_locked_product_without_promo_is_blocked(self):
        response = self.client.post(f'/buy/{self.locked_product.id}/', {
            'product': self.locked_product.id,
            'person': 'Петров',
            'address': 'Lenina St.',
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.locked_product.purchase_set.count(), 0)
