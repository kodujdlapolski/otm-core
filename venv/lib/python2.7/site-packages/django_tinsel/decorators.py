# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import sys
import json
from functools import wraps

from django.contrib.auth import get_user_model
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, Http404)
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from django_tinsel.exceptions import HttpBadRequestException
from django_tinsel.utils import LazyEncoder


def route(**kwargs):
    """
    Route a request to different views based on http verb.

    Kwargs should be 'GET', 'POST', 'PUT', 'DELETE' or 'ELSE',
    where the first four map to a view to route to for that type of
    request method/verb, and 'ELSE' maps to a view to pass the request
    to if the given request method/verb was not specified.
    """
    def routed(request, *args2, **kwargs2):
        method = request.method
        if method in kwargs:
            req_method = kwargs[method]
            return req_method(request, *args2, **kwargs2)
        elif 'ELSE' in kwargs:
            return kwargs['ELSE'](request, *args2, **kwargs2)
        else:
            raise Http404()
    return routed


def log(message=None, out=sys.stdout):
    """Log a message before passing through to the wrapped function.

    This is useful if you want to determine whether wrappers are
    passing down the pipeline to the functions they wrap, or exiting
    early, usually with some kind of exception.

    Example:
    example_view = decorate(username_matches_request_user,
                            log("The username matched"),
                            json_api_call,
                            example)
    """
    def decorator(view_fn):
        @wraps(view_fn)
        def f(*args, **kwargs):
            print(message, file=out)
            return view_fn(*args, **kwargs)
        return f
    return decorator


def render_template(template):
    """
    takes a template to render to and returns a function that
    takes an object to render the data for this template.

    If callable_or_dict is callable, it will be called with
    the request and any additional arguments to produce the
    template paramaters. This is useful for a view-like function
    that returns a dict-like object instead of an HttpResponse.

    Otherwise, callable_or_dict is used as the parameters for
    the rendered response.
    """
    def outer_wrapper(callable_or_dict=None, statuscode=None, **kwargs):
        def wrapper(request, *args, **wrapper_kwargs):
            if callable(callable_or_dict):
                params = callable_or_dict(request, *args, **wrapper_kwargs)
            else:
                params = callable_or_dict

            # If we want to return some other response type we can,
            # that simply overrides the default behavior
            if params is None or isinstance(params, dict):
                resp = render_to_response(template, params,
                                          RequestContext(request), **kwargs)
            else:
                resp = params

            if statuscode:
                resp.status_code = statuscode

            return resp

        return wrapper
    return outer_wrapper


def json_api_call(req_function):
    """ Wrap a view-like function that returns an object that
        is convertable from json
    """
    @wraps(req_function)
    def newreq(request, *args, **kwargs):
        outp = req_function(request, *args, **kwargs)
        if issubclass(outp.__class__, HttpResponse):
            return outp
        else:
            return '%s' % json.dumps(outp, cls=LazyEncoder)
    return string_to_response("application/json")(newreq)


def string_to_response(content_type):
    """
    Wrap a view-like function that returns a string and marshalls it into an
    HttpResponse with the given Content-Type
    If the view raises an HttpBadRequestException, it will be converted into
    an HttpResponseBadRequest.
    """
    def outer_wrapper(req_function):
        @wraps(req_function)
        def newreq(request, *args, **kwargs):
            try:
                outp = req_function(request, *args, **kwargs)
                if issubclass(outp.__class__, HttpResponse):
                    response = outp
                else:
                    response = HttpResponse()
                    response.write(outp)
                    response['Content-Length'] = str(len(response.content))

                response['Content-Type'] = content_type

            except HttpBadRequestException as bad_request:
                response = HttpResponseBadRequest(bad_request.message)

            return response
        return newreq
    return outer_wrapper


def username_matches_request_user(view_fn):
    """Checks if the username matches the request user, and if so replaces
    username with the actual user object.
    Returns 404 if the username does not exist, and 403 if it doesn't match.
    """
    @wraps(view_fn)
    def wrapper(request, username, *args, **kwargs):
        User = get_user_model()

        user = get_object_or_404(User, username=username)
        if user != request.user:
            return HttpResponseForbidden()
        else:
            return view_fn(request, user, *args, **kwargs)

    return wrapper
