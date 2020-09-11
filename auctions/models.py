from django.contrib.auth.models import AbstractUser
from django.db import models




class Listing(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_Name = models.CharField(max_length=64)
    item_StarBid = models.FloatField()
    item_Description = models.TextField(blank=True,null=True)
    item_URL = models.URLField() 
    item_Category = models.CharField(max_length=64)
    item_Owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="owner")
    item_Winner = models.ForeignKey("User", on_delete=models.CASCADE, blank=True, null=True, related_name="winner")
    item_isActive = models.BooleanField()

    def __str__(self):
        return f"{self.item_id}. {self.item_Name}"


class User(AbstractUser):
    # user_id=models.AutoField(primary_key=True)
    user_Watchlist = models.ManyToManyField(Listing, blank=True, related_name="watched")


class Bid(models.Model):
    bid_id = models.AutoField(primary_key=True)
    bid_Bids = models.FloatField(blank=True,null=True)
    bid_User = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_Listing  = models.ForeignKey(Listing, on_delete=models.CASCADE)

class Comment(models.Model):
    com_id = models.AutoField(primary_key=True)
    com_User = models.ForeignKey(User, on_delete=models.CASCADE)
    com_Listing = models.ForeignKey(Listing,on_delete=models.CASCADE)
    com_Title = models.CharField(max_length=128)
    com_Contents = models.TextField()

