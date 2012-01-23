===============
django-intercom
===============

django-intercom makes it easy to user intercom.io in your django application. You just need to do the following.

Installation
============
1. Install django-intercom using easy_setup or pip::

    pip install django-intercom


2. add intercom to your INSTALLED_APPS in your django settings file::

    INSTALLED_APPS = (
        # all
        # other 
        # apps
        'intercom',
    )

3. Add "INTERCOM_APPID" setting to your django settings file with your intercom application Id.

    in settings.py::

        INTERCOM_APPID = "your appID"

4. Add the template tag code into your base template before the body tag.

    At the top of the page put this::

    {% load intercom %}

    At the bottom of the page before the </body> tag put this::

    {% intercom_tag %}


Enable Secure Mode (Optional)
=============================
This is optional, if it isn't set, then you will not use secure mode.

If you want to turn on secure mode, you can add INTERCOM_SECURE_KEY to your settings.py with the private key you can get from your intercom->app->security page. 

in settings.py::

    INTERCOM_SECURE_KEY = "your security_code"

You will need to look in the code samples to find the security key.

You will also need to make sure you check the "Enable secure mode" check box on the security page before this will work correctly.