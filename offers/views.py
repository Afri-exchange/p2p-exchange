from django.http import Http404
# from django.forms.util import ErrorList
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils import timezone
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, reverse, HttpResponseRedirect
from django.urls import reverse_lazy
# Create your views here.
from offers.forms import OfferForm
from accounts.models import Accounts
from offers.models import Offers, Bids
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView, CreateView, DeleteView
import requests
from decimal import Decimal
TICKER_API_URL = 'http://api.coinmarketcap.com/v1/ticker/'
# Create your views here.


def error_404_view(request, exception):
    return render(request, 'jinja/error_404.html')


@method_decorator(login_required, name='dispatch')
class OfferUpdateView(UpdateView):
    model = Offers
    fields = ('fiat_currency', 'pay_method',
              'min_amount', 'max_amount', 'margin_percent')
    template_name = 'jinja/edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'offer'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        price = round(get_latest_crypto_price('ethereum'))
        context['price'] = "The price of 1 ethereum is ${}".format(price)
        return context

    def form_valid(self, form):
        offer = form.save(commit=False)
        try:
            offer.validate_min_amount()
        except ValidationError as e:
            form.add_error('min_amount', e)
            return self.form_invalid(form)
        # post.updated_by = self.request.user
        # post.updated_at = timezone.now()
        offer.save()
        return redirect('offers')


@method_decorator(login_required, name='dispatch')
class CreateOfferView(CreateView):
    model = Offers
    fields = ['fiat_currency', 'pay_method',
              'min_amount', 'max_amount', 'margin_percent']
    template_name = 'jinja/index.html'

    def get_initial(self):
        acc = get_object_or_404(Accounts, owned_by=self.request.user)
        if acc.acc_balance == 0:
            raise Http404("Not enough Balance")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        price = round(get_latest_crypto_price('ethereum'))
        context['price'] = "The price of 1 ethereum is ${}".format(price)
        return context

    def form_valid(self, form):
        offer = form.save(commit=False)
        try:
            offer.validate_min_amount()
        except ValidationError as e:
            form.add_error('min_amount', e)
            return self.form_invalid(form)
        offer.created_by = self.request.user
        offer.save()
        return redirect('offers')


@method_decorator(login_required, name='dispatch')
class CreateBidView(CreateView):
    model = Bids
    fields = ['amount']
    template_name = 'jinja/add_bid.html'

    def get_initial(self):
        offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        if offer.created_by == self.request.user:
            raise Http404("Offer Owner can't create Bids")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer'] = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        feed = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        price = round(get_latest_crypto_price('ethereum'))
        context['price'] = "The price of 1 ethereum is ${}".format(price)
        context['warn'] = "The amount should be within the range of {} and {}".format(feed.min_amount, feed.max_amount)
        return context

    def form_valid(self, form):
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        bid = form.save(commit=False)
        bid.created_by = self.request.user
        bid.offer = self.offer
        try:
            bid.validate_amount()
        except ValidationError as e:
            form.add_error('amount',e)
            return self.form_invalid(form)
        bid.last_updated = timezone.now()
        bid.save()
        acc = get_object_or_404(Accounts, owned_by=self.offer.created_by)
        acc.escrow_balance += bid.amount
        acc.acc_balance -= bid.amount
        acc.save()
        return redirect('view_bids', id=self.offer.pk)


@method_decorator(login_required, name='dispatch')
class BidUpdateView(UpdateView):
    model = Bids
    fields = ('amount',)
    template_name = 'jinja/edit_bid.html'
    pk_url_kwarg = 'bid_id'
    context_object_name = 'bid'

    def get_object(self, *args, **kwargs):
        bid = super(BidUpdateView, self).get_object(*args, **kwargs)
        if bid.status != "OPEN":
            raise Http404("No bids found matching the query")
        return bid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feed = get_object_or_404(Bids, pk=self.kwargs.get('bid_id'))
        context['warn'] = "The amount should be within the range of {} and {}".format(feed.offer.min_amount, feed.offer.max_amount)
        price = round(get_latest_crypto_price('ethereum'))
        context['price'] = "The price of 1 ethereum is ${}".format(price)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        bid = form.save(commit=False)
        try:
            bid.validate_amount()
        except ValidationError as e:
            form.add_error('amount', e)
            return self.form_invalid(form)
        bid.last_updated = timezone.now()
        bid.save()
        return redirect('view_bids', id=bid.offer.pk)

