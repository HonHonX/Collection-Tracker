# based on https://github.com/csev/dj4e-samples/blob/main/dj4e-samples/github_settings-dist.py
# modified with ChatGPT and code from tracker

# Copy this file to github_settings.py (don't check it into github)

# Go to https://github.com/settings/apps

# Add a New OAuth2 App 

# Using PythonAnywhere here are some settings:

# Application name: CollectionTracker PythonAnywhere
# Homepage Url: https://wtcollectiontracker.eu.pythonanywhere.com
# Application Description: Developing a web application
# Authorization callback URL: https://wtcollectiontracker.eu.pythonanywhere.com/oauth/complete/github/

# Also on PythonAnywhere, go into the Web tab and enable "Force HTTPS"
# so you don't get a redirect URI mismatch.

# Then copy the client_key and secret to this file

from decouple import config
##import socket
## fixed for pythonanywhere:
# the hostname cannot be called reliably via pythonanywhere and github, 
# although the hostname is correct, 
# the "else" branch is chosen and the data is used for localhost

# Determine the hostname
##hostname = socket.gethostname()

# Check if you're on localhost or production based on the hostname or environment variable
##if hostname == 'wtcollectiontracker.eu.pythonanywhere.com':

SOCIAL_AUTH_GITHUB_KEY = config('SOCIAL_AUTH_GITHUB_KEY_PyA')
SOCIAL_AUTH_GITHUB_SECRET = config('SOCIAL_AUTH_GITHUB_SECRET_PyA')

##else:
    # If you are running on localhost, here are some settings:

    # Application name: Collectiontracker Localhost
    # Homepage Url: http://localhost:8000
    # Application Description: Developing a web application
    # Authorization callback URL: http://127.0.0.1:8000/oauth/complete/github/

##    SOCIAL_AUTH_GITHUB_KEY = config('SOCIAL_AUTH_GITHUB_KEY_LOCAL')
##    SOCIAL_AUTH_GITHUB_SECRET = config('SOCIAL_AUTH_GITHUB_SECRET_LOCAL')

# Ask for the user's email (don't edit this line)
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

# Note you may not get email for github users that don't make their
# email public - that is OK

# For detail: https://python-social-auth.readthedocs.io/en/latest/configuration/django.html

# Using ngrok is hard because the url changes every time you start ngrok