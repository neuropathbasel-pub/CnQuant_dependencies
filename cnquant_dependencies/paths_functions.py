import os
import logging
from pathlib import Path
from typing import Optional, Union
from cnquant_dependencies.enums.CommonArrayType import CommonArrayType
from cnquant_dependencies.models.StatusJson import (
    check_if_previous_analysis_was_successful,
    get_status_json_path,

)
from cnquant_dependencies.bin_settings_functions import make_bin_settings_string

def get_sentrix_ids(idat_directory: Path) -> list[str]:
    """
    Retrieves a list of valid Sentrix IDs from a directory containing non-empty .idat files.
    This function scans the specified directory for files with the extensions
    '_Red.idat' and '_Grn.idat'. It then extracts the base names of these files
    (excluding the extensions) and returns a list of Sentrix IDs that have both
    corresponding '_Red.idat' and '_Grn.idat' files.
    Args:
        idat_directory (Path): The directory containing the .idat files.
    Returns:
        list[str]: A list of valid Sentrix IDs that have both '_Red.idat' and
                   '_Grn.idat' files in the specified directory.
    """
    red_files: list[str] = []
    grn_files: list[str] = []
    for file in os.listdir(path=idat_directory):
        if (
            file.endswith(".idat")
            and os.path.getsize(filename=os.path.join(idat_directory, file)) != 0
        ):
            if file.endswith("_Red.idat"):
                red_files.append(file.replace("_Red.idat", ""))
            elif file.endswith("_Grn.idat"):
                grn_files.append(file.replace("_Grn.idat", ""))
    valid_sentrix_ids = list(set(red_files) & set(grn_files))

    return valid_sentrix_ids


def get_precomputed_sample_ids(
    current_precomputed_cnv_directory: Path,
    rerun_failed_analyses: bool = False,
    downsize_to: str = CommonArrayType.NO_DOWNSIZING.value,
) -> set[str]:
    processed_sentrix_ids: set[str] = set()
    if os.path.exists(path=current_precomputed_cnv_directory):
        for sentrix_id in os.listdir(path=current_precomputed_cnv_directory):
            sentrix_id_directory: Path = Path(
                current_precomputed_cnv_directory / sentrix_id
            )
            file_suffix = f"{'_' + downsize_to if downsize_to != CommonArrayType.NO_DOWNSIZING.value else ''}"
            status_json_path: Path = (
                sentrix_id_directory / f"{sentrix_id}_status{file_suffix}.json"
            )

            if rerun_failed_analyses:
                analysis_successful: bool = check_if_previous_analysis_was_successful(
                    status_json_path=status_json_path
                )
                if not analysis_successful:
                    processed_sentrix_ids.add(sentrix_id)
            else:
                status_json_path_exists: bool = status_json_path.exists()

                if status_json_path_exists:
                    processed_sentrix_ids.add(sentrix_id)

    return processed_sentrix_ids


def sentrix_ids_to_process(
    idat_directory: Path,
    preprocessing_method: str,
    reference_sentrix_ids: set[str],
    CNV_base_output_directory: Path,
    bin_size: int,
    min_probes_per_bin: int,
    sentrix_ids_to_process: Optional[Union[list[str], set[str]]] = None,
    rerun_sentrix_ids: bool = False,
    downsize_to: str = CommonArrayType.NO_DOWNSIZING.value,
) -> set[str]:
    """
    Determine which Sentrix IDs need processing for CNV analysis based on specified parameters.

    Args:
        idat_directory (Path): Directory where IDAT files are stored.
        preprocessing_methods (list[str]): List of preprocessing methods to apply.
        reference_sentrix_ids (set[str]): Sentrix IDs to exclude from processing, e.g., reference samples.
        CNV_base_output_directory (Path): Base directory where preprocessed CNV data is stored.
        combinations (list[tuple[int, int]]): List of tuples where each tuple contains:
            - bin_size (int): Size of the bins for CNV analysis.
            - min_probes_per_bin (int): Minimum number of probes required per bin.

    Returns:
        dict[str, dict[str, list[tuple[int, int]]]]: A nested dictionary where:
            - The outer key is the preprocessing method.
            - The inner key is a Sentrix ID that needs processing.
            - The value is a list of tuples, each containing bin size and min probes per bin,
              indicating the settings for which this Sentrix ID has not yet been processed.

    Notes:
        - The function uses helper functions `get_sentrix_ids` and `get_precomputed_sample_ids`
          to gather existing and precomputed IDs respectively.
        - Prints the number of remaining samples to process for each combination of settings.
    """

    available_sample_ids = (
        set(get_sentrix_ids(idat_directory=idat_directory)) - reference_sentrix_ids
    )
    if sentrix_ids_to_process is not None:
        available_sample_ids = available_sample_ids.intersection(
            set(sentrix_ids_to_process)
        )

    bin_settings_string: str = (
        f"bin_size_{bin_size}_min_probes_per_bin_{min_probes_per_bin}"
    )

    current_precomputed_cnv_directory = (
        CNV_base_output_directory / preprocessing_method / bin_settings_string
    )

    if rerun_sentrix_ids:
        precomputed_sentrix_ids = set()
    else:
        precomputed_sentrix_ids = get_precomputed_sample_ids(
            current_precomputed_cnv_directory=current_precomputed_cnv_directory,
            rerun_failed_analyses=rerun_sentrix_ids,
            downsize_to=downsize_to,
        )

    current_missing_sentrix_ids = available_sample_ids - precomputed_sentrix_ids

    return current_missing_sentrix_ids

def get_only_processed_sentrix_ids(
    sentrix_ids_to_check: list[str] | set[str] | None,
    results_directory: Path,
    downsize_to: str = CommonArrayType.NO_DOWNSIZING.value,
    logger: logging.Logger = logging.getLogger(name=__name__),
) -> list[str]:
    """Retrieves a list of Sentrix IDs that have been successfully processed based on status JSON files.
    
    Args:
        sentrix_ids_to_check (list[str] | set[str] | None): Optional list or set of Sentrix IDs to filter by. 
            If None, checks all subdirectories in results_directory.
        results_directory (Path): The directory containing subdirectories for each Sentrix ID.
        downsize_to (str): The downsize option for status JSON path generation. Defaults to NO_DOWNSIZING.
        logger (logging.Logger): Logger for recording warnings/errors.
    
    Returns:
        list[str]: A list of Sentrix IDs that have successful status JSON files.
    
    Notes:
        - Only considers subdirectories in results_directory.
        - Logs warnings for missing directories or status files but does not raise errors.
    """
    if not results_directory.exists() or not results_directory.is_dir():
        logger.warning(f"Results directory does not exist or is not a directory: {results_directory}")
        return []
    
    try:
        all_subdirs = {p.name for p in results_directory.iterdir() if p.is_dir()}
    except OSError as e:
        logger.error(f"Error listing subdirectories in {results_directory}: {e}")
        return []
    
    if sentrix_ids_to_check is not None:
        sentrix_ids_set = set(sentrix_ids_to_check)
        analyzed_sentrix_ids = all_subdirs & sentrix_ids_set
    else:
        analyzed_sentrix_ids = all_subdirs
    
    available_sentrix_ids = [
        sentrix_id for sentrix_id in analyzed_sentrix_ids
        if check_if_previous_analysis_was_successful(
            status_json_path=get_status_json_path(
                sentrix_id=sentrix_id,
                sentrix_id_directory=results_directory / sentrix_id,
                downsize_to=downsize_to,
            ),
            logger=logger,
        )
    ]
    
    return available_sentrix_ids