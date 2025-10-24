Simulation of the workshop *Mathe Macht Medikamente*
===
Roche's Zukunftstag 2025

## Setup

Make sure you install [pyenv](https://github.com/pyenv/pyenv), which manages the Python version, and [poetry](https://python-poetry.org/docs/basic-usage/), which manages package dependencies.

I used `pyenv` 2.6.11 and `poetry` 2.2.1.

Install and initialize the local Python version.

```
pyenv install 3.11.0
pyenv local 3.11.0
poetry init
poetry add numpy pandas matplotlib itables
poetry add -D jupyterlab ## libraries for development use only
poetry install --no-root
```

Once this is done, you will have a local installation of the Python version 3.11.0, and all packages required to run the simulation.

## Run the script

```
poetry run jupyter-lab 
