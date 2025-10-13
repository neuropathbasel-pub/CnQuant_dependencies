import orjson
import time
import traceback
import logging
from cnquant_dependencies.enums.CommonArrayType import CommonArrayType
from typing import Optional
from pathlib import Path



class StatusJson:
    """
    Represents the status and metadata of a CQcalc analysis for a given Sentrix ID.

    This class encapsulates all relevant information about the analysis process, including input parameters,
    timing data, completion status, and output paths. It provides methods to generate a JSON representation
    of the status and save it to disk. The logger is injected optionally for flexible logging without hard
    dependencies.

    Attributes:
        sentrix_id (str): The unique identifier for the sample.
        idat_directory (str | Path): Directory containing the IDAT files.
        preprocessing_method (str): The preprocessing method used.
        min_probes_per_bin (int): Minimum number of probes required per bin.
        bin_size (int): Size of the bins used in analysis.
        sentrix_id_output_directory (str | Path): Directory for output results.
        reference_sentrix_ids (Optional[str]): Reference Sentrix IDs, if any.
        array_type (Optional[str]): Type of the array used.
        red_idat_size (float): Size of the red IDAT file in MB.
        green_idat_size (float): Size of the green IDAT file in MB.
        failure_reason (Optional[str]): Reason for failure, if any.
        completion_status (Optional[bool]): Whether the analysis completed successfully.
        raw_data_parsing_time (Optional[float]): Time taken for raw data parsing in seconds.
        data_analysis_timing (Optional[float]): Time taken for data analysis in seconds.
        data_downsized (bool): Whether the data was downsized.
        logger (logging.Logger): Logger instance for logging messages (defaults to a basic logger if not provided).
    """
    def __init__(
        self,
        sentrix_id: str,
        idat_directory: str | Path,
        preprocessing_method: str,
        min_probes_per_bin: int,
        bin_size: int,
        sentrix_id_output_directory: str | Path,
        reference_sentrix_ids: Optional[str] = None,
        array_type: Optional[str] = None,
        red_idat_size: float = 0,
        green_idat_size: float = 0,
        failure_reason: Optional[str] = None,
        completion_status: Optional[bool] = None,
        raw_data_parsing_time: Optional[float] = None,
        data_analysis_timing: Optional[float] = None,
        downsize_to: str = "NO_DOWNSIZING",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initializes the StatusJson instance with analysis metadata.

        Args:
            sentrix_id (str): The unique identifier for the sample.
            idat_directory (str | Path): Directory containing the IDAT files.
            preprocessing_method (str): The preprocessing method used.
            min_probes_per_bin (int): Minimum number of probes required per bin.
            bin_size (int): Size of the bins used in analysis.
            sentrix_id_output_directory (str | Path): Directory for output results.
            reference_sentrix_ids (Optional[str]): Reference Sentrix IDs, if any. Defaults to None.
            array_type (Optional[str]): Type of the array used. Defaults to None.
            red_idat_size (float): Size of the red IDAT file in MB. Defaults to 0.
            green_idat_size (float): Size of the green IDAT file in MB. Defaults to 0.
            failure_reason (Optional[str]): Reason for failure, if any. Defaults to None.
            completion_status (Optional[bool]): Whether the analysis completed successfully. Defaults to None.
            raw_data_parsing_time (Optional[float]): Time taken for raw data parsing in seconds. Defaults to None.
            data_analysis_timing (Optional[float]): Time taken for data analysis in seconds. Defaults to None.
            data_downsized (bool): Whether the data was downsized. Defaults to False.
            logger (Optional[logging.Logger]): Logger instance for logging. Defaults to a basic logger if not provided.
        """
        self.logger = logger or logging.getLogger(name=__name__)
        self.idat_directory: str | Path = idat_directory
        self.sentrix_id: str = sentrix_id
        self.preprocessing_method: str = preprocessing_method
        self.min_probes_per_bin: int = min_probes_per_bin
        self.bin_size: int = bin_size
        self.array_type: Optional[str] = array_type
        self.red_idat_size: float = red_idat_size
        self.green_idat_size: float = green_idat_size
        self.failure_reason: Optional[str] = failure_reason
        self.data_analysis_timing: Optional[float] = data_analysis_timing
        self.reference_sentrix_ids: Optional[str] = reference_sentrix_ids
        self.completion_status: Optional[bool] = completion_status
        self.sentrix_id_output_directory: str | Path = sentrix_id_output_directory
        self.raw_data_parsing_time: Optional[float] = raw_data_parsing_time
        self.downsize_to: Optional[str] = downsize_to

    def make_status_json(self) -> dict[str, str | dict[str,str]]:
        """
        Generates a dictionary representation of the analysis status for JSON serialization.

        Returns:
            dict[str, str | dict[str, str]]: A nested dictionary containing status data, including
            completion status, input details, timing, and settings.
        """
        status_data: dict = {
            "analysis_completed_successfully": str(self.completion_status) if self.completion_status is not None else "False",
            "sentrix_id": self.sentrix_id,
            "array_type": str(self.array_type) if self.array_type is not None else "N/A",
            "failure_reason": self.failure_reason if self.failure_reason is not None else "N/A",
            "timestamp": str(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())),
            "analysis_settings": {
                "bin_size": str(self.bin_size),
                "min_probes_per_bin": str(self.min_probes_per_bin),
                "downsized_to": self.downsize_to,
            },
            "input_data": {
                "input_directory": str(self.idat_directory),
                "red_idat_size": f"{self.red_idat_size} MB",
                "green_idat_size": f"{self.green_idat_size} MB",
                "reference_sentrix_ids": self.reference_sentrix_ids if self.reference_sentrix_ids is not None else "N/A",
                "preprocessing_method": self.preprocessing_method,
            },
            "results_output_directory": str(self.sentrix_id_output_directory),
            "time_taken": {
                "Raw data parsing time [s]": f"{self.raw_data_parsing_time:.2f}" if self.raw_data_parsing_time is not None else "N/A",
                "Data analysis time [s]":f"{self.data_analysis_timing:.2f}" if self.data_analysis_timing is not None else "N/A",
                },
        }
        return status_data
    
    def save_to_disk(self, file_suffix: str) -> None:
        """
        Saves the status JSON to disk in the specified output directory.

        Creates the output directory if it does not exist, then writes the JSON data to a file
        named after the Sentrix ID with the given suffix.

        Args:
            file_suffix (str): Suffix to append to the filename (e.g., "_final").

        Raises:
            PermissionError: If there are permission issues writing to the directory.
            Exception: For other errors during saving, logged via the logger.
        """
        
        status_json_path = Path(self.sentrix_id_output_directory) / f"{self.sentrix_id}_status{file_suffix}.json"
        
        try:
            status_json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(
                file=status_json_path,
                mode="wb",
            ) as f:
                f.write(orjson.dumps(self.make_status_json(), option=orjson.OPT_INDENT_2))
        except PermissionError:
            error_message = traceback.format_exc()
            raise PermissionError(f"Permission error while trying to save analysis status json to {status_json_path}. Please check the directory permissions.\nself.sentrix_id_output_directory: {self.sentrix_id_output_directory}")
        except Exception:
            error_message = traceback.format_exc()
            self.logger.critical(
                msg=f"There was following error while saving analysis status json:\n{error_message}",
            )
        return None
    
def get_status_json_path(sentrix_id: str, sentrix_id_directory: Path, downsize_to: str = CommonArrayType.NO_DOWNSIZING.value) -> Path:
    """Generates the path to a status JSON file based on the sentrix ID, directory, and downsize option.
    
    Args:
        sentrix_id (str): The sentrix ID used as the base name for the file.
        sentrix_id_directory (Path): The directory where the status JSON file is located.
        downsize_to (str): The downsize option (e.g., a CommonArrayType value). Defaults to NO_DOWNSIZING.value, which adds no suffix.
    
    Returns:
        Path: The full path to the status JSON file, including any downsize suffix if applicable.
    """
    file_suffix = f"{'_' + downsize_to if downsize_to != CommonArrayType.NO_DOWNSIZING.value else ''}"
    status_json_path: Path = (
        sentrix_id_directory / f"{sentrix_id}_status{file_suffix}.json"
    )
    return status_json_path
    
def load_analysis_status_json(status_json_path: str | Path, logger = logging.getLogger(name=__name__)) -> dict[str, str | dict[str,str]]:
    """Loads and parses a JSON file containing analysis status data.
    
    Args:
        status_json_path (str | Path): The path to the JSON file to load.
    
    Returns:
        dict[str, Any]: The parsed JSON data as a dictionary. Returns an empty dict if the file does not exist.
    
    Raises:
        ValueError: If the file exists but contains invalid JSON or is not a dictionary.
        OSError: If there are file I/O issues (e.g., permission denied).
    """
    path = Path(status_json_path)
    if not path.exists():
        logger.warning(f"Status JSON file does not exist: {path}")
        return {}
    
    try:
        with path.open("rb") as file:
            data = orjson.loads(file.read())
            if not isinstance(data, dict):
                raise ValueError(f"Loaded data is not a dictionary: {type(data)}")
            return data
    except orjson.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {path}: {e}")
        raise ValueError(f"Failed to decode JSON from {path}: {e}")
    except OSError as e:
        logger.error(f"File I/O error for {path}: {e}")
        raise OSError(f"Unable to read file {path}: {e}")
    
def check_if_previous_analysis_was_successful(
    status_json_path: str | Path, logger = logging.getLogger(name=__name__)
) -> bool:
    """
    Checks if a previous analysis was successful by reading a status JSON file.

    This function verifies the existence of the specified JSON file and parses it to determine
    if the analysis completed successfully. It looks for the key "analysis_completed_successfully"
    in the JSON and checks if its value is "true" (case-insensitive). If the file does not exist
    or the status is not "true", it returns False.

    Args:
        status_json_path (str | Path): The path to the JSON file containing the analysis status.

    Returns:
        bool: True if the analysis was successful, False otherwise.

    Raises:
        PermissionError: If there is a permission issue reading the file.
    """
    status: bool = False
    if Path(status_json_path).exists():
        try:
            with open(file=status_json_path, mode="rb") as file:
                status_json = orjson.loads(file.read())
                status: bool = (
                    True
                    if status_json.get("analysis_completed_successfully").lower()
                    == "true"
                    else False
                )
        except PermissionError:
            raise PermissionError(f"Permission denied for reading {status_json_path}.")
        except Exception as e:
            logger.critical(f"Error reading {status_json_path}: {e}")

    return status

    

def get_array_type(
    status_json_path: str | Path,
    logger = logging.getLogger(name=__name__)
) -> str:
    """
    Checks if a previous analysis was successful by reading a status JSON file.

    This function verifies the existence of the specified JSON file and parses it to determine
    if the analysis completed successfully. It looks for the key "analysis_completed_successfully"
    in the JSON and checks if its value is "true" (case-insensitive). If the file does not exist
    or the status is not "true", it returns False.

    Args:
        status_json_path (str | Path): The path to the JSON file containing the analysis status.

    Returns:
        bool: True if the analysis was successful, False otherwise.

    Raises:
        PermissionError: If there is a permission issue reading the file.
    """
    if Path(status_json_path).exists():
        try:
            with open(file=status_json_path, mode="rb") as file:
                status_json = orjson.loads(file.read())
                return status_json.get("array_type", "N/A").lower()

        except PermissionError:
            raise PermissionError(f"Permission denied for reading {status_json_path}.")
        except Exception as e:
            logger.critical(f"Error reading {status_json_path}: {e}")

    return "N/A"