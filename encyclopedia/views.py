from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from . import util
from markdown2 import markdown
from django import forms
from django.urls import reverse
from random import randint


class SearchForm(forms.Form):
    q = forms.CharField()

class CreatePageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'id':'input_field', 'placeholder':'title/name of file'}))
    text = forms.CharField(label="", widget=forms.Textarea(attrs={'id':'text_area', 'placeholder':'markdown'}))

def index(request):
    titles = util.list_entries()
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["q"].lower()
            for name in titles:
                if title.lower() == name.lower():
                    return HttpResponseRedirect(reverse('entry_page', kwargs={'title': title}))
            else:
                titlesb = []
                for name in titles:
                    if name.lower().find(title) != -1:
                        titlesb.append(name)
                titles = titlesb
    return render(request, "encyclopedia/index.html", {
        "entries": titles
    })

def entry_page(request, title):
    titles = util.list_entries()
    for name in titles:
        if title.capitalize() == name.capitalize():
            page = util.get_entry(title)
            page = str(markdown(page))
            return render(request, 'encyclopedia/page.html', {
                'page': page,
                'title': title,
            })
    raise Http404

def create_page(request):
    if request.method == "POST":
        form = CreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['text']
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("index"))
        return render(request, 'encyclopedia/create_page.html', {
            "form" : form,
        })

    return render(request, 'encyclopedia/create_page.html', {
        "form" : CreatePageForm()
    })

def edit_page(request, title):
    form = CreatePageForm(initial={
        'title': title,
        'text': util.get_entry(title)
    })
    return render(request, 'encyclopedia/edit.html', {
        'form': form,
        'title': title,
    })


def random(request):
    titles = util.list_entries()
    title = titles[randint(0, len(titles) - 1)]
    return HttpResponseRedirect(reverse("entry_page", kwargs={'title':title}))