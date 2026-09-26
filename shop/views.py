from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView

from .models import Product, PromoCode, Purchase

PROMO_SESSION_KEY = 'active_promo_codes'


def get_active_promo_codes(request):
    return request.session.get(PROMO_SESSION_KEY, [])


def get_available_products(request):
    """Обычные товары + товары активированных промокодов."""
    active = get_active_promo_codes(request)
    return Product.objects.filter(
        Q(promo_code__isnull=True) | Q(promo_code__code__in=active)
    ).order_by('pk')


def activate_promo_code(request):
    """Активирует промокод из POST-формы. Возвращает True при успехе."""
    code = request.POST.get('promo_code', '').strip().upper()
    promo = PromoCode.objects.filter(code=code).first()
    if promo is None:
        return False
    active = get_active_promo_codes(request)
    if promo.code not in active:
        active.append(promo.code)
        request.session[PROMO_SESSION_KEY] = active
    return True


def index(request):
    promo_error = False
    if request.method == 'POST':
        promo_error = not activate_promo_code(request)
    products = get_available_products(request)
    context = {
        'products': products,
        'active_promo_codes': get_active_promo_codes(request),
        'promo_error': promo_error,
    }
    return render(request, 'shop/index.html', context)


class PurchaseCreate(CreateView):
    model = Purchase
    fields = ['product', 'person', 'address']

    def dispatch(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        available = get_available_products(request).filter(pk=product_id)
        if not available.exists():
            raise Http404(
                'Товар недоступен: для его покупки активируйте промокод')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(f'Спасибо за покупку, {self.object.person}!')
