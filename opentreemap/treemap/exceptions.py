# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json
from requests import HTTPError

from django.contrib import messages
from django.contrib.messages.api import MessageFailure
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from social_core.utils import social_logger
from social_core.exceptions import SocialAuthBaseException
from social_django.middleware import SocialAuthExceptionMiddleware


class InvalidInstanceException(Exception):
    pass


class JSONResponseForbidden(HttpResponseForbidden):
    def __init__(self, *args, **kwargs):
        super(JSONResponseForbidden, self).__init__(
            json.dumps({'error': 'Permission Denied'}),
            *args,
            content_type='application/json',
            **kwargs)


class CustomSocialDjangoExceptionMiddleware(SocialAuthExceptionMiddleware):

    """
    Handling exceptions that were ignored by social_django.
    """

    def process_exception(self, request, exception):
        super(CustomSocialDjangoExceptionMiddleware, self).process_exception(request, exception)

        if isinstance(exception, ValidationError):
            if exception.error_dict.get('email'):
                error_message = _("Sorry, there was a problem with logging you in. "
                                  "It appears your email is already in our database. "
                                  "Try to log in with your existing account. "
                                  "If you don't remember your login, please use \"Recover my username\" option.")
            else:
                error_message = _("Sorry, logging in was unsuccessful. Try to use different method.")
            messages.error(request, error_message)
            return redirect('auth_login')

        elif isinstance(exception, HTTPError):
            error_message = _("Sorry, logging in was unsuccessful. Try to use different method.")
            messages.error(request, error_message)
            return redirect('auth_login')
