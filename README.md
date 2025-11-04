Simulation of the workshop *Mathe Macht Medikamente*
===
Jitao David Zhang, Rigani Jegatheeswaran, and David Weber

Ein Workshop für [Roche's Zukunftstag 2025](https://www.roche-registration.ch/zukunftstag-2025), in Zusammenarbeit mit dem Verein *WissensZukunft*.

## Quick Start (Streamlit App)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
# Create three sessions (morning, afternoon, test)
python scripts/initialize_sessions.py

# Generate test data (populates test_session with 29 teams)
python scripts/generate_test_data.py

# Check which session is currently active
python scripts/check_session.py

# Create a QR Code
python scripts/generate_qr_codes.py
```

### 3. Run the App
```bash
python -m streamlit run app.py --server.port 8504
```

### 4. Development Mode Features

**Current configuration (DEV_MODE = True):**
- **test_session**: Pre-populated with 29 teams
- **morning_session**: Empty - register teams via dropdown (no QR code)
- **afternoon_session**: Empty - register teams via dropdown (no QR code)

**Admin Dashboard**: http://localhost:8501 → Enter password

**Switch Sessions**: Admin Dashboard → Session Management → Select session

### 5. Session Structure

| Session | Purpose |
|---------|---------|
| `test_session` | Testing with pre-populated data |
| `morning_session` | Live morning workshop |
| `afternoon_session` | Live afternoon workshop |

**In development (DEV_MODE=True):**
- Teams select from dropdown (no QR code scanning needed)
- All three sessions available
- Switch between sessions in Admin Dashboard

**In production (DEV_MODE=False):**
- Teams MUST scan QR codes on tables
- Each table has unique QR code with team name
- Morning/afternoon sessions separated

---

## Setup the dependencies (Jupyter Notebook)

I tried two ways to setup the dependencies, i.e. the packages required by the Jupyter notebook, and either should work. You can choose whichever that fits you.

### Alternative 1 and the solution that I used: Use `pyenv` and `poetry`

Make sure you install [pyenv](https://github.com/pyenv/pyenv), which manages the Python version, and [poetry](https://python-poetry.org/docs/basic-usage/), which manages package dependencies.

I used `pyenv` 2.6.11 and `poetry` 2.2.1.

Install and initialize the local Python version.

```
pyenv install 3.11.0
pyenv local 3.11.0
poetry init
### To add dependencies
# poetry add numpy pandas matplotlib itables
# poetry add -D jupyter jupyterlab
## The project has been setup so that it can run out of the box
poetry install --no-root
```

Once this is done, you will have a local installation of the Python version 3.11.0, and all packages required to run the simulation.

### Alternative 2: Use `conda`

One could use conda as well

```
conda create -n zukunftstag2025 -c conda-forge numpy pandas matplotlib itables jupyter jupyterlab seaborn mplcursors ipympl ## the package list is NOT updated, you may have to adjust it
conda activate zukunftstag2025
```

When I set up my environment on my personal computer, I used the combination of `pyenv` and `poetry`. When I setup the environment on in my virtual box, I used the conda environment, because poetry failed due to SSL certificate issues (into which I wish to look deeper later). Both methods seem to work.

## Run the script

```
poetry run jupyter-lab 2025-10-Zukunftstag-simulation.ipynb
```

## Trouble shooting

* Install `sudo apt-get install libsqlite3-dev` in Debian before installing Python with pyenv, in case the error `No module named _sqlite3` pops up. See [stackoverflow](https://stackoverflow.com/questions/1210664/no-module-named-sqlite3)
