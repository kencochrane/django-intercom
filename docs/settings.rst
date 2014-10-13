Settings
========
These are the settings that you can add to your django settings file to control django-intercom.


INTERCOM_APPID
--------------
**Required**

Default: None

Example::

    INTERCOM_APPID = "your appID"


INTERCOM_SECURE_KEY
-------------------
**Optional**

Default: None

example::

        INTERCOM_SECURE_KEY = "your security_code"


INTERCOM_INCLUDE_USERID
-----------------------
**Optional**

Whether to include the ``user_id`` in the intercom settings. Turn this off if
you want to use the email as the key to identify a user.

Default: True

example::

        INTERCOM_INCLUDE_USERID = False


INTERCOM_ENABLE_INBOX
---------------------
**Optional**

Default: True

example::

    INTERCOM_ENABLE_INBOX = True


INTERCOM_ENABLE_INBOX_COUNTER
-----------------------------
**Optional**

Default: True

example::

    INTERCOM_ENABLE_INBOX_COUNTER = True


INTERCOM_INBOX_CSS_SELECTOR
---------------------------
**Optional**

Default: '#Intercom'

example::

    INTERCOM_INBOX_CSS_SELECTOR = '#Intercom'


INTERCOM_CUSTOM_DATA_CLASSES
----------------------------
**Optional**

Default = None

example::

    INTERCOM_CUSTOM_DATA_CLASSES = [
        'thepostman.utils.custom_data.IntercomCustomData',
    ]
