Installation
============
1. Install django-intercom using pip::

    pip install django-intercom

2. Add intercom to your INSTALLED_APPS in your django settings file::

    INSTALLED_APPS = (
        # all
        # other 
        # apps
        'intercom',
    )

3. Add "INTERCOM_APPID" setting to your django settings file with your intercom application Id.

    in settings.py::

        INTERCOM_APPID = "your appID"
