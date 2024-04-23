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

## Build documentation
```
cd doc
make clean html
```
