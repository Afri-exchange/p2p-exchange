from django.http import Http404
from django.utils import timezone
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, reverse, HttpResponseRedirect
from django.urls import reverse_lazy
# Create your views here.
from offers.forms import OfferForm
from offers.models import Offers, Bids
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView, CreateView, DeleteView
import requests
TICKER_API_URL = 'https://api.coinmarketcap.com/v1/ticker/'
# Create your views here.


def error_404_view(request, exception):
    return render(request, 'jinja/error_404.html')


@method_decorator(login_required, name='dispatch')
class OfferUpdateView(UpdateView):
    model = Offers
    fields = ('avail_amount', 'fiat_currency', 'pay_method',
              'min_amount', 'max_amount', 'margin_percent')
    template_name = 'jinja/edit.html'
    pk_url_kwarg = 'id'
    context_object_name = 'offer'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        offer = form.save(commit=False)
        # post.updated_by = self.request.user
        # post.updated_at = timezone.now()
        offer.save()
        return redirect('offers')


@method_decorator(login_required, name='dispatch')
class CreateOfferView(CreateView):
    model = Offers
    fields = ['avail_amount', 'fiat_currency', 'pay_method',
              'min_amount', 'max_amount', 'margin_percent']
    template_name = 'jinja/index.html'

    def form_valid(self, form):
        offer = form.save(commit=False)
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
        return context

    def form_valid(self, form):
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        bid = form.save(commit=False)
        bid.created_by = self.request.user
        bid.offer = self.offer
        bid.last_updated = timezone.now()
        bid.save()
        return redirect('view_bids', id=self.offer.pk)


@method_decorator(login_required, name='dispatch')
class BidUpdateView(UpdateView):
    model = Bids
    fields = ('amount',)
    template_name = 'jinja/edit_bid.html'
    pk_url_kwarg = 'bid_id'
    context_object_name = 'bid'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        bid = form.save(commit=False)
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
        pk = self.bid.offer.pk
        self.bid.delete()
        return HttpResponseRedirect(reverse('view_bids', kwargs={'id': pk}))

# @method_decorator(login_required, name='dispatch')
class BidListView(ListView):
    model = Bids
    context_object_name = 'bids'
    template_name = 'jinja/bids.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['offer'] = self.offer
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.offer = get_object_or_404(Offers, pk=self.kwargs.get('id'))
        queryset = self.offer.bids.order_by('-last_updated')
        return queryset

class ShowOffersView(ListView):
    model = Offers
    context_object_name = 'offers'
    template_name = 'jinja/offers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price'] = round(get_latest_crypto_price('bitcoin'))
        return context


@method_decorator(login_required, name='dispatch')
class UserOfferView(ListView):
    model = Offers
    context_object_name = 'offers'
    template_name = 'jinja/show.html'

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


def get_latest_crypto_price(crypto):
    response = requests.get(TICKER_API_URL+crypto)
    response_json = response.json()
    return float(response_json[0]['price_usd'])
