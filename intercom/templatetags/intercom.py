import logging
import hashlib
from django.template import Library, Node
from django.conf import settings
from django.utils import simplejson
from django.utils.importlib import import_module

register = Library()
log = logging.getLogger(__name__)

INTERCOM_APPID = getattr(settings, 'INTERCOM_APPID', None)
INTERCOM_SECURE_KEY = getattr(settings, 'INTERCOM_SECURE_KEY', None)
INTERCOM_ENABLE_INBOX = getattr(settings, 'INTERCOM_ENABLE_INBOX', True)
INTERCOM_ENABLE_INBOX_COUNTER = getattr(settings, 'INTERCOM_ENABLE_INBOX_COUNTER', True)
INTERCOM_INBOX_CSS_SELECTOR = getattr(settings, 'INTERCOM_INBOX_CSS_SELECTOR', '#Intercom')
INTERCOM_CUSTOM_DATA_CLASSES = getattr(settings, 'INTERCOM_CUSTOM_DATA_CLASSES', None)

def my_import(name):
    """ dynamic importing """
    module, attr = name.rsplit('.', 1)
    mod = __import__(module, fromlist=[attr])
    klass = getattr(mod, attr)
    return klass()

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

    if INTERCOM_APPID is None:
        log.warning("INTERCOM_APPID isn't setup correctly in your settings")

    # make sure INTERCOM_APPID is setup correct and user is authenticated
    if INTERCOM_APPID and request.user and request.user.is_authenticated():
        email = request.user.email
        user_created = request.user.date_joined
        name = request.user.username
        user_hash = None
        use_counter = 'true' if INTERCOM_ENABLE_INBOX_COUNTER else 'false'

        custom_data = {}
        if INTERCOM_CUSTOM_DATA_CLASSES:
            for custom_data_class in INTERCOM_CUSTOM_DATA_CLASSES:
                try:
                    cd_class = my_import(custom_data_class)
                    # check make sure the class has a custom_data method.
                    if cd_class and hasattr(cd_class, 'custom_data'):
                        # call custom_data method and update the custom_data dict
                        custom_data.update(cd_class.custom_data(request.user))
                    else:
                        log.warning("%s doesn't have a custom_data method, skipping." % custom_data_class)
                except ImportError, e:
                    log.warning("%s couldn't be imported, there was an error during import. skipping. %s" % (custom_data_class,e) )

            custom_data = simplejson.dumps(custom_data)

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
                "enable_inbox": INTERCOM_ENABLE_INBOX,
                "use_counter": use_counter,
                "css_selector" : INTERCOM_INBOX_CSS_SELECTOR,
                "custom_data": custom_data,
                "user_hash" : user_hash}

    # if it is here, it isn't a valid setup, return False to not show the tag.
    return {"INTERCOM_IS_VALID" : False}
    