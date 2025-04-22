# **Welcome to the MOVIZ Visualization Tool 🎞📽**

## Overview
*MOVIZ* enables users to explore trends and discover hidden trends in movie statistics from small, independent projects to record-breaking blockbusters, from the earliest films to newest releases.

### Features
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
- **Relational Database Construction**
  Including the RDB table schema

- **Interactive Visualization GUI**


### Considerations

## Project Support
This project was built with Python **3.12.8** and uses [`uv`]([url](https://docs.astral.sh/uv/getting-started/installation/)) as the virtual environment and package manager. MOVIZ's dependencies have been listed in `pyproject.toml`. The official documentation for the tool can be found [here]([url](https://docs.astral.sh/uv/)). 

To launch the application and to begin visualization, clone the repository and run the GUI with
```python main.py```

## Project Structure
```
```

## Acknowledgements
The inspiration for this project comes from my love of movies, statistics, and Letterboxd. The data from the project was collected from the following sources:
1. [u/asaniczka]([url](https://github.com/asaniczka))'s ['Full TMDB Movies Dataset 202 (1M Movies)'](([url](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies))) via Kaggle
2. [u/ChidambaraRaju]([url](https://github.com/ChidambaraRaju))'s ['IMDb Movie Dataset: All Movies by Genre']([url](https://www.kaggle.com/datasets/rajugc/imdb-movies-dataset-based-on-genre)) via Kaggle
3. Movie Budget webpages from [The-Numbers.com]([url](https://www.the-numbers.com/movie/budgets/all))
