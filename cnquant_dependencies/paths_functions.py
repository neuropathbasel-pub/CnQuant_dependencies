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
    bin_settings_string: str = make_bin_settings_string(
        bin_size=bin_size, min_probes_per_bin=min_probes_per_bin
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
    results_directory: Path,
    sentrix_ids_to_check: Optional[list[str] | set[str]] = None,
    downsize_to: str = CommonArrayType.NO_DOWNSIZING.value,
    logger: logging.Logger = logging.getLogger(name=__name__),
) -> list[str]:
    if not results_directory.exists() or not results_directory.is_dir():
        logger.warning(
            f"Results directory does not exist or is not a directory: {results_directory}"
        )
        return []

    detected_sentrix_ids = set(os.listdir(path=results_directory))

    if sentrix_ids_to_check is not None:
        detected_sentrix_ids = detected_sentrix_ids.intersection(
            set(sentrix_ids_to_check)
        )
    else:
        detected_sentrix_ids = detected_sentrix_ids

    available_sentrix_ids = [
        sentrix_id
        for sentrix_id in detected_sentrix_ids
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


def generate_summary_data_paths(
    base_output_directory: Path,
    bin_size: int,
    min_probes_per_bin: int,
    methylation_class: str,
    downsizing_target: str,
    preprocessing_method: str,
) -> tuple[Path, Path, Path]:
    """Generates file paths for summary data outputs, including metadata, plot data, and genes data.

    This function constructs the necessary directory structure and file paths based on the provided
    parameters. It creates the output directory if it does not exist.

    Args:
        base_output_directory (Path): The base directory where output files will be stored.
        bin_size (int): The bin size used in the analysis.
        min_probes_per_bin (int): The minimum number of probes per bin.
        methylation_class (str): The methylation class (e.g., a category like "hyper" or "hypo").
        downsizing_target (str): The target for downsizing (e.g., an array type or "no_downsizing").

    Returns:
        tuple[Path, Path, Path]: A tuple containing:
            - plot_save_path (Path): Path to the compressed JSON file for plot data (.json.zst).
            - genes_save_path (Path): Path to the Parquet file for genes data (.parquet).
            - metadata_path (Path): Path to the JSON file for metadata (.json).

    Notes:
        - The output directory is created under base_output_directory / bin_settings / methylation_class.
        - File names follow the pattern: {methylation_class}_{downsizing_target}_[suffix].
    """
    bin_settings_directory_string = make_bin_settings_string(
        bin_size=bin_size,
        min_probes_per_bin=min_probes_per_bin,
    )
    output_directory: Path = Path(
        base_output_directory / preprocessing_method / bin_settings_directory_string / methylation_class
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    save_name_prefix: Path = output_directory / Path(methylation_class)

    metadata_path: Path = save_name_prefix.with_name(
        name=f"{methylation_class}_{downsizing_target}_metadata.json"
    )
    plot_save_path: Path = save_name_prefix.with_name(
        name=f"{methylation_class}_{downsizing_target}.json.zst"
    )
    genes_save_path: Path = save_name_prefix.with_name(
        name=f"{methylation_class}_{downsizing_target}_genes.parquet"
    )
    return plot_save_path, genes_save_path, metadata_path


# def get_cnquant_output_data_paths(sentrix_id: str, downsize_to: CommonArrayType, file_type: str, output_directory: Path, preprocessing_method: str, bin_size: int, min_probes_per_bin: int)
#     path_prefix_bins = cnv_dir / Path(sentrix_id) /f"{sentrix_id}"
#     if downsize_to == CommonArrayType.NO_DOWNSIZING.value:
#         detail_path = Path(f"{path_prefix_bins}_detail.parquet")
#         segments_path = Path(f"{path_prefix_bins}_segments.parquet")
#     else:
#         detail_path = Path(f"{path_prefix_bins}_detail_{downsize_to}.parquet")
#         segments_path = Path(f"{path_prefix_bins}_segments_{downsize_to}.parquet")
#     pass

# current_results_directory = (
#             cnv_results_base_directory
#             / preprocessing_method
#             / make_bin_settings_string(
#                 bin_size=bin_size, min_probes_per_bin=min_probes_per_bin
#             )
#         )
