# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db.models.fields.files import ImageFieldFile
from django.utils.encoding import force_text
from django.utils.functional import Promise


def decorate(*reversed_views):
    """
    provide a syntax decorating views without nested calls.

    instead of:
    json_api_call(etag(<hash_fn>)(<view_fn>)))

    you can write:
    decorate(json_api_call, etag(<hash_fn>), <view_fn>)
    """
    fns = reversed_views[::-1]
    view = fns[0]
    for wrapper in fns[1:]:
        view = wrapper(view)
    return view


# https://docs.djangoproject.com/en/dev/topics/serialization/#id2
class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        elif hasattr(obj, 'dict'):
            return obj.dict()
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, 'as_dict'):
            return obj.as_dict()
        elif isinstance(obj, Point):
            srid = 4326
            obj = obj.transform(srid, clone=True)
            return {'x': obj.x, 'y': obj.y, 'srid': srid}
        # TODO: Handle S3
        elif isinstance(obj, ImageFieldFile):
            if obj:
                return obj.url
            else:
                return None
        elif isinstance(obj, GEOSGeometry):
            srid = 4326
            return {
                'geojson': json.loads(obj.transform(srid, clone=True).json),
                'srid': srid
            }
        else:
            return super(LazyEncoder, self).default(obj)
