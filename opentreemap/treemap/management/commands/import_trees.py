import math

from datetime import datetime
from collections import defaultdict

from pyproj import Proj
from pyreproj import Reprojector
import unicodecsv
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from treemap.models import Species, Tree, User, Plot

IMPORT_AS_USERNAME = 'super'


class Command(BaseCommand):
    """
    Imports data fetched by tree_scraper.
    https://github.com/kodujdlapolski/tree-research

    Expected format:
    [
        'Aktualno\xc5\x9b\xc4\x87 danych na dzie\xc5\x84',
        'Jednostka zarz\xc4\x85dzaj\xc4\x85ca',
        'Nazwa polska',
        'Nazwa \xc5\x82aci\xc5\x84ska',
        'Numer inwentaryzacyjny',
        'Obw\xc3\xb3d pnia w cm',
        'Wysoko\xc5\x9b\xc4\x87 w m',
        'gtype',
        'height',
        'id',
        'imgurl',
        'width',
        'x',
        'y'
    ]
    """

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('instance_id', type=int)
        parser.add_argument(
            '--import-species',
            action='store_true',
            dest='import_species'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        instance_id = options['instance_id']
        data = load_tree_data(file_path)

        if options['import_species']:
            self.stdout.write('Importing distinct species list to the database')
            save_species(data, instance_id)
        else:
            self.stdout.write('Importing trees to the database')
            import_trees(data, instance_id)


def get_area(circumference):
    """
    :circumference: of the single tree
    """
    return math.pi * (circumference / (2.0 * math.pi)) ** 2


def get_summed_trunk_diam(circumferences_str):
    if not circumferences_str:
        return None
    circ_list = map(float, circumferences_str.split(', '))
    area = sum(get_area(circ) for circ in circ_list)
    return float(math.sqrt(area / math.pi) * 2)


def convert_coords(row):
    pl_proj = Proj(init='EPSG:2178')
    rp = Reprojector()
    transform = rp.get_transformation_function(
        from_srs=pl_proj, to_srs='EPSG:3857'
    )
    return transform(float(row[12]), float(row[13]))


def save_tree(row, user, instance_id):
    fmt = '%d.%m.%Y'
    updated_at = datetime.strptime(row[0], fmt)
    (x, y) = convert_coords(row)
    geom = Point(x, y)
    height = float(row[6].replace(',', '.')) if row[6] else None
    trunk_diam = get_summed_trunk_diam(row[5])

    exists = Plot.objects.filter(instance_id=instance_id, geom=geom).exists()
    if not exists:
        species = Species.objects.get(species=row[3], instance_id=instance_id)
        plot = Plot(instance_id=instance_id, updated_at=updated_at, geom=geom)
        plot.save_with_system_user_bypass_auth()
        tree = Tree(
            plot=plot,
            instance_id=1,
            species=species,
            diameter=trunk_diam,
            height=height,
        )
        tree.save_with_system_user_bypass_auth()
        print(trunk_diam, species.species, updated_at)


def save_species(data, instance_id):
    uniq_species = defaultdict(dict)
    for row in data:
        species = row[3]
        common_name = row[2]
        genus = species.split(' ')[0]
        uniq_species[species] = {'common_name': common_name, 'genus': genus}

    for species_name, details in uniq_species.iteritems():
        sp = Species(
            common_name=details['common_name'],
            genus=details['genus'],
            species=species_name,
            instance_id=instance_id,
        )
        sp.save_with_system_user_bypass_auth()


def load_tree_data(file_path):
    data = []
    with open(file_path, 'r') as desc:
        reader = unicodecsv.reader(desc, delimiter=',')
        for i, row in enumerate(reader):
            if i > 0:
                data.append(row)
    return data


def import_trees(data, instance_id):
    user = User.objects.get(username=IMPORT_AS_USERNAME)
    for row in data:
        save_tree(row, user, instance_id)
