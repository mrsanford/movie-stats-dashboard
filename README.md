# **MOVIZ Visualization Tool 🎞**

## Overview -- Welcome to MoVIZ
*MOVIZ* enable users to visualize movie statistics ranging from budget indie projects to record-breaking blockbusters, from the earliest films to newest releases. The project implements a full data pipeline to ingest up-to-date datasets from TMDB, IMDb, and *The Numbers* budget dataset, applying normalization and various cleaning methods, and a robust database. The MoVIZ database contains a wide array of films from 1880 to 2025. Users can filter their desired characteristics, analyze, and visualize relationships between genres, decades, certificates, ratings, production budgets, and worldwide box office gross, all with a user-friend GUI. 

### Features

The project implements a full data pipeline and outputs an interactive GUI:
- **Data Ingestion**
  - Automatically downloads and loads datasets from TMDB, IMDb Genres, and budget [project datasets](#Acknowledgements)
- **Data Cleaning & Transformation**
  - diagram of normalized column names and dataset equivalencies
  - dropped columns
  - missing values
  - transformations/assumptions included augmented/added columns
  - normalized fields
  - removed duplicates
  - removed adult films in tmdb.csv
  - limited to released movies (no upcoming or rumored, etc.)
  - time spans from 1880 to 04/2025 to allow for leniency in the inclusion of the earliest movies. The basis for 1880 comes from the first motion picture created, the [*Roundhay Garden Scene*]([url](https://en.wikipedia.org/wiki/List_of_cinematic_firsts#:~:text=1888,the%20first%20motion%20picture%20recorded.)) in 1888. In line with released movies, MOVIZ is limited to movies released on or before April 2025.
  - genre_db certificates and developing equivalencies
  - 

**Relational Database Table Construction**
Below is the relational database structure used for MoVIZ
<p align="center">
  <img src="MoVIZ_RDb.png" width="500" alt="MoVIZ Database Tables Diagram">
</p>


**Interactive Visualization GUI**
The implementation has been created with Dash.

### Considerations
- Due to GitHub's max limit on the size of dataset files, I have opted not to push /processed and /raw files and folders; however, the framework will populate and become available upon cloning the repository and running the pipeline.
- While *The Numbers* contains comprehensive financial coverage for roughly ~6000 films, please be aware that movies filtered on financial data may be limited in offerings compared to the larger offerings of films by TMDB and the IMDb datasets.
- If you would like more information on the project details, especially regarding dataset cleaning justification and related processes, the ![write-up](DATA440_Final_Project_Write-Up_(GitHub).pdf) is available.
  - Note: In my references, I mention an IMDb dataset and a genres dataset-- they are the same and the names are used interchangeably.

## Project Support
This project was built with Python **3.12.8** and uses [`uv`]([url](https://docs.astral.sh/uv/getting-started/installation/)) as for virtual environment and package management. MOVIZ's dependencies have been listed in `pyproject.toml`. The official documentation for the tool can be found [here]([url](https://docs.astral.sh/uv/)). 

To launch the application and begin visualization for the first time, clone the repository and run with ```python main.py```. Note: you will need to complete the dataset downloads, cleaning and merging, and the database creation steps prior to launching the GUI.

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
This project is product of my love for movies and statistics. MOVIZ's data was collected from the following sources:
1. [u/asaniczka](https://github.com/asaniczka)'s ["Full TMDB Movies Dataset 2024 (1M Movies)"](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies) via Kaggle
2. [u/ChidambaraRaju](https://github.com/ChidambaraRaju)'s ['IMDb Movie Dataset: All Movies by Genre'](https://www.kaggle.com/datasets/rajugc/imdb-movies-dataset-based-on-genre) via Kaggle
3. Movie Budget data from [The-Numbers.com](https://www.the-numbers.com/movie/budgets/all)
4. Thank you to https://dbdiagram.io/home, which was used to create my database table logic