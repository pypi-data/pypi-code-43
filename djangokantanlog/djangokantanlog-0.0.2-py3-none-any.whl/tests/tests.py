# -*- coding: utf8 -*-
from django.test import TestCase
from logging import getLogger
from django.urls import reverse
from django.contrib.auth.models import User
from .models import TObject


logger = getLogger(__name__)


class KantanlogTests(TestCase):

    fixtures = ['test_kantanlog.xml']

    def setUp(self):
        logger.debug('log user name test name')
        self.client.logout()
        User.objects.create_user('temp', 'temp@local', 'temp')

    def test_profile(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_cby(self):
        logger.debug('test cby')
        self.client.login(username='temp', password='temp')
        response = self.client.post(
            reverse('create'),
            {},
            HTTP_X_FORWARDED_FOR='127.0.0.2',
        )
        tv = TObject.objects.get(name='init')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tv.level, 1)
        self.assertEqual(tv.created_by, 'temp')
        self.assertEqual(tv.updated_by, 'temp')

    def test_uby(self):
        logger.debug('test uby')
        tv = TObject.objects.get(name='original')
        self.assertEqual(tv.level, -1)
        self.assertEqual(tv.created_by, 'me')
        self.assertEqual(tv.updated_by, 'me')

        self.client.login(username='temp', password='temp')
        response = self.client.post(reverse('update'))

        self.assertEqual(response.status_code, 200)
        tv = TObject.objects.get(name='original')
        self.assertEqual(tv.level, 777)
        self.assertEqual(tv.created_by, 'me')
        self.assertEqual(tv.updated_by, 'temp')
