from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from collection.models import Album, UserAlbumWishlist, UserAlbumCollection
from .models import Friend, FriendList, SharingToken
from .forms import FriendForm
from utils.friend_helpers import get_base_url, remove_friend, add_guest_friend, send_invitation_email, create_reciprocal_friend, are_friends, send_email, send_friend_request_email
import uuid


@login_required
def friends_view(request):
    """
    Handles the friends view, including adding and removing friends.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered friends view.
    """
    user = request.user
    user_token, created = SharingToken.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        if 'remove_friend' in request.POST:
            friend_email = request.POST.get('friend_email')
            remove_friend(user, friend_email)
            return redirect('friends_view')
        else:
            form = FriendForm(request.POST)
            if form.is_valid():
                friend_email = form.cleaned_data['friend_email']
                friend_user = User.objects.filter(email=friend_email).first()
                if friend_user and friend_user != user:
                    Friend.objects.bulk_create([
                        Friend(user=user, friend_email=friend_email, friend_name=friend_user.username, status='pending'),
                        Friend(user=friend_user, friend_email=user.email, friend_name=user.username, status='pending')
                    ])
                    send_friend_request_email(friend_user, request)
                else:
                    handle_guest_friend(form, user, request)
                return redirect('friends_view')
    else:
        form = FriendForm()
    
    friends = Friend.objects.filter(user=user).exclude(friend_email=user.email).select_related('user')
    return render(request, 'friends/friends.html', {'form': form, 'friends': friends, 'token': user_token.token})

@login_required
def confirm_friend_request(request, friend_email, sender_username):
    """
    Confirms a friend request and updates the friend status to 'accepted'.

    Args:
        request (HttpRequest): The HTTP request object.
        friend_email (str): The email of the friend.
        sender_username (str): The username of the sender.

    Returns:
        HttpResponse: Redirects to the friends view.
    """
    sender_user = get_object_or_404(User, username=sender_username)
    
    friend = get_object_or_404(Friend, friend_email=friend_email, user=sender_user)
    friend.status = 'accepted'
    friend.save()

    reciprocal_friend = create_reciprocal_friend(request.user, sender_user)
                
    # Add both friends to each other's FriendList
    friend_list, created = FriendList.objects.get_or_create(user=request.user)
    friend_list.friends.add(friend)
    reciprocal_friend_list, created = FriendList.objects.get_or_create(user=sender_user)
    reciprocal_friend_list.friends.add(reciprocal_friend)
    return redirect('friends_view')

def friend_wishlist(request, username):
    """
    Displays the wishlist of a user if they are friends with the current user.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the user whose wishlist is to be displayed.

    Returns:
        HttpResponse: The rendered user wishlist view.
    """
    user = get_object_or_404(User, username=username)
    if not are_friends(request.user, user):
        return render(request, 'friends/not_friends.html')
    wishlist = Album.objects.filter(useralbumwishlist__user=user)
    return render(request, 'friends/user_wishlist.html', {'user': user, 'wishlist': wishlist})

def friend_collection(request, username):
    """
    Displays the collection of a user if they are friends with the current user.

    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the user whose collection is to be displayed.

    Returns:
        HttpResponse: The rendered user collection view.
    """
    user = get_object_or_404(User, username=username)
    if not are_friends(request.user, user):
        return render(request, 'friends/not_friends.html')
    collection = Album.objects.filter(useralbumcollection__user=user)
    return render(request, 'friends/user_collection.html', {'user': user, 'collection': collection})

def shared_user_wishlist(request, token):
    """
    Displays the wishlist of a user based on a sharing token.

    Args:
        request (HttpRequest): The HTTP request object.
        token (str): The sharing token.

    Returns:
        HttpResponse: The rendered user wishlist view.
    """
    user_token = get_object_or_404(SharingToken, token=token)
    user = user_token.user
    wishlist = Album.objects.filter(useralbumwishlist__user=user)
    return render(request, 'friends/user_wishlist.html', {'user': user, 'wishlist': wishlist})

def shared_user_collection(request, token):
    """
    Displays the collection of a user based on a sharing token.

    Args:
        request (HttpRequest): The HTTP request object.
        token (str): The sharing token.

    Returns:
        HttpResponse: The rendered user collection view.
    """
    user_token = get_object_or_404(SharingToken, token=token)
    user = user_token.user
    collection = Album.objects.filter(useralbumcollection__user=user)
    return render(request, 'friends/user_collection.html', {'user': user, 'collection': collection})

@login_required
def generate_token(request):
    """
    Generates a new sharing token for the current user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the new token.
    """
    user = request.user
    user_token, created = SharingToken.objects.get_or_create(user=user)
    if not created:
        user_token.token = uuid.uuid4()
        user_token.save()
    return JsonResponse({'token': str(user_token.token)})








