# coding: utf-8

import os
import re
import json

from django.db import transaction
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

    def generate_species_code(self, genus, species, cultivar):
        """
        OpenTreeMap is using american USDA codes, but we'll need to generate our own ones.
        """
        if cultivar:
            code = u"%s%s%s" % (genus[0], species[0], cultivar[0])
        else:
            code = u"%s%s" % (genus[0], species[0])

        code = code.upper()

        added_code = Species.objects.filter(otm_code=code).order_by('otm_code')
        if added_code.exists():
            code = u"%s%s" % (added_code, "1")

        return code

    def parse_species_name(self, species_input):
        """
        Extract genus, species and cultivar names from string.
        """
        genus = species_input.split(" ")[0]
        species = species_input
        cultivar = ""

        cultivar_match = re.match(r"'([A-Za-z_\./\\-]*)'", species_input)
        if cultivar_match:
            species = species_input.split("'")[0]
            cultivar = cultivar_match.group().replace("'", "")

        return genus, species, cultivar

    def get_or_create_species(self, properties, instance, admin):
        species = Species.objects.filter(common_name=properties['gatunek'], instance=instance)
        if not species.exists():
            genus, _species, cultivar = self.parse_species_name(properties['gatunek_1'])
            otm_code = self.generate_species_code(genus, _species, cultivar)
            species = Species(
                common_name=properties['gatunek'],
                genus=genus,
                species=species,
                instance=instance,
                otm_code=otm_code
            )
            species.save_with_user(admin)

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
                with transaction.atomic():

                    lon_wgs84, lat_wgs84 = tree['geometry']['coordinates']
                    lon_webm, lat_webm = converter.to_webmercator(lon_wgs84, lat_wgs84)
                    plot_geom = Point(lon_webm, lat_webm, srid=3857)

                    plot = self.get_or_create_plot(tree, instance, plot_geom, admin)
                    species = self.get_or_create_species(tree['properties'], instance, admin)
                    height = float(tree['properties']['wysokosc'].replace(',','.'))
                    diameter = float(tree['properties']['srednica_k'].replace(',','.'))

                    # Default values if original are unknown.
                    height = height or 10.0
                    diameter = diameter or 1.0

                    tree = Tree.objects.filter(plot=plot, instance=instance, species=species)

                    if not tree.exists():
                        new_tree = Tree(
                             plot=plot,
                             diameter=diameter,
                             readonly=False,
                             canopy_height=height,
                             instance=instance,
                             height=height,
                             species=species
                        )
                        new_tree.save_with_user(admin)
