# -*- coding: utf-8 -*-
from __future__ import (print_function, division, absolute_import,
                        unicode_literals)

import datetime
import logging
import hashlib
import hmac
import json
from django.template import Library

from django_intercom.settings import (INTERCOM_APPID, INTERCOM_ENABLE_INBOX,
                                      INTERCOM_INBOX_CSS_SELECTOR, INTERCOM_DISABLED,
                                      INTERCOM_USER_DATA_CLASS,
                                      INTERCOM_INCLUDE_USERID,
                                      INTERCOM_ENABLE_INBOX_COUNTER,
                                      INTERCOM_CUSTOM_DATA_CLASSES,
                                      INTERCOM_COMPANY_DATA_CLASS,
                                      INTERCOM_SECURE_KEY,
                                      INTERCOM_UNAUTHENTICATED_USER_EMAIL)

register = Library()
log = logging.getLogger(__name__)

DEFAULT_USER = {
    "INTERCOM_IS_VALID": True,
    "intercom_appid": INTERCOM_APPID,
    "email_address": None,
    "user_id": None,
    "user_created": datetime.datetime.utcnow(),
    "name": None,
    "enable_inbox": INTERCOM_ENABLE_INBOX,
    "use_counter": 'false',
    "css_selector": INTERCOM_INBOX_CSS_SELECTOR,
    "custom_data": {},
    "company_data": {},
    "user_hash": None,
}


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
        return {"INTERCOM_IS_VALID": False}

    # Ensure that the context contains a value for the request key before
    # continuing.
    if 'request' not in context:
        return {"INTERCOM_IS_VALID": False}

    request = context['request']

    if INTERCOM_APPID is None:
        log.warning("INTERCOM_APPID isn't setup correctly in your settings")

    # make sure INTERCOM_APPID is setup correct and user is authenticated
    if INTERCOM_APPID and request.user and request.user.is_authenticated:
        user_data = {}
        if INTERCOM_USER_DATA_CLASS:
            try:
                ud_class = my_import(INTERCOM_USER_DATA_CLASS)
                # make sure the class has a user_data method
                if ud_class and hasattr(ud_class, 'user_data'):
                    user_data = ud_class.user_data(request.user)
            except ImportError as e:
                log.warning(
                    "%s couldn't be imported, there was an error during"
                    " import. skipping. %s", INTERCOM_USER_DATA_CLASS, e)

        if INTERCOM_INCLUDE_USERID:
            user_id = user_data.get('user_id', request.user.id)
        else:
            user_id = None
        email = user_data.get('email', request.user.email)
        user_created = user_data.get('user_created', request.user.date_joined)
        try:
            name = user_data.get('name', request.user.username)
        except:
            name = user_data.get('name', request.user.get_username())
        user_hash = None
        use_counter = 'true' if INTERCOM_ENABLE_INBOX_COUNTER else 'false'
        custom_data = get_custom_data(request.user)
        company_data = get_company_data(request.user)

        # this is optional, if they don't have the setting set, it won't use.
        if INTERCOM_SECURE_KEY is not None:
            hmac_value = str(user_id) if user_id else email
            user_hash = hmac.new(INTERCOM_SECURE_KEY.encode('utf8'),
                                 hmac_value.encode('utf8'),
                                 digestmod=hashlib.sha256).hexdigest()

        DEFAULT_USER.update({"INTERCOM_IS_VALID": True,
                             "intercom_appid": INTERCOM_APPID,
                             "email_address": email,
                             "user_id": user_id,
                             "user_created": user_created,
                             "name": name,
                             "enable_inbox": INTERCOM_ENABLE_INBOX,
                             "use_counter": use_counter,
                             "css_selector": INTERCOM_INBOX_CSS_SELECTOR,
                             "custom_data": custom_data,
                             "company_data": company_data,
                             "user_hash": user_hash})

    else:
        # unauthenticated
        DEFAULT_USER.update(
            {"INTERCOM_IS_VALID": True,
             "intercom_appid": INTERCOM_APPID,
             "user_id": request.session.session_key,
             "email_address": INTERCOM_UNAUTHENTICATED_USER_EMAIL,
             "name": 'Unknown'}
        )
    # if it is here, it isn't a valid setup, return False to not show the tag.
    return DEFAULT_USER


def get_custom_data(user):
    """
    Get the user custom data from the custom cdata class
    Args:
        user: The Django user

    Returns:
        custom_data(json): the custom data loaded from the class if exists,
        otherwise it is empty
    """
    custom_data = {}
    if INTERCOM_CUSTOM_DATA_CLASSES is None:
        return json.dumps(custom_data)
    for custom_data_class in INTERCOM_CUSTOM_DATA_CLASSES:
        try:
            cd_class = my_import(custom_data_class)
            # check make sure the class has a custom_data method.
            if cd_class and hasattr(cd_class, 'custom_data'):
                # call custom_data method and update the custom_data dict
                custom_data.update(cd_class.custom_data(user))
            else:
                log.warning("%s doesn't have a custom_data qmethod, skipping.",
                            custom_data_class)
        except ImportError as e:
            log.warning(
                "%s couldn't be imported, there was an error during import. "
                "skipping. %s", custom_data_class, e)
        finally:
            return json.dumps(custom_data)


def get_company_data(user):
    """
    Get the company custom data from the custom company class
    Args:
        user: The Django user

    Returns:
        company_data(json): the company data loaded from the class if exists,
        otherwise it is empty
    """
    company_data = {}
    if INTERCOM_COMPANY_DATA_CLASS is None:
        return json.dumps(company_data)
    try:
        cd_class = my_import(INTERCOM_COMPANY_DATA_CLASS)
        # make sure the class has a company_data method
        if cd_class and hasattr(cd_class, 'company_data'):
            data = cd_class.company_data(user)
            if all(k in data for k in ('id', 'name', 'created_at')):
                company_data.update(data)
            else:
                log.warning(
                    "company method of %s doesn't return all of the required "
                    "dictionary keys (id, name, created_at), skipping.",
                    INTERCOM_COMPANY_DATA_CLASS)
        else:
            log.warning("%s doesn't have a company_data method, skipping.",
                        INTERCOM_COMPANY_DATA_CLASS)
    except ImportError as e:
        log.warning(
            "%s couldn't be imported, there was an error during import. "
            "skipping. %s", INTERCOM_COMPANY_DATA_CLASS, e)

    finally:
        return json.dumps(company_data)
