# coding: utf-8

import os
import json

from django.conf import settings
from django.contrib.gis.geos.geometry import Point
from django.core.management.base import BaseCommand


from treemap.instance import Instance
from treemap.models import Tree, Plot, User, Species
from treemap.lib.geo_tools import ProjectionConverter


class Command(BaseCommand):
    
    """
    Import trees form file.
    """

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        if os.path.isfile(options['filename']):
            self.import_trees_from_geojson(options['filename'])
        else:
            self.stdout.write(self.style.ERROR('No such file!'))

    def get_or_create_species(self, properties, instance):
        species = Species.objects.filter(common_name=properties['gatunek'], instance=instance)
        if not species.exists():
            # TODO additional logic here
            raise
        else:
            return species.last()

    def get_or_create_plot(self, tree, instance, plot_geom, admin):
        address = tree['properties']['adres'] + tree['properties']['numer_adres']
        plot = Plot.objects.filter(geom=plot_geom, address_street=address, instance=instance)

        if not plot.exists():
            plot = Plot(
                address_city='Warszawa',
                updated_by=admin,
                readonly=False,
                instance=instance,
                geom=plot_geom,
                feature_type='Plot',
                address_street=address
            )

            plot.save_with_user(admin)
            return plot
        else:
            return plot.last()

    def import_trees_from_geojson(self, filename):

        admin = User.objects.get(username=settings.ADMIN_NAME)
        instance = Instance.objects.get(name=settings.INSTANCE_NAME)
        file_ = open(filename, 'r')
        converter = ProjectionConverter()

        for line in file_:

            j = json.loads(line)
            trees = j['features']

            for tree in trees:

                lon_wgs84, lat_wgs84 = tree['geometry']['coordinates']
                lon_webm, lat_webm = converter.to_webmercator(lon_wgs84, lat_wgs84)
                plot_geom = Point(lon_webm, lat_webm, srid=3857)

                plot = self.get_or_create_plot(tree, instance, plot_geom, admin)
                species = self.get_or_create_species(tree['properties'], instance)
                
                # TODO;
                # wysokosc  = float(properties['wysokosc'].replace(',','.'))
                # if wysokosc == 0.0:
                #     wysokosc = 0.1
                # 
                # diameter =  float(properties['srednica_k'].replace(',','.'))
                # 
                # if diameter  ==  0.0:
                # 
                # #        obwod  =  float(properties['pnie_obwod'].replace(',','.'))
                # 
                # #        diameter = obwod/math.pi
                # 
                # #        if diameter  ==  0.0:
                # 
                #         diameter = 0.1
                # 
                # new_tree = Tree(
                #     plot=new_plot,
                #     diameter=diameter,
                #     readonly=False,
                #     canopy_height=wysokosc,
                #     instance=instance,
                #     height=wysokosc,
                #     species=specie
                # )
                # 
                # new_tree.save_with_user(admin)

