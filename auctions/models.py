from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True)

class Bid(models.Model):
    person = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bids')
    amount = models.IntegerField()

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return f"{self.id}: {self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    discription = models.TextField(max_length=128)
    image = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    base_price = models.IntegerField()
    current_bid = models.OneToOneField(Bid, on_delete=models.SET_NULL, null=True, unique=True, related_name='listing', blank=True)
    bid_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}: {self.title}"
class Comment(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=512)