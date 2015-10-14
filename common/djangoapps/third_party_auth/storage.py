"""
A custom Storage for python-social-auth that is Django 1.8-compatible.
"""

from social.apps.django_app.default.models import UserSocialAuth, DjangoStorage


class DjangoUserSocialAuth(UserSocialAuth):
    class Meta:
        proxy = True

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        if not isinstance(uid, six.string_types):
            uid = str(uid)
        if hasattr(transaction, 'atomic'):
            # In Django versions that have an "atomic" transaction decorator / context
            # manager, there's a transaction wrapped around this call.
            # If the create fails below due to an IntegrityError, ensure that the transaction
            # stays undamaged by wrapping the create in an atomic.
            with transaction.atomic():
                social_auth = cls.objects.create(user=user, uid=uid, provider=provider)
        else:
            social_auth = cls.objects.create(user=user, uid=uid, provider=provider)
        return social_auth


class LatestDjangoStorage(DjangoStorage):
    """
    A DjangoStorage compatible with Django 1.8 transactions.
    """
    user = DjangoUserSocialAuth
