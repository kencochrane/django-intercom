import logging
import hashlib
import json
from django.template import Library, Node
from django.conf import settings
from django.utils.importlib import import_module

register = Library()
log = logging.getLogger(__name__)

INTERCOM_APPID = getattr(settings, 'INTERCOM_APPID', None)
INTERCOM_SECURE_KEY = getattr(settings, 'INTERCOM_SECURE_KEY', None)
INTERCOM_ENABLE_INBOX = getattr(settings, 'INTERCOM_ENABLE_INBOX', True)
INTERCOM_ENABLE_INBOX_COUNTER = getattr(settings, 'INTERCOM_ENABLE_INBOX_COUNTER', True)
INTERCOM_INBOX_CSS_SELECTOR = getattr(settings, 'INTERCOM_INBOX_CSS_SELECTOR', '#Intercom')
INTERCOM_USER_DATA_CLASS = getattr(settings, 'INTERCOM_USER_DATA_CLASS', None)
INTERCOM_CUSTOM_DATA_CLASSES = getattr(settings, 'INTERCOM_CUSTOM_DATA_CLASSES', None)
INTERCOM_COMPANY_DATA_CLASS = getattr(settings, 'INTERCOM_COMPANY_DATA_CLASS', None)
INTERCOM_DISABLED = getattr(settings, 'INTERCOM_DISABLED', False)

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

    # Short-circuit if the tag is disabled.
    if INTERCOM_DISABLED is True:
        return {"INTERCOM_IS_VALID" : False}

    # Ensure that the context contains a value for the request key before
    # continuing.
    if not context.has_key('request'):
        return {"INTERCOM_IS_VALID" : False}

    request = context['request']

    if INTERCOM_APPID is None:
        log.warning("INTERCOM_APPID isn't setup correctly in your settings")

    # make sure INTERCOM_APPID is setup correct and user is authenticated
    if INTERCOM_APPID and request.user and request.user.is_authenticated():
        user_data = {}
        if INTERCOM_USER_DATA_CLASS:
            try:
                ud_class = my_import(INTERCOM_USER_DATA_CLASS)
                # make sure the class has a user_data method
                if ud_class and hasattr(ud_class, 'user_data'):
                    user_data = ud_class.user_data(request.user)
            except ImportError, e:
                log.warning("%s couldn't be imported, there was an error during import. skipping. %s" % (INTERCOM_USER_DATA_CLASS, e) )

        user_id = user_data.get('user_id', request.user.id)
        email = user_data.get('email', request.user.email)
        user_created = user_data.get('user_created', request.user.date_joined)
        try:
            name = user_data.get('name', request.user.username)
        except:
            name = user_data.get('name', request.user.get_username())
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

            custom_data = json.dumps(custom_data)

        company_data = {}
        if INTERCOM_COMPANY_DATA_CLASS:
            try:
                cd_class = my_import(INTERCOM_COMPANY_DATA_CLASS)
                # make sure the class has a company_data method
                if cd_class and hasattr(cd_class, 'company_data'):
                    data = cd_class.company_data(request.user)
                    if all (k in data for k in ('id', 'name', 'created_at')):
                        company_data.update(data)
                    else:
                        log.warning("company method of %s doesn't return all of the required dictionary keys (id, name, created_at), skipping." % INTERCOM_COMPANY_DATA_CLASS)
                else:
                    log.warning("%s doesn't have a company_data method, skipping." % INTERCOM_COMPANY_DATA_CLASS)
            except ImportError, e:
                log.warning("%s couldn't be imported, there was an error during import. skipping. %s" % (INTERCOM_COMPANY_DATA_CLASS, e) )

            company_data = json.dumps(company_data)

        # this is optional, if they don't have the setting set, it won't use.
        if INTERCOM_SECURE_KEY is not None:
            m = hashlib.sha1()
            user_hash_key = "%s%s" % (INTERCOM_SECURE_KEY, user_id)
            m.update(user_hash_key)
            user_hash = m.hexdigest()

        return {"INTERCOM_IS_VALID" : True,
                "intercom_appid":INTERCOM_APPID,
                "email_address": email,
                "user_id": user_id,
                "user_created": user_created,
                "name": name,
                "enable_inbox": INTERCOM_ENABLE_INBOX,
                "use_counter": use_counter,
                "css_selector" : INTERCOM_INBOX_CSS_SELECTOR,
                "custom_data": custom_data,
                "company_data": company_data,
                "user_hash" : user_hash}

    # if it is here, it isn't a valid setup, return False to not show the tag.
    return {"INTERCOM_IS_VALID" : False}
    
