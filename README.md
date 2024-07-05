# Factorio-Blueprint-Generator

This tool generates a blueprint, from a specification of factories and flows.

## Goal
The intention is that the tool can integrate with solvers, so the solver provides the recipies to execute, the number of factories needed, the capacity between factory types.
This tool will then lay out the recipies to an acctual blueprint.



# Quick start

## Installation
```
clone Factorio-Bklueprint-Genrator
python -m venv .fbg
.fbg\Scripts\activate.bat
pip install -r requirements.txt
```

## Run test
```
pip install -r requirements-dev.txt
python -m unittest
```

## Regenerating server files
See following link for specific details and setup:
https://dev.to/maximsaplin/integrating-flutter-all-6-platforms-and-python-a-comprehensive-guide-4ipo

Specifically these commands, from the root of the repository, will regenerate server files

./starter-kit/prepare-sources.sh --proto service.proto --flutterDir app --pythonDir ./server/

./starter-kit/bundle-python.sh --flutterDir ./app --pythonDir ./server


## Build documentation
```
cd doc
make clean html
```
