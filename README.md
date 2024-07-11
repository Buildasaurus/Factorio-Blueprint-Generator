# Factorio-Blueprint-Generator

This tool generates a blueprint, from a specification of factories and flows.

## Goal
The intention is that the tool can integrate with solvers, so the solver provides the recipies to execute, the number of factories needed, the capacity between factory types.
This tool will then lay out the recipies to an acctual blueprint.



# Quick start

## Installation
```
clone Factorio-Blueprint-Generator
python -m venv .fbg
.fbg\Scripts\activate.bat
pip install -r requirements.txt
```

## Run test
```
pip install -r requirements-dev.txt
python -m unittest
```

## Running server & UI
To run the server, navigate to the ./server folder and run
´´´
py server.py
´´´

The UI requires the Dart SDK and flutter to run. Follow the Dart SDK installation guide
https://dart.dev/get-dart

When installed the project can be built to your local machine with
```
flutter run
```
Or in vsc open the main.dart and press f5, or "Start" button.

The ui can run without the server, but won't be able to generate blueprints.


## Build documentation
```
cd doc
make clean html
```
