from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from collection.models import Album, UserAlbumWishlist, UserAlbumCollection
from .models import Friend, FriendList, SharingToken
from .forms import FriendForm
import uuid

@login_required
def friends_view(request):
    user = request.user
    user_token, created = SharingToken.objects.get_or_create(user=user)
    if request.method == 'POST':
        if 'remove_friend' in request.POST:
            friend_email = request.POST.get('friend_email')
            friend = Friend.objects.filter(user=request.user, friend_email=friend_email).first()
            if friend:
                reciprocal_friend = Friend.objects.filter(user__email=friend_email, friend_email=request.user.email).first()
                if reciprocal_friend:
                    reciprocal_friend.delete()
                friend.delete()
                # Remove friend from FriendList
                friend_list = FriendList.objects.get(user=request.user)
                friend_list.friends.remove(friend)
            return redirect('friends_view')
        else:
            form = FriendForm(request.POST)
            if form.is_valid():
                friend_email = form.cleaned_data['friend_email']
                friend_user = User.objects.filter(email=friend_email).first()
                if friend_user and friend_user != request.user:
                    friend = Friend(user=request.user, friend_email=friend_email, friend_name=friend_user.username, status='pending')
                    friend.save()
                    reciprocal_friend = Friend(user=friend_user, friend_email=request.user.email, friend_name=request.user.username, status='pending')
                    reciprocal_friend.save()
                    send_friend_request_email(friend)
                else:
                    friend = form.save(commit=False)
                    friend.user = request.user
                    friend.status = 'guest'
                    friend.save()
                    send_invitation_email(friend)
                return redirect('friends_view')
    else:
        form = FriendForm()
    
    friends = Friend.objects.filter(user=request.user).exclude(friend_email=request.user.email)
    return render(request, 'friends/friends.html', {'form': form, 'friends': friends, 'token': user_token.token})

def send_invitation_email(friend):
    subject = 'Invitation to Join Collection Tracker'
    message = f'Hi,\n\nYou have received a friend request from {friend.user.username} on Collection Tracker. Please join the app using the link below to accept the request:\n\nhttp://localhost:8000/register/?email={friend.friend_email}\n\nPlease click the link below to confirm the request after registering:\n\nhttp://localhost:8000/friends/confirm/{friend.friend_email}/{friend.user.username}/\n\nThank you!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [friend.friend_email]
    send_mail(subject, message, email_from, recipient_list)

@login_required
def confirm_friend_request(request, friend_email, sender_username):
    sender_user = get_object_or_404(User, username=sender_username)
    
    friend = get_object_or_404(Friend, friend_email=friend_email, user=sender_user)
    friend.status = 'accepted'
    friend.save()

    reciprocal_friend = Friend.objects.filter(user=request.user, friend_email=sender_user.email).first()
    if reciprocal_friend:
        reciprocal_friend.status = 'accepted'
        reciprocal_friend.save()
    else:
        # Create reciprocal friend 
        reciprocal_friend = Friend(user=request.user, friend_email=sender_user.email, friend_name=sender_user.username, status='accepted')
        reciprocal_friend.save()
                
    # Add both friends to each other's FriendList
    friend_list, created = FriendList.objects.get_or_create(user=request.user)
    friend_list.friends.add(friend)
    reciprocal_friend_list, created = FriendList.objects.get_or_create(user=sender_user)
    reciprocal_friend_list.friends.add(reciprocal_friend)
    return redirect('friends_view')

def send_friend_request_email(friend):
    subject = 'Friend Request Confirmation'
    message = f'Hi {friend.friend_email},\n\nYou have received a friend request from {friend.user.username}. Please click the link below to confirm the request:\n\nhttp://localhost:8000/friends/confirm/{friend.friend_email}/{friend.user.username}/\n\nThank you!'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [friend.friend_email]
    send_mail(subject, message, email_from, recipient_list)

def user_wishlist(request, username):
    user = get_object_or_404(User, username=username)
    if not Friend.objects.filter(user=request.user, friend_email=user.email, status='accepted').exists():
        return render(request, 'friends/not_friends.html')
    wishlist = Album.objects.filter(useralbumwishlist__user=user)
    return render(request, 'friends/user_wishlist.html', {'user': user, 'wishlist': wishlist})

def user_collection(request, username):
    user = get_object_or_404(User, username=username)
    if not Friend.objects.filter(user=request.user, friend_email=user.email, status='accepted').exists():
        return render(request, 'friends/not_friends.html')
    collection = Album.objects.filter(useralbumcollection__user=user)
    return render(request, 'friends/user_collection.html', {'user': user, 'collection': collection})

def shared_user_wishlist(request, token):
    user_token = get_object_or_404(SharingToken, token=token)
    user = user_token.user
    wishlist = Album.objects.filter(useralbumwishlist__user=user)
    return render(request, 'friends/user_wishlist.html', {'user': user, 'wishlist': wishlist})

def shared_user_collection(request, token):
    user_token = get_object_or_404(SharingToken, token=token)
    user = user_token.user
    collection = Album.objects.filter(useralbumcollection__user=user)
    return render(request, 'friends/user_collection.html', {'user': user, 'collection': collection})

@login_required
def generate_token(request):
    user = request.user
    user_token, created = SharingToken.objects.get_or_create(user=user)
    if not created:
        user_token.token = uuid.uuid4()
        user_token.save()
    return JsonResponse({'token': str(user_token.token)})

