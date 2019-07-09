===============
django-intercom
===============

django-intercom makes it easy to use http://intercom.io in your django application. You just need to do the following.

Supported Python versions: 2.7 and 3.3+

Releases
========
- 0.1.3 : 07-09-2019
  - Fixed anonymous error where it wasn't getting set correctly  [@humitos]
  - bump django to 2.0.13
  - changed default_user so it wasn't global [@humitos]
- 0.1.2 : 10-19-2018
  - #35 fix(error): TypeError: 'bool' object is not callable [@AnArchkoleptik]
  - bump django dev requirement to 2.0.9
- 0.1.1 : 07-21-2018
  - Fix intercom_tag when user is not authenticated
- 0.1.0 : 06-30-2018
  - rename package to avoid conflict with python-intercom_tag
  - refactor custom_data and company_data parts
  - refactor is_authenticated
  - fix PEP8 issues
  - add ability to use intercom with anonymous users
- 0.0.13 : 2-16-2016
  - fixed setup.py problems with python 3
- 0.0.12 : 2-1-2016
  - added python3 support

Documentation
=============
Documentation is also available online at http://django-intercom.readthedocs.org

Installation
============
1. Install django-intercom using easy_setup or pip::

    pip install django-intercom


2. Add intercom to your ``INSTALLED_APPS`` in your django settings file::

    INSTALLED_APPS = (
        # all
        # other
        # apps
        'django_intercom',
    )

3. Add ``INTERCOM_APPID`` setting to your django settings file with your intercom application Id.

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

Disable Tag (Optional)
======================
This is optional, if it isn't set to True, then the tag will be active.

If you want to disable the tag, you can add INTERCOM_DISABLED to your settings.py.

in settings.py::

    INTERCOM_DISABLED = True

This is useful when you do not want to send user information to intercom.io on every request in some enviroment for a period of time, e.g. in a development enviroment.

This provides a quick way to disable the tag without having to remove/comment out the tag in templates or the INTERCOM_APPID in settings.py (the latter would disable the sending of information but result in a setup warning in the log).

Intercom Inbox
==============
Intercom has the ability to add an inbox link to your app so that people can contact you, and for you to let them know when they have a message waiting. If you would like to use these features you need to do the following.

1. Add the intercom css id to any inline element containing text, for example::

    <a id="Intercom" href="#">Support</a>

2. Add the appropriate CSS to your style sheet.

No Icon::

    #Intercom {
      display: inline-block;
      text-decoration: underline;
      padding: 0;
    }

White Envelope (white text on black background)::

    #Intercom {
      display: inline-block;
      text-decoration: underline;
      padding: 0 0 0 24px;
      background: transparent url(https://www.intercom.io/images/white_env.png) no-repeat left center;
    }

Black Envelope (black text on white/grey background)::

    #Intercom {
      display: inline-block;
      text-decoration: underline;
      padding: 0 0 0 24px;
      background: transparent url(https://www.intercom.io/images/black_env.png) no-repeat left center;
    }

If you want to show the unread message count then also add the following::

    #Intercom em {
      display: inline-block;
      font-style: normal;
      text-decoration: underline;
    }

3. Configure your settings. Add the following to your django settings if you would like to change the defaults.

INTERCOM_ENABLE_INBOX
---------------------
Default: True

In settings.py::

    INTERCOM_ENABLE_INBOX = True


INTERCOM_ENABLE_INBOX_COUNTER
-----------------------------
Default: True

In settings.py::

    INTERCOM_ENABLE_INBOX_COUNTER = True


INTERCOM_INBOX_CSS_SELECTOR
---------------------------
Default: '#Intercom'

In settings.py::

    INTERCOM_INBOX_CSS_SELECTOR = '#Intercom'


User Data
=========
By default, django-intercom will send the following user information to intercom.io:

1. user_id (sourced from request.user.id)
2. email (sourced from request.user.email)
3. name (sourced from request.user.username or, and as a fallback, request.user.get_username())
4. created_at (sourced from request.user.date_joined)
5. user_hash (calculated using INTERCOM_SECURE_KEY and user_id, if INTERCOM_SECURE_KEY is set)

You can override any or all of fields 1-4 by creating a Class with a user_data method that accepts a Django User model as an argument. The method should return a dictionary containing any or all of the keys **user_id**, **email**, **name** and **user_created**, and the desired values for each. Note that the user_created key must contain a datetime. Here is an example::

    from django.utils.dateformat import DateFormat

    class IntercomUserData:
        """ User data class located anywhere in your project
            This one is located in thepostman/utils/user_data.py """

        def user_data(self, user):
            """ Required method, same name and only accepts one attribute (django User model) """

            return {
                'name' : user.userprofile.name,
            }

You will need to register your class with django-intercom so that it knows where to find it. You do this by adding the class to the INTERCOM_USER_DATA_CLASS setting.

INTERCOM_USER_DATA_CLASS
---------------------------
Default = None

in settings.py::

    INTERCOM_USER_DATA_CLASS = 'thepostman.utils.user_data.IntercomUserData'

Custom Data
===========
Intercom.io allows you to send them your own custom data, django-intercom makes this easy. All you need to do it create a Class with a custom_data method that accepts a Django User model as an argument and returns a dictionary. Here is an example::

    from thepostman.models import message

    class IntercomCustomData:
        """ Custom data class located anywhere in your project
            This one is located in thepostman/utils/custom_data.py """

        def custom_data(self, user):
            """ Required method, same name and only accepts one attribute (django User model) """

            num_messages = message.objects.filter(user=user).count()
            num_unread = messages.objects.filter(user=user, read=False).count()

            return {
                'num_messages' : num_messages,
                'num_unread' : num_unread,
            }

Once you have your classes built, you will need to register them with django-intercom so that it knows where to find them. You do this by adding the class to the INTERCOM_CUSTOM_DATA_CLASSES setting. It is important to note that if you have the same dict key returned in more then one Custom Data Class the last class that is run (lower in the list) will overwrite the previous ones.

INTERCOM_CUSTOM_DATA_CLASSES
----------------------------
Default = None

in settings.py::

    INTERCOM_CUSTOM_DATA_CLASSES = [
        'thepostman.utils.custom_data.IntercomCustomData',
    ]


Company Data
============
Intercom.io allows you to group your users by company, django-intercom makes this easy. All you need to do is create a Class with a company_data method that accepts a Django user model as an argument and returns a dictionary containing the keys id, name and created_at, and whatever other information you want to store about the company. Note that the created_at key must contain a Unix timestamp. Here is an example::

    from django.utils.dateformat import DateFormat

    class IntercomCompanyData:
        """ Company data class located anywhere in your project
            This one is located in thepostman/utils/company_data.py """

        def company_data(self, user):
            """ Required method, same name and only accepts one attribute (django User model) """

            organisation = user.organisation

            return {
                'id' : organisation.id,
                'name' : organisation.name,
                'created_at' : DateFormat(organisation.created_at).U(),
                'price_plan' : organisation.price_plan,
            }

You will need to register your class with django-intercom so that it knows where to find it. You do this by adding the class to the INTERCOM_COMPANY_DATA_CLASS setting.

INTERCOM_COMPANY_DATA_CLASS
---------------------------
Default = None

in settings.py::

    INTERCOM_COMPANY_DATA_CLASS = 'thepostman.utils.company_data.IntercomCompanyData'
