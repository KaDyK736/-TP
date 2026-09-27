# -*- coding: utf-8 -*-
"""Лабораторная работа 3.

Модульные тесты магазина (Лабораторная работа 2) с использованием
mock-объектов: ORM, сессия и родительские обработчики Django
подменяются, поэтому проверяется логика представлений без обращения
к базе данных.
"""
from unittest import mock

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase
from django.views.generic.base import View

from shop import views
from shop.views import PROMO_SESSION_KEY, PurchaseCreate


class FakeSession(dict):
    """Замена request.session: dict уже поддерживает get/[...]=."""


class FakePromo:
    def __init__(self, code):
        self.code = code


def make_request(method='get', path='/', data=None):
    request = getattr(RequestFactory(), method)(path, data or {})
    request.session = FakeSession()
    return request


class ActivatePromoCodeMockedTest(SimpleTestCase):

    def test_valid_code_is_saved_to_session(self):
        request = make_request('post', '/', {'promo_code': 'gamer'})
        with mock.patch('shop.views.PromoCode') as promo_model:
            promo_model.objects.filter.return_value \
                .first.return_value = FakePromo('GAMER')
            result = views.activate_promo_code(request)
        self.assertTrue(result)
        self.assertEqual(request.session[PROMO_SESSION_KEY], ['GAMER'])
        promo_model.objects.filter.assert_called_once_with(code='GAMER')

    def test_code_is_normalized_to_upper_case(self):
        request = make_request('post', '/', {'promo_code': '  nEwYeAr '})
        with mock.patch('shop.views.PromoCode') as promo_model:
            promo_model.objects.filter.return_value \
                .first.return_value = FakePromo('NEWYEAR')
            views.activate_promo_code(request)
        promo_model.objects.filter.assert_called_once_with(code='NEWYEAR')

    def test_unknown_code_returns_false(self):
        request = make_request('post', '/', {'promo_code': 'GHOST'})
        with mock.patch('shop.views.PromoCode') as promo_model:
            promo_model.objects.filter.return_value \
                .first.return_value = None
            result = views.activate_promo_code(request)
        self.assertFalse(result)
        self.assertNotIn(PROMO_SESSION_KEY, request.session)

    def test_repeated_activation_does_not_duplicate_code(self):
        request = make_request('post', '/', {'promo_code': 'GAMER'})
        request.session[PROMO_SESSION_KEY] = ['GAMER']
        with mock.patch('shop.views.PromoCode') as promo_model:
            promo_model.objects.filter.return_value \
                .first.return_value = FakePromo('GAMER')
            result = views.activate_promo_code(request)
        self.assertTrue(result)
        self.assertEqual(request.session[PROMO_SESSION_KEY], ['GAMER'])


class GetAvailableProductsMockedTest(SimpleTestCase):

    def test_filter_built_from_session_codes(self):
        request = make_request()
        request.session[PROMO_SESSION_KEY] = ['GAMER', 'STUDENT']
        with mock.patch('shop.views.Product') as product_model:
            queryset = product_model.objects.filter.return_value
            sentinel = queryset.order_by.return_value
            result = views.get_available_products(request)
        product_model.objects.filter.assert_called_once()
        query = product_model.objects.filter.call_args.args[0]
        self.assertIn('promo_code__code__in', str(query))
        queryset.order_by.assert_called_once_with('pk')
        self.assertIs(result, sentinel)

    def test_empty_session_still_builds_query(self):
        request = make_request()
        with mock.patch('shop.views.Product') as product_model:
            views.get_available_products(request)
        query = product_model.objects.filter.call_args.args[0]
        self.assertIn('promo_code__isnull', str(query))


class IndexViewMockedTest(SimpleTestCase):

    def setUp(self):
        self.client = self.client_class()

    def test_get_uses_products_from_helper(self):
        with mock.patch('shop.views.get_available_products',
                        return_value=[]) as helper:
            response = self.client.get('/')
        self.assertTrue(helper.called)
        self.assertEqual(response.context['products'], [])
        self.assertFalse(response.context['promo_error'])
        self.assertEqual(response.context['active_promo_codes'], [])

    def test_get_without_promo_skips_activation(self):
        with mock.patch('shop.views.activate_promo_code') as activate, \
                mock.patch('shop.views.get_available_products',
                           return_value=[]):
            self.client.get('/')
        activate.assert_not_called()

    def test_post_marks_error_when_activation_fails(self):
        with mock.patch('shop.views.activate_promo_code',
                        return_value=False), \
                mock.patch('shop.views.get_available_products',
                           return_value=[]):
            response = self.client.post('/', {'promo_code': 'X'})
        self.assertTrue(response.context['promo_error'])

    def test_post_without_error_when_activation_succeeds(self):
        with mock.patch('shop.views.activate_promo_code',
                        return_value=True), \
                mock.patch('shop.views.get_available_products',
                           return_value=[]):
            response = self.client.post('/', {'promo_code': 'GAMER'})
        self.assertFalse(response.context['promo_error'])

    def test_activation_receives_the_request(self):
        with mock.patch('shop.views.activate_promo_code',
                        return_value=True) as activate, \
                mock.patch('shop.views.get_available_products',
                           return_value=[]):
            self.client.post('/', {'promo_code': 'GAMER'})
        self.assertTrue(activate.called)
        request_arg = activate.call_args.args[0]
        self.assertEqual(request_arg.method, 'POST')


class PurchaseCreateMockedTest(SimpleTestCase):

    def make_view(self, product_id, available):
        queryset = mock.MagicMock()
        queryset.filter.return_value.exists.return_value = available
        return queryset

    def test_locked_product_without_promo_raises_404(self):
        request = make_request()
        queryset = self.make_view(product_id=7, available=False)
        view = PurchaseCreate()
        view.setup(request, product_id=7)
        with mock.patch('shop.views.get_available_products',
                        return_value=queryset):
            with self.assertRaises(Http404):
                view.dispatch(request, product_id=7)
        queryset.filter.assert_called_once_with(pk=7)

    def test_available_product_delegates_to_create_view(self):
        request = make_request()
        queryset = self.make_view(product_id=7, available=True)
        view = PurchaseCreate()
        view.setup(request, product_id=7)
        with mock.patch('shop.views.get_available_products',
                        return_value=queryset), \
                mock.patch.object(View, 'dispatch',
                                  return_value='parent-dispatch'):
            result = view.dispatch(request, product_id=7)
        self.assertEqual(result, 'parent-dispatch')

    def test_form_valid_saves_purchase_and_thanks(self):
        view = PurchaseCreate()
        form = mock.MagicMock()
        form.save.return_value = mock.MagicMock(person='Петров')
        response = view.form_valid(form)
        form.save.assert_called_once()
        self.assertEqual(view.object, form.save.return_value)
        self.assertIn('Спасибо за покупку, Петров!',
                      response.content.decode('utf-8'))
