from django.contrib import admin
from .models import *
# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    exclude = ('current_bid', 'bid_count', 'is_active')
admin.site.register(Bid)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)