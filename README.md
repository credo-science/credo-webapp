# CREDO storage API

Implementation of credo storage API.

## Prerequisities

 * Python 3.x installation
 * Docker
 * Redis

## Running a local instance

To run a local instance:

Configure and start Redis server

```bash
./run.sh
docker exec -it credo-webapp bash
python3 manage.py migrate
python3 manage.py generate_sample_data
```

Web interface will be available at the displayed URL under the `/web/` path.

## API documentation
* [APIv2](credoapiv2)


## ACRA reporting
Endpoint for submitting crash reports (in JSON): `/acra/report`
