from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from .models import User, Bid, Listing, Comment

# Register your models here.

admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Listing)
admin.site.register(Comment)