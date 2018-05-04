# CREDO storage API

Implementation of credo storage API.

## Prerequisities

 * Python 2.7 installation
 * Pipenv (any recent version)

## Running a local instance

To run a local instance:

```bash
pipenv install
pipenv shell
python manage.py migrate
python manage.py generate_sample_data
python runserver
```

Web interface will be available at the displayed URL under the `/web/` path.

## API documentation
* [APIv1](credoapi)
* [APIv2](credoapiv2)


## ACRA reporting
Endpoint for submitting crash reports (in JSON): `/acra/report`
