from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.polygon import Polygon
from treemap.models import Boundary, Instance

"""
Adds all necessary attributes to the Warsaw instance,
so it's possible to develop features locally.
"""

n1geom = MultiPolygon(
    Polygon(((21.2331980000000016, 52.1797839999999979), (20.9269539999999985,
                                                          52.0836830000000006),
             (20.8047310000000003, 52.2378500000000017), (21.0759560000000015,
                                                          52.3117949999999965),
             (21.2331980000000016, 52.1797839999999979))))

bound = Boundary(name="warszawa", category='none', sort_order=4, geom=n1geom)
bound.save()

instance = Instance.objects.get(name='warszawa')

# The ESRI map doesn't require further setup (unlike Google map)
instance.basemap_type = 'esri'

# Itree region is required for ecobenefits to work
instance.itree_region_default = 'NoEastXXX'
instance.boundaries.add(bound)
instance.save()
