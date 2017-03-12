from __future__ import absolute_import, unicode_literals

import urllib
import urlparse
import hashlib

try:
    from django.http.request import QueryDict
except ImportError:  # django 1.4.2
    from django.http import QueryDict

from django.utils.encoding import iri_to_uri


class UrlHelper(object):
    def __init__(self, full_path):
        # If full_path is an UrlHelper instance, extract the full path from it
        if type(full_path) is UrlHelper:
            full_path = full_path.get_full_path()

        # parse the path
        r = urlparse.urlparse(full_path)
        self.path = r.path
        self.fragment = r.fragment
        self.query_dict = QueryDict(r.query, mutable=True)

    def get_query_string(self, **kwargs):
        return self.query_dict.urlencode(**kwargs)

    def get_query_data(self):
        return self.query_dict

    def update_query_data(self, **kwargs):
        for key, val in kwargs.iteritems():
            if hasattr(val, '__iter__'):
                self.query_dict.setlist(key, val)
            else:
                self.query_dict[key] = val

    def get_path(self):
        return self.path

    def get_full_path(self, **kwargs):
        query_string = self.get_query_string(**kwargs)
        if query_string:
            query_string = '?%s' % query_string
        fragment = self.fragment and '#%s' % iri_to_uri(self.fragment) or ''

        return '%s%s%s' % (
            iri_to_uri(self.get_path()),
            query_string,
            fragment
        )

    def get_full_quoted_path(self, **kwargs):
        return urllib.quote_plus(self.get_full_path(**kwargs), safe='/')

    def overload_params(self, **kwargs):
        for key, val in kwargs.iteritems():
            uniques = set(self.query_dict.getlist(key))
            uniques.add(val)
            self.query_dict.setlist(key, list(uniques))

    def del_param(self, param):
        try:
            del self.query_dict[param]
        except KeyError:
            pass  # Fail silently

    def del_params(self, *params, **kwargs):
        if not params and not kwargs:
            self.query = {}
            return
        if params:
            for param in params:
                self.del_param(param)
        if kwargs:
            for key, val in kwargs.iteritems():
                to_keep = [x for x in self.query_dict.getlist(key)
                           if not x.startswith(val)]
                self.query_dict.setlist(key, to_keep)

    def toggle_params(self, **params):
        for param, value in params.items():
            value = unicode(value)
            if value in self.query_dict.getlist(param):
                self.del_params(**{param: value})
            else:
                self.overload_params(**{param: value})

    @property
    def hash(self):
        md5 = hashlib.md5()
        md5.update(self.get_full_path())
        return md5.hexdigest()

    @property
    def query(self):
        return self.get_query_data()

    @query.setter
    def query(self, value):
        if type(value) is dict:
            self.query_dict = QueryDict('', mutable=True)
            self.update_query_data(**value)
        else:
            self.query_dict = QueryDict(value, mutable=True)

    @property
    def query_string(self):
        return self.get_query_string()

    @query_string.setter
    def query_string(self, value):
        self.query_dict = QueryDict(value, mutable=True)

    def __str__(self):
        return self.get_full_path()