@method_decorator(login_required, name='dispatch')
class BidDeleteView(DeleteView):
    model = Bids
    pk_url_kwarg = 'id'
    # success_url = reverse_lazy('offers')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        # pk = self.kwargs['pk']
        self.bid = get_object_or_404(Bids, pk=self.kwargs.get('id'))
        if self.bid.created_by != self.request.user:
            raise Http404("No bids found matching the query")
        if self.bid.status == "ACCEPTED":
            raise Http404("No bids found matching the query")
        if self.bid.status == "OPEN":
            acc = get_object_or_404(Accounts, owned_by=self.bid.offer.created_by)
            acc.escrow_balance -= self.bid.amount
            acc.acc_balance += self.bid.amount
            acc.save()
        pk = self.bid.offer.pk
        self.bid.delete()
        return HttpResponseRedirect(reverse('view_bids', kwargs={'id': pk}))

@login_required
def OwnerAcceptBid(request, id):
    bid = get_object_or_404(Bids, pk=id)
    if bid.offer.created_by != request.user:
        raise Http404("No bids found matching the query")
    if bid.status != "OPEN":
        raise Http404("No bids found matching the query")
    acc = get_object_or_404(Accounts, owned_by=request.user)
    if acc.acc_balance == 0:
        raise Http404("Not enough Balance")
    pk = bid.offer.pk
    # margin = bid.offer.margin_percent
    bid_amount = bid.amount
    acc2 = get_object_or_404(Accounts, owned_by=bid.created_by)
    # price = round(get_latest_crypto_price('ethereum'))
    # amount = bid_amount / (price * (margin + 100))
    acc.escrow_balance -= bid_amount
    acc.save()
    acc2.acc_balance += bid_amount
    acc2.save()
    bid.status = "ACCEPTED"
    bid.save()
    return HttpResponseRedirect(reverse('view_bids', kwargs={'id': pk}))

@login_required
def OwnerDeclineBid(request, id):
    bid = get_object_or_404(Bids, pk=id)
    if bid.offer.created_by != request.user:
        raise Http404("No bids found matching the query")
    if bid.status != "OPEN":
        raise Http404("No bids found matching the query")
    acc = get_object_or_404(Accounts, owned_by=request.user)
    acc.escrow_balance -= bid.amount
    acc.acc_balance += bid.amount
    acc.save()
    pk = bid.offer.pk
    bid.status = "DECLINED"
    bid.save()
    return HttpResponseRedirect(reverse('view_bids', kwargs={'id': pk}))

# @method_decorator(login_required, name='dispatch')
class BidListView(ListView):
    model = Bids
    context_object_name = 'bids'
    template_name = 'jinja/bids.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['price'] = round(get_latest_crypto_price('ethereum'))
        kwargs['offer'] = self.offer
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        queryset = self.offer.bids.order_by('-last_updated')
        return queryset

@method_decorator(login_required, name='dispatch')
class UserOfferBidListView(ListView):
    model = Bids
    context_object_name = 'bids'
    template_name = 'jinja/offer_bids.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['price'] = round(get_latest_crypto_price('ethereum'))
        kwargs['offer'] = self.offer
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        if self.offer.created_by != self.request.user:
            raise Http404("No offers found matching the query")
        queryset = self.offer.bids.order_by('-last_updated')
        return queryset

@method_decorator(login_required, name='dispatch')
class UserBidsView(ListView):
    model = Bids
    context_object_name = 'bids'
    template_name = 'jinja/my_bids.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price'] = round(get_latest_crypto_price('ethereum'))
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by=self.request.user)
        return queryset.order_by('-last_updated')

class ShowOffersView(ListView):
    model = Offers
    context_object_name = 'offers'
    template_name = 'jinja/offers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price'] = round(get_latest_crypto_price('ethereum'))
        return context


@method_decorator(login_required, name='dispatch')
class UserOfferView(ListView):
    model = Offers
    context_object_name = 'offers'
    template_name = 'jinja/show.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['acc'] = get_object_or_404(Accounts, owned_by=self.request.user)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)


@method_decorator(login_required, name='dispatch')
class OfferDeleteView(DeleteView):
    model = Offers
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('offers')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        # pk = self.kwargs['pk']
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        if self.offer.created_by != self.request.user:
            raise Http404("No offers found matching the query")
        for bid in self.offer.bids.all():
            if bid.status == "OPEN":
                acc = get_object_or_404(
                    Accounts, owned_by=bid.offer.created_by)
                acc.escrow_balance -= bid.amount
                acc.acc_balance += bid.amount
                acc.save()
        self.offer.delete()
        return HttpResponseRedirect(reverse('offers'))



def get_latest_crypto_price(crypto):
    response = requests.get(TICKER_API_URL+crypto)
    response_json = response.json()
    return float(response_json[0]['price_usd'])
