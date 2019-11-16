from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, reverse

# Create your views here.
from offers.forms import OfferForm
from offers.models import Offers
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
# Create your views here.


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Offers
    fields = ('avail_amount', 'fiat_currency', 'pay_method',
              'min_amount', 'max_amount', 'margin_percent')
    template_name = 'edit.html'
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


@login_required
def new(request):
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            try:
                offer = form.save(commit=False)
                offer.created_by = request.user
                offer.save()
                return redirect('/offers')
            except:
                pass
    else:
        form = OfferForm()
    return render(request, 'index.html', {'form': form})


@login_required
def show(request):
    offers = Offers.objects.filter(created_by=request.user)
    return render(request, "show.html", {'offers': offers})


def showall(request):
    offers = Offers.objects.all()
    return render(request, "offers.html", {'offers': offers})
# def edit(request, id):
#     offer = Offers.objects.get(id=id)
#     return render(request, 'edit.html', {'offer': offer})


# def update(request, id):
#     offer = Offers.objects.get(id=id)
#     form = OfferForm(request.POST, instance=offer)
#     if form.is_valid():
#         form.save()
#         return redirect("/")
#     return render(request, 'edit.html', {'offer': offer})

@login_required
def destroy(request, id):
    offer = get_object_or_404(Offers, id=id)
    offer.delete()
    return redirect("/offers")
