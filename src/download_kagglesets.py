## DOWNLOADS THE DATASETS FROM KAGGLE VIA KAGGLEHUB ##
import os
import shutil
import kagglehub
from src.utils.logging import setup_logger


def download_kaggle_dataset(
    kaggle_id: str,
    output_dir: str,
    target_filename: str = None,
    logger_name: str = "kaggle_downloader",
    log_filepath: str = "downloads",
) -> None:
    """
    Downloads a dataset from Kaggle and saves all CSVs to an output directory.
    Saves the logging progress.
    ---
    Args:
        kaggle_id (str): Kaggle dataset identifier (e.g., "username/dataset-name")
        output_dir (str): local directory to save the files
    """

    # calling the loggers
    logger = setup_logger(logger_name, log_filepath)
    logger.info(f"Downloading dataset '{kaggle_id}' to {output_dir}")

    download_path = kagglehub.dataset_download(kaggle_id)
    logger.info("Download complete")

    os.makedirs(output_dir, exist_ok=True)
    csv_files = [file for file in os.listdir(download_path) if file.endswith(".csv")]
    logger.info(f"Found {len(csv_files)} CSV files")

    for i, file in enumerate(csv_files):
        src = os.path.join(download_path, file)
        dst_name = target_filename if (target_filename and i == 0) else file
        dst = os.path.join(output_dir, dst_name)

        if not os.path.exists(dst):
            shutil.copy(src, dst)
            logger.info(f"Copied {file} → {dst}")
        else:
            logger.info(f"Skipped {file}. Already exists")
    return
