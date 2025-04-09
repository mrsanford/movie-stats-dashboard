import os
import time
import requests
import pandas as pd
from io import StringIO
from tqdm import tqdm
from src.helpers import BUDGET_OUTPUT_PATH

# dummy headers and clean_money
headers = {"User-Agent": "Mozilla/5.0"}


def clean_money(value: int) -> int | None:
    """
    Converts currency strings to ints by removing symbols($) and reformatting
    ---
    Args:
        value (int) is the string value of the money amount
    Returns:
        Either (int) value of the money amount or None if string was empty
    """
    return (
        int(value.replace("$", "").replace(",", "").replace("\xa0", "").strip())
        if value.strip()
        else None
    )


def webscrape_budgets(
    save_path: str = BUDGET_OUTPUT_PATH,
    max_pages: int = 5,
) -> pd.DataFrame:
    """
    Scrapes movie budget data from The-Numbers.com and saves data to CSV
    ---
    Args:
        save_path (str) is the path for saving the output csv file
        max_pages (int) is the number of 100-row pages to scrape
        Note: default 5 pages will return 500 rows MAX
    Returns:
        pd.DataFrame is a cleaned DataFrame with all relevant data
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    base_url = "https://www.the-numbers.com/movie/budgets/all"
    all_budget_data = []

    for start in tqdm(range(0, max_pages * 100, 100), desc="Scraping pages"):
        url = base_url if start == 0 else f"{base_url}/{start + 1}"
        response = requests.get(url, headers=headers)

        try:
            df = pd.read_html(StringIO(response.text))[0]
        except ValueError:
            print(f"[Warning] No table found at start={start}")
            continue

        df.columns = [col.strip() for col in df.columns]
        if df.columns[0] != "Index":
            df.rename(columns={df.columns[0]: "Index"}, inplace=True)
        df.set_index("Index", inplace=True)

        for col in ["Production Budget", "Domestic Gross", "Worldwide Gross"]:
            df[col] = df[col].apply(clean_money)

        all_budget_data.append(df)
        time.sleep(1.5)

    final_df = pd.concat(all_budget_data).drop_duplicates()
    final_df.to_csv(save_path)
    print(f"Saved {len(final_df)} rows to {save_path}")
    return final_df
