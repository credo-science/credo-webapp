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

API web interface will be available at the displayed URL under the `/web/` path.

## Interacting with the v1 API:

Somple payloads are available here: https://github.com/credo-science/sample-payloads. Interaction with the API can be done with curl, by issuing commands like:

```bash
curl -X POST --data @pingp.json http://127.0.0.1:8000
```
