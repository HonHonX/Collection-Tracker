from django.shortcuts import get_object_or_404
from friends.models import Friend, FriendList
from django.core.mail import send_mail
from django.conf import settings

def get_base_url(request):
    """
    Extracts and returns the base URL from the request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The base URL.
    """
    extracted = tldextract.extract(request.get_host())
    return f"{request.scheme}://{extracted.domain}.{extracted.suffix}"

def send_email(subject, message, recipient_list):
    """
    Sends an email.

    Args:
        subject (str): The subject of the email.
        message (str): The message of the email.
        recipient_list (list): The list of recipients.
    """
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, recipient_list)

def send_invitation_email(friend, request):
    """
    Sends an invitation email to a friend to join the app.

    Args:
        friend (Friend): The friend object.
        request (HttpRequest): The HTTP request object.
    """
    base_url = 'https://wtcollectiontracker.eu.pythonanywhere.com'
    subject = 'Invitation to Join Collection Tracker'
    message = f'Hi,\n\nYou have received a friend request from {friend.user.username} on Collection Tracker. Please join the app using the link below to accept the request:\n\n{base_url}/register/?email={friend.friend_email}\n\nPlease click the link below to confirm the request after registering:\n\n{base_url}/friends/confirm/{friend.friend_email}/{friend.user.username}/\n\nThank you!'
    recipient_list = [friend.friend_email]
    send_email(subject, message, recipient_list)

def send_friend_request_email(friend, request):
    """
    Sends a friend request confirmation email.

    Args:
        friend (Friend): The friend object.
        request (HttpRequest): The HTTP request object.
    """
    base_url = 'https://wtcollectiontracker.eu.pythonanywhere.com'
    subject = 'Friend Request Confirmation'
    message = f'Hi {friend.friend_email},\n\nYou have received a friend request from {friend.user.username}. Please click the link below to confirm the request:\n\n{base_url}/friends/confirm/{friend.friend_email}/{friend.user.username}/\n\nThank you!'
    recipient_list = [friend.friend_email]
    send_email(subject, message, recipient_list)

def remove_friend(user, friend_email):
    """
    Removes a friend relationship between the given user and the friend with the specified email.

    Args:
        user (User): The user who wants to remove the friend.
        friend_email (str): The email of the friend to be removed.
    """
    friend = Friend.objects.filter(user=user, friend_email=friend_email).first()
    if friend:
        reciprocal_friend = Friend.objects.filter(user__email=friend_email, friend_email=user.email).first()
        if reciprocal_friend:
            reciprocal_friend.delete()
        friend.delete()
        # Remove friend from FriendList
        friend_list = get_object_or_404(FriendList, user=user)
        friend_list.friends.remove(friend)

def add_guest_friend(form, user, request):
    """
    Processes the addition of a guest friend. 
    If the friend you want to add is not a registered user, 
    they'll get a friend request in addition to an inviation to join the app.

    Args:
        form (FriendForm): The friend form.
        user (User): The current user.
        request (HttpRequest): The HTTP request object.
    """
    friend = form.save(commit=False)
    friend.user = user
    friend.status = 'guest'
    friend.save()
    send_invitation_email(friend, request)


def create_reciprocal_friend(user, friend_user, status='accepted'):
    """
    Creates reciprocal friend relationships between two users.

    Args:
        user (User): The user object.
        friend_user (User): The friend user object.
        status (str): The status of the friend relationship.
    """
    reciprocal_friend = Friend.objects.filter(user=user, friend_email=friend_user.email).first()
    if reciprocal_friend:
        reciprocal_friend.status = status
        reciprocal_friend.save()
    else:
        reciprocal_friend = Friend(user=user, friend_email=friend_user.email, friend_name=friend_user.username, status=status)
        reciprocal_friend.save()
    return reciprocal_friend

def are_friends(user, friend_user):
    """
    Checks if two users are friends.

    Args:
        user (User): The user object.
        friend_user (User): The friend user object.

    Returns:
        bool: True if the users are friends, False otherwise.
    """
    return Friend.objects.filter(user=user, friend_email=friend_user.email, status='accepted').exists()

