import os
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Union
from collections import defaultdict
from cnquant_dependencies.enums.CommonArrayType import CommonArrayType
from cnquant_dependencies.models.StatusJson import (
    check_if_previous_analysis_was_successful,
    get_status_json_path,
)
from cnquant_dependencies.bin_settings_functions import make_bin_settings_string

ENDING_CONTROL_PROBES: str = "_control-probes"
ENDING_GRN = "_Grn.idat"
ENDING_RED = "_Red.idat"
ENDING_GZ = ".gz"
ENDING_SUFFIXES = ("_Grn.idat", "_Red.idat", "_Grn.idat.gz", "_Red.idat.gz")

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

# TODO: Convert to Path
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
    create_directory: bool = True,
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
    if create_directory:
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

def get_available_summary_plots(
    summary_plots_base_directory: Path,
    genes_file_suffix: str = "_genes.parquet",
    plot_file_suffix: str = ".json.zst",
    logger: logging.Logger = logging.getLogger(name=__name__),
) -> dict[str,dict[tuple[int,int],dict[str,list[str]]]]:
    """
    Scans the summary plots base directory to identify available preprocessing methods,
    bin settings, and methylation classes with their associated downsizing targets.

    The function expects a directory structure like:
    summary_plots_base_directory/
    ├── preprocessing_method1/
    │   ├── bin_size_min_probes/
    │   │   ├── results_directory1/
    │   │   │   ├── results_prefix_target1_genes.parquet
    │   │   │   ├── results_prefix_target1.json.zst
    │   │   │   └── ...
    │   │   └── results_directory2/
    │   └── ...
    └── preprocessing_method2/
        └── ...

    For each bin settings directory (e.g., "50000_20"), it extracts bin_size and min_probes
    from the name. For each results directory, it collects genes files and plot files,
    strips the results_prefix and suffixes, and ensures they match in count.

    Args:
        summary_plots_base_directory (Path): The root directory containing preprocessing method subdirectories.
        genes_file_suffix (str, optional): Suffix for genes files (default: "_genes.parquet").
        plot_file_suffix (str, optional): Suffix for plot files (default: ".json.zst").

    Returns:
        dict: A nested dictionary with the following structure:
            {
                "preprocessing_method": {
                    (bin_size, min_probes): {
                        "results_directory_name": ["target1", "target2", ...]
                    }
                }
            }
            - Keys at top level: preprocessing method names (str).
            - Keys at second level: tuples of (bin_size: int, min_probes: int).
            - Keys at third level: results directory names (str).
            - Values at third level: lists of downsizing targets (str), derived from genes file names.

    Raises:
        ValueError: If the number of genes files does not match the number of plot files in any results directory.
    """
    available_methylation_classes = dict()
    for preprocessing_method in [
        item.name for item in summary_plots_base_directory.iterdir() if item.is_dir()
    ]:
        available_methylation_classes[preprocessing_method] = defaultdict(
            dict[str, list[str]]
        )
        for available_settings in [
            item.name
            for item in Path(
                summary_plots_base_directory / preprocessing_method
            ).iterdir()
            if item.is_dir()
        ]:
            integers: list[int] = list()
            parts = available_settings.split("_")
            for part in parts:
                if part.isdigit():
                    integers.append(int(part))

            available_methylation_classes[preprocessing_method][
                (integers[0], integers[1])
            ] = dict()
            for results_directory in [
                item
                for item in Path(
                    summary_plots_base_directory
                    / preprocessing_method
                    / available_settings
                ).iterdir()
                if item.is_dir()
            ]:
                genes_files_downsizing_targets = []
                plots_downsizing_targets = []
                results_prefix = f"{results_directory.name}_"
                for file in results_directory.iterdir():
                    if file.name.endswith(plot_file_suffix):
                        plots_downsizing_targets.append(
                            file.name.replace(results_prefix, "").rstrip(
                                plot_file_suffix
                            )
                        )
                    if file.name.endswith(genes_file_suffix):
                        genes_files_downsizing_targets.append(
                            file.name.replace(results_prefix, "").rstrip(
                                genes_file_suffix
                            )
                        )
                if len(genes_files_downsizing_targets) != len(plots_downsizing_targets):
                    logger.error(
                        msg=f"Number of genes files ({len(genes_files_downsizing_targets)}) does not match number of plot files ({len(plots_downsizing_targets)}) in {results_directory}."
                    )
                    raise ValueError(
                        f"Number of genes files ({len(genes_files_downsizing_targets)}) does not match number of plot files ({len(plots_downsizing_targets)}) in {results_directory}."
                    )
                available_methylation_classes[preprocessing_method][
                    (integers[0], integers[1])
                ][results_directory.name] = genes_files_downsizing_targets

    return available_methylation_classes

