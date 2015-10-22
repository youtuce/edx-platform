"""
Platform support for Programs.

This package is a thin wrapper around interactions with the Programs service,
supporting learner- and author-facing features involving that service
if and only if the service is deployed in the Open edX installation.

To ensure maximum separation of concerns, and a minimum of interdependencies,
this package should be kept small, thin, and stateless.
"""
import json
import logging
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from provider.oauth2.models import AccessToken, Client
from provider.utils import now


log = logging.getLogger(__name__)


def get_id_token(username):
    """
    Generates a JWT ID-Token, using or creating user's OAuth access token.

    Returns a string containing the signed JWT value.

    TODO: this closely duplicates the function in edxnotes/helpers.py - we
    should move it to a shared place (and add a client name parameter)

    TODO: there's a circular import problem somewhere which is why we do
    the oidc import inside of this function.
    """
    import oauth2_provider.oidc as oidc  # avoid circular import problem

    try:
        client = Client.objects.get(name="programs")
    except Client.DoesNotExist:
        raise ImproperlyConfigured("OAuth2 Client with name 'programs' is not present in the DB")

    access_tokens = AccessToken.objects.filter(
        client=client,
        user__username=username,
        expires__gt=now()
    ).order_by('-expires')

    if access_tokens:
        access_token = access_tokens[0]
    else:
        access_token = AccessToken(client=client, user=username)
        access_token.save()

    id_token = oidc.id_token(access_token)
    secret = id_token.access_token.client.client_secret
    return id_token.encode(secret)


def get_course_programs_for_dashboard(username, course_keys):
    """
    Given a username and an iterable of course keys, find all
    the programs relevant to the user's dashboard and return them in a
    dictionary keyed by the course_key.

    username is a string coming from the currently-logged-in user's name
    dashboard enrollments is an iterable of course keys

    TODO: move this to a utils module outside of __init__
    TODO: ultimately, we will want this function to be versioned, since
    it assumes v1 of the programs API.  This is not critical for our
    initial release.
    """
    # unicode-ify the course keys for efficient lookup
    course_keys = map(unicode, course_keys)

    # get programs from service.
    # TODO: slumber-based client (i.e. EcommerceApiClient) should be used here
    # That client needs a modification before it can be used - presently
    # it generates the JWT auth header internally, but we need to pass
    # in our own JWT that we are getting from the oauth2 provider (using
    # the `get_id_token` function)
    response = requests.get(
        url='{}programs/'.format(settings.PROGRAMS_API_URL),
        headers={'Authorization': 'JWT {}'.format(get_id_token(username))}
    )
    data = json.loads(response.content)
    programs = data['results']

    # reindex the result from pgm -> course code -> course run
    #  to
    # course run -> program, ignoring course runs not present in the dashboard enrollments
    course_programs = {}
    for program in programs:
        for course_code in program['course_codes']:
            for run in course_code['run_modes']:
                if run['course_key'] in course_keys:
                    course_programs[run['course_key']] = program

    return course_programs
