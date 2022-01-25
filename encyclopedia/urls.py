from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry_page, name="entry_page"),
    path("create_page", views.create_page, name="create_page"),
    path("wiki/<str:title>/edit", views.edit_page, name="edit_page"),
    path("random", views.random, name="random"),
]
