# **Welcome to the MOVIZ Visualization Tool 🎞📽**

## Overview
*MOVIZ* enables users to visualize trends in movie statistics ranging from small, independent projects to record-breaking blockbusters, from the earliest films to newest releases. The project implements a full data pipeline to ingest the most up-to-date data, to process and merge the datasets and create a database, and to visualize various graphs derived from the database.

### Features
The ![write-up](DATA440_Final_Project_Write-Up_(GitHub).pdf) for the project is available for further detail and dataset cleaning justification.
The project implements a full data pipeline and outputs an interative GUI:
- **Data Ingestion**
  - Automatically downloads and loads datasets from TMDb, IMDb Genres, and budget [project datasets](#Acknowledgements)
- **Data Cleaning & Transformation**
  - diagram of normalized column names and dataset equivalencies
  - dropped columns
  - missing values
  - transformations/assumptions included augmented/added columns
  - normalized fields
  - removed duplicates
  - removed adult films in tmdb.csv
  - limited to released movies (no upcoming or rumored, etc)
  - time spans from 1880 to 04/2025 to allow for leniency in the inclusion of the earliest movies. The basis for 1880 comes from the first motion picture created, the [*Roundhay Garden Scene*]([url](https://en.wikipedia.org/wiki/List_of_cinematic_firsts#:~:text=1888,the%20first%20motion%20picture%20recorded.)) in 1888. In line with released movies, MOVIZ is limited to movies released on or before April 2025.
  - genre_db certificates and developing equivalencies
  - 

**Relational Database Table Construction**
![MoVIZ Database Tables](MoVIZ_RDb.pdf)

**Interactive Visualization GUI**
The implementation has been created with Dash.


### Considerations

## Project Support
This project was built with Python **3.12.8** and uses [`uv`]([url](https://docs.astral.sh/uv/getting-started/installation/)) as for virtual environment and package management. MOVIZ's dependencies have been listed in `pyproject.toml`. The official documentation for the tool can be found [here]([url](https://docs.astral.sh/uv/)). 

To launch the application and begin visualization for the first time, clone the repository and run with ```python main.py```. Note: you will need to complete the dataset downloads, cleaning and mergging, and the database creation steps prior to launching the GUI.

## Project Structure
```
data/
├── processed/
├── raw/
logs/
src/
├── dash/
│   ├── dashboard_testing.py
│   └── movie_db.py
├── database/
│   └── database.py
├── downloading/
│   ├── downloading.py
│   └── webscraping.py
├── processing/
│   ├── cleaner_tools.py
│   ├── cleaning.py
│   └── merging.py
└── utils/
    ├── helpers.py
    └── logging.py
.gitattributes
.gitignore
.python-version
main.py
pyproject.toml
README.md
DATA440_Final_Project_Write-Up_(GitHub).pdf
MoVIZ_RDb.pdf
uv.lock
```

## Acknowledgements
This project is the combination of my love for movies and statistics. MOVIZ's data was collected from the following sources:
1. [u/asaniczka](https://github.com/asaniczka)'s ["Full TMDB Movies Dataset 2024 (1M Movies)"](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies) via Kaggle
2. [u/ChidambaraRaju](https://github.com/ChidambaraRaju)'s ['IMDb Movie Dataset: All Movies by Genre'](https://www.kaggle.com/datasets/rajugc/imdb-movies-dataset-based-on-genre) via Kaggle
3. Movie Budget data from [The-Numbers.com](https://www.the-numbers.com/movie/budgets/all)
4. Thank you to https://dbdiagram.io/home, which was used to create my database table logic