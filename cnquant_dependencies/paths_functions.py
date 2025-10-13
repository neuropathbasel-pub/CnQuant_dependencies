import orjson
import logging
from pathlib import Path
from typing import Any
from cnquant_dependencies.CommonArrayType import CommonArrayType

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

# def load_analysis_status_json(status_json_path: str | Path,  ) -> dict:
   
#     if not Path(status_json_path).exists():
#         return {}
#     try:
#         with open(file=status_json_path, mode="rb") as file:
#             status_json = orjson.loads(file.read())
#             return status_json
#     except PermissionError:
#         raise PermissionError(f"Permission denied for reading {status_json_path}.")
#     except Exception as e:
#         raise Exception(f"An error occurred while reading {status_json_path}: {e}")
    
def load_analysis_status_json(status_json_path: str | Path, logger = logging.getLogger(name=__name__)) -> dict[str, Any]:
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