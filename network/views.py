from audioop import add
import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

from .models import Follow, User, Post


def index(request):
    posts = Post.objects.all()
    p = Paginator(posts, 5)
    page = request.GET.get('page')
    post_list = p.get_page(page)
    return render(request, "network/index.html", {
        "post_list": post_list,
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

        
@login_required(login_url="/login")
def add_post(request):
    if request.method == "POST":
        text = request.POST["text"]
        current_post = Post(text=text, date_time=datetime.now(), poster=request.user)
        current_post.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/add.html")

def profile(request, user_id):
    person = get_object_or_404(User, pk = int(user_id))
    posts = Post.objects.filter(poster = person)
    p = Paginator(posts, 5)
    page = request.GET.get('page')
    post_list = p.get_page(page)
    return render(request, "network/profile.html", {
        "post_list": post_list,
        "person": person,
    })

@csrf_exempt
@login_required(login_url="/login")
def follow(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    user_id = data.get("user_id")
    person = get_object_or_404(User, pk=int(user_id))
    add_follower = True
    for follow_object in person.followers.all():
        if follow_object.follower == request.user:
            follow = Follow.objects.get(following=person, follower=request.user)
            follow.delete()
            add_follower = False
    if add_follower:
        follow = Follow(following=person, follower=request.user)
        follow.save()
        
    return JsonResponse({"message": "Follow request handed successfully."}, status=201)

@login_required(login_url="/login")
def following(request):
    posts = []
    following = []
    for follow_object in request.user.following.all():
        following.append(follow_object.following)
    for post in Post.objects.all():
        if post.poster in following:
            posts.append(post)
    p = Paginator(posts, 5)
    page = request.GET.get('page')
    post_list = p.get_page(page)
    return render(request, "network/index.html", {
        "post_list": post_list,
    })

@csrf_exempt
@login_required(login_url="/login")
def like(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    data = json.loads(request.body)
    post_id = int(data.get("post_id"))
    post = get_object_or_404(Post, pk=post_id)
    if post in request.user.liked_posts.all():
        post.like_count -= 1
        post.likers.remove(request.user)
    else:
        post.likers.add(request.user)
        post.like_count += 1
    post.save()
    return JsonResponse({"message": "liked successfully."}, status=201)


@login_required(login_url="/login")
def edit(request, post_id):
    post = get_object_or_404(Post, pk=int(post_id))
    if request.method == "POST":
        post.text = request.POST["text"]
        post.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/edit.html", {
        "post": post,
    })
    