def get_combined_plot_path(
    base_output_directory: Path,
    bin_size: int,
    min_probes_per_bin: int,
    methylation_class: str,
    preprocessing_method: str,
    file_name_suffix: str = "combined",
    create_directory: bool = True,
) -> Path:
    """Generates the file path for a combined plot data file in compressed JSON format.
    
    This function constructs the output directory path based on the provided parameters
    and creates the directory if it does not exist (when create_directory is True).
    The file path follows the naming convention for combined plot data.
    
    Args:
        base_output_directory (Path): The base directory where output files will be stored.
        bin_size (int): The bin size used in the analysis.
        min_probes_per_bin (int): The minimum number of probes per bin.
        methylation_class (str): The methylation class (e.g., a category like "hyper" or "hypo").
        preprocessing_method (str): The preprocessing method used (e.g., "quantile").
        file_name_suffix (str, optional): Suffix for the file name (default: "combined").
        create_directory (bool, optional): Whether to create the output directory if it doesn't exist. Defaults to True.
    
    Returns:
        Path: The full path to the compressed JSON plot file (.json.zst).
    
    Notes:
        - The output directory is created under base_output_directory / preprocessing_method / bin_settings / methylation_class.
        - File name follows the pattern: {methylation_class}_{file_name_suffix}.json.zst.
    """
    bin_settings_directory_string: str = make_bin_settings_string(
        bin_size=bin_size,
        min_probes_per_bin=min_probes_per_bin,
    )
    output_directory: Path = Path(
        base_output_directory / preprocessing_method / bin_settings_directory_string / methylation_class
    )
    if create_directory:
        output_directory.mkdir(parents=True, exist_ok=True)

    save_name_prefix: Path = output_directory / Path(methylation_class)

    plot_save_path: Path = save_name_prefix.with_name(
        name=f"{methylation_class}_{file_name_suffix}.json.zst"
    )

    return plot_save_path

def is_valid_idat_basepath(basepath):
    """Checks if the given basepath(s) point to valid IDAT files."""
    if not isinstance(basepath, list):
        basepath = [basepath]
    basepath = [str(x) for x in basepath]
    return all(
        (os.path.exists(x + ENDING_GRN) or os.path.exists(x + ENDING_GRN + ENDING_GZ))
        and (
            os.path.exists(x + ENDING_RED) or os.path.exists(x + ENDING_RED + ENDING_GZ)
        )
        for x in basepath
    )

def idat_basepaths(files: list[str], only_valid=False):
    """Returns unique basepaths from IDAT files or directory.

    This function processes a list of IDAT files or a directory containing IDAT
    files and returns their basepaths by removing the file endings. The
    function ensures that there are no duplicate basepaths in the returned list
    and maintains the order of the files as they appear in the input.

    Args:
        files (path or list): A file or directory path or a list of file paths.
        only_valid (bool): If True, only returns basepaths that point to valid
            IDAT file pairs. Defaults is 'False'.

    Returns:
        list: A list of unique basepaths corresponding to the provided IDAT
            files. If a directory is provided, all IDAT files are recursively
            considered.

    Example:
        >>> idat_basepaths("/path/to/dir")
        [PosixPath('/path/to/dir/file1'), PosixPath('/path/to/dir/file2')]

        >>> idat_basepaths(["/path1/file1_Grn.idat", "/path2/file2_Red.idat"])
        [PosixPath('/path1/file1'), PosixPath('/path2/file2')]

        >>> idat_basepaths("/path/to/idat/file_Grn.idat.gz")
        [PosixPath('/path/to/idat/file')]
    """

    def get_idat_files(file_or_dir):
        path = os.path.expanduser(file_or_dir)
        # If path is dir take all files in it
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path, followlinks=True):
                for filename in filenames:
                    if filename.endswith(ENDING_SUFFIXES):
                        yield os.path.join(dirpath, filename)
        else:
            yield path

    def strip_suffix(file_path):
        for suffix in ENDING_SUFFIXES:
            if file_path.endswith(suffix):
                return file_path[: -len(suffix)]
        return file_path

    if not isinstance(files, list):
        files = [files]
    _files = [
        strip_suffix(idat_file)
        for file_or_dir in files
        for idat_file in get_idat_files(file_or_dir)
    ]
    # Remove duplicates, keep ordering
    unique_basepaths_dict = dict.fromkeys(_files)
    if only_valid:
        return [
            Path(base) for base in unique_basepaths_dict if is_valid_idat_basepath(base)
        ]
    return [Path(base) for base in unique_basepaths_dict]

def idat_paths_from_basenames(basenames):
    """Returns paths to green and red IDAT files.

    Args:
        basenames (list): List of basepaths for IDAT files.

    Returns:
        tuple: Paths to green and red IDAT files.

    Raises:
        FileNotFoundError: If any IDAT file is not found.
    """
    grn_idat_files = np.array([Path(str(name) + ENDING_GRN) for name in basenames])
    red_idat_files = np.array([Path(str(name) + ENDING_RED) for name in basenames])

    def check_and_fix(files):
        not_existing = [i for i, path in enumerate(files) if not path.exists()]
        files[not_existing] = [
            x.parent / (x.name + ENDING_GZ) for x in files[not_existing]
        ]
        return next((x for x in files[not_existing] if not x.exists()), None)

    not_found = check_and_fix(grn_idat_files)
    not_found = check_and_fix(red_idat_files) if not_found is None else not_found
    if not_found is not None:
        idat_file = str(not_found).replace(ENDING_GZ, "")
        msg = f"IDAT file not found: {idat_file}."
        raise FileNotFoundError(msg)
    return grn_idat_files, red_idat_files