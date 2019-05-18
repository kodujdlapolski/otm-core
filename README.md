![OTM2 open source logo](https://opentreemap.github.io/images/logo@2x.png)

# Mapadrzew.pl
This is Polish instance of the Open Tree Map forked from https://github.com/OpenTreeMap/otm-core, hosted under mapadrzew.pl.

The project is maintained by [Koduj dla Polski](https://kodujdlapolski.pl/projects/mapadrzew/) team.

## Installation

The easiest way to set up the project is to use docker-compose which will build containers for all services that are required. Docker-compose can be installed easily on most Linux/MacOS systems: https://docs.docker.com/compose/install/

### otm-core
Fetch the ecobenefits repository to the services/ dir.
```
cd otm-core/
git clone git@github.com:kodujdlapolski/ecobenefits.git services/ecobenefits
```

Copy local settings from the template.
```
cp opentreemap/opentreemap/settings/local_settings.py.template opentreemap/opentreemap/settings/local_settings.py
```

Run build for all Docker containers. This may take a while.
```
docker-compose build
```

When containers are ready, start all services:
```
docker-compose up
```

Now you can populate the PostgreSQL database with data that will be useful for development.
```
docker-compose run core ./opentreemap/manage.py migrate
docker-compose run core ./opentreemap/manage.py create_system_user
docker-compose run core ./opentreemap/manage.py createsuperuser --username super --email example@koduj.pl
docker-compose run core ./opentreemap/manage.py create_instance warszawa --url_name warszawa --user super --center=21.012230,52.229675
docker-compose run core ./opentreemap/manage.py shell < scripts/prepare_waw_instance.py
```

Last step is to prepare the static/javascript files for project.
```
docker-compose run core python opentreemap/manage.py collectstatic_js_reverse
docker-compose run core yarn run build
docker-compose run core python opentreemap/manage.py collectstatic --noinput
```

### ecobenefits
Please refer to README in ecobenefits repository to learn how to set up this service: https://github.com/kodujdlapolski/ecobenefits/blob/master/README.md

### Useful commands
Stop all services
```
docker-compose down
```

Execute command in particular service
```
docker-compose run ecobenefits python run.py
```

Remove all data from volumes (purges the database)
```
docker-compose down -v
```


For full installation instructions for the original project, see the [Github wiki](https://github.com/OpenTreeMap/otm-core/wiki/Installation-Guide).


## Other Repositories

This repository (ie, otm-core) is but one of a few separate repositories 
that together compose the OpenTreeMap project. Others include:

* [otm-tiler](https://github.com/kodujdlapolski/otm-tiler) - map tile
server based on [Windshaft](https://github.com/CartoDB/Windshaft)
* [ecobenefits](https://github.com/kodujdlapolski/ecobenefits) - ecosystem
benefits calculation service
* [otm-ios](https://github.com/OpenTreeMap/otm-ios) - An 
OpenTreeMap client for iOS devices.
* [otm-android](https://github.com/OpenTreeMap/otm-android) - An OpenTreeMap client for Android devices.


## Developer documentation
 - [Javascript module conventions](doc/js.md)
 - [Python mixins](doc/mixins.md)
