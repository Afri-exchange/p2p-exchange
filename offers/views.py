from django.shortcuts import render, redirect

# Create your views here.
from offers.forms import OfferForm
from offers.models import Offers
# Create your views here.


def emp(request):
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('/')
            except:
                pass
    else:
        form = OfferForm()
    return render(request, 'index.html', {'form': form})


def show(request):
    offers = Offers.objects.all()
    return render(request, "show.html", {'offers': offers})


def edit(request, id):
    offer = Offers.objects.get(id=id)
    return render(request, 'edit.html', {'offer': offer})


def update(request, id):
    offer = Offers.objects.get(id=id)
    form = OfferForm(request.POST, instance=offer)
    if form.is_valid():
        form.save()
        return redirect("/")
    return render(request, 'edit.html', {'offer': offer})


def destroy(request, id):
    offer = Offers.objects.get(id=id)
    offer.delete()
    return redirect("/")
