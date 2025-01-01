# Factorio-Blueprint-Generator

This tool generates a blueprint, from a specification of factories and flows.

## Goal
The intention is that the tool can integrate with solvers, so the solver provides the recipies to execute, the number of factories needed, the capacity between factory types.
This tool will then lay out the recipies to an acctual blueprint.



# Quick start

## Installation
Download the source code
```
git clone Factorio-Blueprint-Generator
```

### With docker
This installs both dev and non-dev requirements for now.
```
docker build -t fbt .
```
To enter interactive environment
```
docker run -it fbt
```

### Without docker
To install the server execute the following steps:
```
cd server
python -m venv .fbg
.fbg\Scripts\activate.bat
pip install -r requirements.txt
```


## Run test
```
cd server
pip install -r requirements-dev.txt
python -m unittest
```


## Running server
To run the server:
```
cd server
python server.py
```

## Build documentation
The documentation is built with Sphinx
```
cd doc
make clean html
```

The server API is specified in OpenAPI file server/fbg-api.yaml
If the server runs at port 5000 on localhost, the API documentation
can be read at http://localhost:5000/ui
