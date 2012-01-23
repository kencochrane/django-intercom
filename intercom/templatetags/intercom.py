import logging
import hashlib
from django.template import Library, Node
from django.conf import settings

register = Library()
log = logging.getLogger(__name__)

@register.inclusion_tag('intercom/intercom_tag.html', takes_context=True)
def intercom_tag(context):
    """ This tag will check to see if they have the INTERCOM_APPID setup
        correctly in the django settings and also check if the user is logged
        in, if so then it will pass the data along to the intercom_tag template
        to be displayed.
        
        If something isn't perfect we will return False, which will then not 
        install the javascript since it isn't needed.
        
        You could do this without using a template tag, but I felt this was a
        little cleaner then doing everything in the template.
    """

    request = context['request']

    INTERCOM_APPID = getattr(settings, 'INTERCOM_APPID', None)
    INTERCOM_SECURE_KEY = getattr(settings, 'INTERCOM_SECURE_KEY', None)
    
    if INTERCOM_APPID is None:
        log.warning("INTERCOM_APPID isn't setup correctly in your settings")

    # make sure INTERCOM_APPID is setup correct and user is authenticated
    if INTERCOM_APPID and request.user and request.user.is_authenticated():
        email = request.user.email
        user_created = request.user.date_joined
        name = request.user.username
        user_hash = None
        
        # this is optional, if they don't have the setting set, it won't use.
        if INTERCOM_SECURE_KEY is not None:
            m = hashlib.sha1()
            user_hash_key = "%s%s" % (INTERCOM_SECURE_KEY, email)
            m.update(user_hash_key)
            user_hash = m.hexdigest()

        return {"INTERCOM_IS_VALID" : True,
                "intercom_appid":INTERCOM_APPID,
                "email_address": email,
                "user_created": user_created,
                "name": name,
                "user_hash" : user_hash}

    # if it is here, it isn't a valid setup, return False to not show the tag.
    return {"INTERCOM_IS_VALID" : False}
    