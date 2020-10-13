from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.db import IntegrityError
from django.db.models import Max, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm

from django import forms

from .models import User, Listing, Bid, Comment



Categories=["", "Electronics","Fashion","Home","Toys"]


class BidForm(forms.Form):
    newBid=forms.FloatField(label="")

# class ClosedForm(ModelForm):
#     class Meta:
#         model=Listing
#         fields=["item_isActive"]
#         labels={"item_isActive": "closer the listing"}

class CommentForm(ModelForm):
    class Meta:
        model=Comment
        fields=["com_Title", "com_Contents"]
        labels={"com_Title":"Title", "com_Contents":"Comment"}



def index(request):

    temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).filter(item_isActive=True).order_by("item_id")
    paginator=Paginator(temp_l,5)
    page_number=request.GET.get("page")
    page_obj=paginator.get_page(page_number)

    return render(request,"auctions/index.html",{
        # "lists":temp_l
        "page_obj":page_obj,
    })

    # return render(request, "auctions/index.html",{
    #     "lists":Listing.objects.all()
    # })



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

def create(request):

    if request.method =="POST":
        Name=request.POST["Name"]
        Price=request.POST["Price"]
       
        if Name=="" or Price=="":
            return render(request,"auctions/create.html",{
                "message":"Please entry the Name and Price of the Listing"
            })

        item=Listing(item_Name=Name, item_StarBid=Price, item_Description=request.POST["Description"], item_URL=request.POST["URL"], 
        item_Category=request.POST["Category"],item_isActive=True, item_Owner=request.user)
        item.save()

        return redirect("index")

    else:
        return render(request, "auctions/create.html",{
            "Categories": Categories
        })

def listing_Page(request, item_id):
     
    temp_comment=Comment.objects.filter(com_Listing=item_id).order_by("com_id")
    paginator = Paginator(temp_comment, 2)
    page_obj=paginator.get_page(1)



    # print (request.user.user_Watchlist.filter(item_id__exact=item_id))
    if request.user.user_Watchlist.filter(item_id__exact=item_id).exists():  
        watched=True
    else:
        watched=False



    message=""


    
    if request.method=="POST":

        # print(request.POST)
       

        if "bid" in request.POST :

            temp_bid=BidForm(request.POST)
            if temp_bid.is_valid():
           
                temp_bid=temp_bid.cleaned_data["newBid"]
                sB=Listing.objects.get(pk=item_id).item_StarBid
                cB=Bid.objects.filter(bid_Listing=item_id)

                if(temp_bid < sB and not cB.exists()) :
                    message="You bid must at least as large as the starting bid"
                elif (cB.exists() and temp_bid <= cB.last().bid_Bids):
                    message="You bid must greater then the current price"
                else:
                    b=Bid(bid_Bids=temp_bid, bid_User=request.user, bid_Listing=Listing.objects.get(pk=item_id))
                    b.save()
                    message="Successful bidding"
                    
                # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)
                # return render(request,"auctions/listing_Page.html",{
                #     "l":temp_l,
                #     "form_Bid":BidForm,
                #     "message":message,
                #     "page_obj":page_obj,
                #     "form_Comment":CommentForm,
                # })

        elif "closed" in request.POST:

            Listing.objects.filter(pk=item_id).update(item_isActive=False)
            Listing.objects.filter(pk=item_id).update(item_Winner=Bid.objects.filter(bid_Listing=item_id).last().bid_User)
            message="You listing has beed closed."
            
            # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)  
            # return render(request,"auctions/listing_Page.html",{
            #     "l":temp_l,
            #     "form_Bid":BidForm,
            #     "message":message,
            #     "page_obj":page_obj,
            #      "form_Comment":CommentForm,
            # })

        elif "watch" in request.POST:
            request.user.user_Watchlist.add(Listing.objects.get(pk=item_id))

            return render(request,"auctions/watchlist.html",{
                "watched":request.user.user_Watchlist.all()
            })

        elif "unwatch" in request.POST:
            request.user.user_Watchlist.remove(Listing.objects.get(pk=item_id))
            watched=False

   
        # elif request.POST['action'] == 'p':// for use 'action' in ajax post
        elif "p" in request.POST:
            page=request.POST.get("page")

            # print("page")
            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)
            # return render(request,"auctions/listing_Page.html",{
            #     "l":temp_l,
            #     "form_Bid":BidForm,
            #     "page_obj":page_obj,
            #     "form_Comment":CommentForm,
            # })


            # data=serializers.serialize('json', page_obj)
            # return HttpResponse(data,content_type="application/json")
        
        
        elif "com" in request.POST:
            # print("go to comment")
            temp_com=CommentForm(request.POST)
            if temp_com.is_valid():
                # print(temp_com)
                c=Comment(com_User=request.user, com_Listing=Listing.objects.get(pk=item_id), 
                com_Title=temp_com.cleaned_data["com_Title"], com_Contents=temp_com.cleaned_data["com_Contents"] ,)
                c.save()

            
            temp_comment=Comment.objects.filter(com_Listing=item_id).order_by("com_id")
            paginator = Paginator(temp_comment, 2)
            page_obj=paginator.get_page(paginator.num_pages)
            # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)
            # return render(request,"auctions/listing_Page.html",{
            #     "l":temp_l,
            #     "form_Bid":BidForm, 
            #     "page_obj":page_obj,
            #     "form_Comment":CommentForm,
            #  })

        # ************for more post request****************#
        else:
           pass 

    
        temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)
        return render(request,"auctions/listing_Page.html",{
                "l":temp_l,
                "form_Bid":BidForm,
                "message":message,
                "page_obj":page_obj,
                "form_Comment":CommentForm,
                "wted":watched,
            })

    
            
    else:
        
        temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).get(pk=item_id)
        return render(request,"auctions/listing_Page.html",{
            "l":temp_l,
            "form_Bid":BidForm,
            "page_obj":page_obj,
            "form_Comment":CommentForm,
            "wted":watched,
        })



def watchlist(request):
    if request.method=="POST":
        # print(request.POST)
        temp_item=Listing.objects.get(pk=int(request.POST.get("item_id")))
        request.user.user_Watchlist.remove(temp_item)
        watched=request.user.user_Watchlist.all().annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids"))
        return render(request,"auctions/watchlist.html",{
            "watched":watched,
        })

    
    
    else:
        watched=request.user.user_Watchlist.all().annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids"))
        return render(request,"auctions/watchlist.html",{
            "watched":watched,
        })




def category(request):
    # print(Categories)
    # while "" in Categories:
    #     Categories.remove("")
    ctgory=[i for i in Categories if i!=""]
    return render(request, "auctions/category.html",{
        "ctgory":ctgory,
    })



def result(request,category):

    if category=="0":
        # __isnull=True means no json
        # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).filter(item_Category__isnull=True)    
        # =None specify that the json hase value "null"  
        # temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).filter(item_Category=None)


        temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).filter(item_Category="")


    else:
        temp_l=Listing.objects.annotate(currentPrice=Max("bid__bid_Bids"),bidNo=Count("bid__bid_Bids")).filter(item_Category=category)
        
    return render(request,"auctions/result.html",{
        "category":category,
        "l_result":temp_l,
    })
    