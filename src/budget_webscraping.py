import os
import time
import requests
import pandas as pd
from io import StringIO
from tqdm import tqdm
from src.helpers import BUDGET_RAW_FILE
from src.utils.logging import setup_logger

# dummy headers and clean_money
headers = {"User-Agent": "Mozilla/5.0"}
logger = setup_logger("budget_scraper", "webscrape_budgets")


def clean_money(value: int) -> int | None:
    """
    Converts currency strings to ints by removing symbols($) and reformatting
    ---
    Args: value (int) is the string value of the money amount
    Returns: the (int) value of the money amount or None if string was empty
    """
    return (
        int(value.replace("$", "").replace(",", "").replace("\xa0", "").strip())
        if value.strip()
        else None
    )


def webscrape_budgets(
    budget_path: str = BUDGET_RAW_FILE,
    max_pages: int = 1,
) -> pd.DataFrame:
    """
    Scrapes movie budget data from The-Numbers.com and saves data to CSV
    ---
    Args:
        budget_path (str) is the path for saving the output csv file
        max_pages (int) is the number of 100-row pages to scrape
        Note: default 5 pages will return 500 rows MAX
    Returns:
        pd.DataFrame is a cleaned DataFrame with all relevant data
    """
    # makes the directory for the save path
    os.makedirs(os.path.dirname(budget_path), exist_ok=True)
    base_url = "https://www.the-numbers.com/movie/budgets/all"
    all_budget_data = []

    logger.info(f"Beginning scrape for ~{max_pages * 100} films")
    # loops over the available webpages
    for start in tqdm(range(0, max_pages * 100, 100), desc="Scraping pages"):
        url = base_url if start == 0 else f"{base_url}/{start + 1}"
        response = requests.get(url, headers=headers)
        logger.info(f"Scraping URL: {url}")
        try:
            df = pd.read_html(StringIO(response.text))[0]
        except ValueError:
            logger.warning(f"No table found at start={start}")
            continue

        df.columns = [col.strip() for col in df.columns]
        if df.columns[0] != "Index":
            df.rename(columns={df.columns[0]: "Index"}, inplace=True)
        df.set_index("Index", inplace=True)

        # cleans columns with monetary values and turns them into ints
        for col in ["Production Budget", "Domestic Gross", "Worldwide Gross"]:
            df[col] = df[col].apply(clean_money)
        all_budget_data.append(df)
        time.sleep(1.5)

    # if the save path exists, reads the dataframe of existing data
    if os.path.exists(budget_path):
        existing_df = pd.read_csv(budget_path, index_col=0)
    else:
        existing_df = pd.DataFrame()
    if all_budget_data:
        new_df = pd.concat(all_budget_data).drop_duplicates()
        final_df = pd.concat([existing_df, new_df]).drop_duplicates()
        logger.info(
            f"Saving final dataset with {final_df.shape[0]} rows to {budget_path}"
        )
        final_df.to_csv(budget_path)
        return final_df
    else:
        logger.warning("No new data scraped.")
        return existing_df
