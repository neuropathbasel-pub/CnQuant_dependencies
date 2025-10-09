from pathlib import Path
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