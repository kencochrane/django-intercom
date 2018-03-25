from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from intercom.templatetags.intercom import (intercom_tag,
                                            get_company_data,
                                            get_custom_data)

MODULE_PATCH = 'intercom.templatetags.intercom.{}'

class CustomDataDummy:
    def custom_data(self, user):
        return {'test': 'This Is Dummy Data'}


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
        tag = intercom_tag(self.context)
        self.assertFalse(tag["INTERCOM_IS_VALID"])

    def test_intercom_tag_with_disabled_settings(self):
        with patch(MODULE_PATCH.format('INTERCOM_DISABLED'), True):
            self.context['request'] = self.request
            tag = intercom_tag(self.context)
            self.assertFalse(tag["INTERCOM_IS_VALID"])

    def test_intercom_tag_with_enabled_settings(self):
        self.context['request'] = self.request
        tag = intercom_tag(self.context)
        self.assertTrue(tag["INTERCOM_IS_VALID"])

    def test_get_custom_data_default_is_empty_JSON(self):
        returned_JSON = get_custom_data(self.user)
        self.assertJSONEqual(returned_JSON, {})

    def test_get_custom_data(self):
        with patch(MODULE_PATCH.format('INTERCOM_CUSTOM_DATA_CLASSES'),
                   ['tests.test_intercom.CustomDataDummy']):
            returned_JSON = get_custom_data(self.user)
            self.assertJSONEqual(returned_JSON, {'test': 'This Is Dummy Data'})

    def test_get_company_data_default_is_empty_JSON(self):
        returned_JSON = get_company_data(self.user)
        self.assertJSONEqual(returned_JSON, {})

    def test_get_company_data(self):
        pass
