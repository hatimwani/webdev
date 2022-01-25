from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import *


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })

def categories(request):
    if request.method == 'POST':
        category = Category.objects.get(pk = int(request.POST['category']))
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.filter(category=category),
            'message': category.name
        })
    return render(request, 'auctions/categories.html', {
        'categories': Category.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="/login")
def add(request):
    if request.method == "POST":
        title = request.POST['title']
        discription = request.POST['discription']
        image = request.POST['image']
        owner = request.user
        base_price = int(request.POST['base_price'])
        if base_price <= 0:
            return render(request, 'auctions/add.html', {
                "categories": Category.objects.all(),
                "message": "base_price must be greater than 0"
            })
        try:
            category = Category.objects.get(pk = int(request.POST['category']))
            listing = Listing(title=title, discription=discription, image=image, owner=owner, base_price=base_price, category=category)
            listing.save()
        except:
            listing = Listing(title=title, discription=discription, image=image, owner=owner, base_price=base_price)
            listing.save()
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'auctions/add.html', {
        "categories": Category.objects.all(),
    })

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk = int(listing_id))
    in_list = False
    if request.user.is_authenticated:
        for item in  request.user.watchlist.all():
            if listing == item:
                in_list = True
    return render(request, "auctions/listing.html", {
        'listing': listing,
        'in_list': in_list,
        'comments': Comment.objects.filter(listing=listing)
    })

@login_required(login_url="/login")
def watchlist(request):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk = int(request.POST['listing_id']))
        in_list = int(request.POST['in_list'])
        if in_list:
            user.watchlist.remove(listing)
            in_list=0
        else:
            user.watchlist.add(listing)
            in_list=1
        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'in_list': in_list
        })
    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })

@login_required(login_url="/login")
def bid(request):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, pk = int(request.POST['listing_id']))
        amount = int(request.POST['bid_amount'])
        bid = Bid(person=request.user, amount=amount)

        in_list = False
        for item in request.user.watchlist.all():
            if listing == item:
                in_list = True

        if listing.current_bid:
            if int(listing.current_bid.amount) >= int(amount):
                return render(request, "auctions/listing.html", {
                    'listing': listing,
                    'in_list': in_list,
                    'message': "Your Bid must be > current bid",
                    'comments': Comment.objects.filter(listing=listing)
                })
            old_bid = listing.current_bid
            listing.current_bid = bid
            old_bid.delete()

        else:
            if int(listing.base_price) > int(amount):
                return render(request, "auctions/listing.html", {
                    'listing': listing,
                    'in_list': in_list,
                    'message': "Your Bid must be >= current price",
                    'comments': Comment.objects.filter(listing=listing)
                })
            listing.current_bid = bid

        listing.bid_count += 1
        bid.save()
        listing.save()
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'in_list': in_list,
            'comments': Comment.objects.filter(listing=listing)
        })  

@login_required(login_url="/login")
def comment(request):
    listing = get_object_or_404(Listing, pk=int(request.POST['listing_id']))
    text = request.POST['text']
    comment = Comment(person=request.user, listing=listing, text=text)
    comment.save()
    return HttpResponseRedirect(reverse('listing', args=(listing.id,)))

@login_required(login_url="/login")
def close_bid(request):
    listing = get_object_or_404(Listing, pk=int(request.POST['listing_id']))
    if listing.owner != request.user:
        raise Http404
    else:
        listing.is_active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing', args=(listing.id,)))