from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from django_intercom.templatetags.intercom import (intercom_tag,
                                                   get_company_data,
                                                   get_custom_data)

MODULE_PATCH = 'django_intercom.templatetags.intercom.{}'


class CustomDataDummy:
    dummy_data = {'test': 'This Is Dummy Data'}

    def custom_data(self, user):
        return self.dummy_data


class CustomCompanyDataDummy:
    dummy_data = {'id': 0,
                  'name': 'intercom_test',
                  'created_at': datetime.utcnow().isoformat()}

    def company_data(self, user):
        return self.dummy_data


class TestIntercomTemplateTag(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test_user',
                                             first_name='Test',
                                             last_name='User',
                                             password='VerySecretPassword')
        self.context = {}
        self.request = RequestFactory().get('/')
        SessionMiddleware().process_request(self.request)
        self.request.session.save()

    def test_intercom_tag_without_request(self):
        """
        Test intercom templatetage without Request
        """
        tag = intercom_tag(self.context)
        self.assertFalse(tag["INTERCOM_IS_VALID"])

    def test_intercom_tag_with_disabled_settings(self):
        """
        Test intercom templatetage with intercom disabled and without app_id
        """
        with patch(MODULE_PATCH.format('INTERCOM_DISABLED'), True):
            self.context['request'] = self.request
            tag = intercom_tag(self.context)
            self.assertFalse(tag["INTERCOM_IS_VALID"])

    def test_intercom_tag_with_enabled_settings_authenticated_user(self):
        """
        Test intercom templatetage with intercom enabled
        """
        expected = {'INTERCOM_IS_VALID': True, 'intercom_appid': '1234abCD',
                    'email_address': '', 'user_id': 1,
                    'name': 'test_user', 'enable_inbox': True,
                    'use_counter': 'true',
                    'css_selector': '#Intercom', 'custom_data': '{}',
                    'company_data': '{}', 'user_hash': None}
        with patch(MODULE_PATCH.format('INTERCOM_APPID'), '1234abCD'):
            self.request.user = self.user
            self.context['request'] = self.request
            tag_dict = intercom_tag(self.context)
            # Remove user_created
            del tag_dict['user_created']
            self.assertDictEqual(tag_dict, expected)

    def test_intercom_tag_with_enabled_settings_unauthenticated_user(self):
        """
        Test intercom templatetage with intercom enabled
        """
        expected = {'INTERCOM_IS_VALID': True,
                    'intercom_appid': '1234abCD',
                    'email_address': 'lead@example.com',
                    'name': 'Unknown', 'enable_inbox': True,
                    'use_counter': 'true', 'css_selector': '#Intercom',
                    'custom_data': '{}', 'company_data': '{}',
                    'user_hash': None}
        with patch(MODULE_PATCH.format('INTERCOM_APPID'), '1234abCD'):
            self.request.user = AnonymousUser()
            self.context['request'] = self.request
            tag_dict = intercom_tag(self.context)
            # Remove user_id
            del tag_dict['user_id']
            self.assertDictEqual(tag_dict, expected)

    def test_get_custom_data_default_is_empty_JSON(self):
        """
        Test getting custom company data with Empty INTERCOM_USER_DATA_CLASS
        """
        returned_JSON = get_custom_data(self.user)
        self.assertJSONEqual(returned_JSON, {})

    def test_get_custom_data(self):
        """
        Test getting custom company data with INTERCOM_USER_DATA_CLASS
        """
        with patch(MODULE_PATCH.format('INTERCOM_CUSTOM_DATA_CLASSES'),
                   ['tests.test_templatetags.CustomDataDummy']):
            returned_JSON = get_custom_data(self.user)
            self.assertJSONEqual(returned_JSON, CustomDataDummy.dummy_data)

    def test_get_company_data_default_is_empty_JSON(self):
        """
        Test getting custom company data with Empty INTERCOM_COMPANY_DATA_CLASS
        """
        returned_JSON = get_company_data(self.user)
        self.assertJSONEqual(returned_JSON, {})

    def test_get_company_data(self):
        """
        Test getting custom company data with INTERCOM_COMPANY_DATA_CLASS
        """
        with patch(MODULE_PATCH.format('INTERCOM_COMPANY_DATA_CLASS'),
                   'tests.test_templatetags.CustomCompanyDataDummy'):
            returned_json = get_company_data(self.user)
            self.assertJSONEqual(returned_json,
                                 CustomCompanyDataDummy.dummy_data)
