from pathlib import Path
from typing import Optional, cast

class Missing_idat(Exception):
    """Reports errors related to missing idat files"""
    def __init__(self, message="Missing idat files"):
        self.message = "Missing idat files"
        super().__init__(self.message)

class Unsupported_array_type(Exception):
    """Reports errors related to missing idat files"""
    def __init__(self, array_type: str, message="The array type is not supported"):
        self.message = message
        self.array_type = array_type
        super().__init__(self.message)

class MixedArrayTypesInReferenceData(Exception):
    """Reports errors related to missing idat files"""
    def __init__(self, message="Mixed array types in reference data"):
        self.message = message

        super().__init__(self.message)       

class Failure_to_load_reference_data(Exception):
    """Reports errors related to loading reference data"""
    def __init__(self, error: str):
        self.message = f"Failed to load reference data.\nError: {error}"
        super().__init__(self.message)

class Failure_to_convert_sentrix_id(Exception):
    """Reports errors related to converting idat to 450k format"""
    def __init__(self, sentrix_id: str = "missing sentrix id",  error: str = "missing error"):
        self.message = f"Failed to convert idat pair id: {sentrix_id}.\nError: {error}"
        super().__init__(self.message)

class FileCorruptionError(Exception):
    """Reports errors related to file corruption detected via checksum mismatch"""
    def __init__(self, file_path: str|Path,  error: str = "The stored and computed checksums do not match"):
        self.message = f"File corruption detected for file: {file_path}.\nError: {error}"
        super().__init__(self.message)

class IdatSizeBelowThreshold(Exception):
    """Reports errors related to IDAT file size [MB] below threshold"""
    def __init__(self, sentrix_id: str, red_idat_size: Optional[float] = None, green_idat_size: Optional[float] = None, idat_file_size_threshold: Optional[float] = None, custom_message: Optional[str] = None):
        if custom_message is not None:
            self.message = custom_message
        elif all(parameter is not None for parameter in [red_idat_size, green_idat_size, idat_file_size_threshold]):
            red_size = cast(float, red_idat_size)
            green_size = cast(float, green_idat_size)
            threshold = cast(float, idat_file_size_threshold)
            if red_size < threshold and green_size < threshold:
                self.message = f"Both IDAT file sizes for sentrix ID: {sentrix_id} are below the threshold of {threshold} MB.\nRed IDAT size: {red_size} MB, Green IDAT size: {green_size} MB."
            elif red_size < threshold:
                self.message = f"Red IDAT file size for sentrix ID: {sentrix_id} is below the threshold of {threshold} MB.\nRed IDAT size: {red_size} MB."
            elif green_size < threshold:
                self.message = f"Green IDAT file size for sentrix ID: {sentrix_id} is below the threshold of {threshold} MB.\nGreen IDAT size: {green_size} MB."
            else:
                self.message = f"There is a bug in the IdatSizeBelowThreshold exception. IDAT file sizes for sentrix ID: {sentrix_id} are above the threshold of {threshold} MB.\nRed IDAT size: {red_size} MB, Green IDAT size: {green_size} MB."
        else:
            self.message = "Insufficient information provided to determine IDAT file size status."
        super().__init__(self.message)

class IdatSizeNotEqual(Exception):
    """Reports errors related to IDAT file sizes [MB] not being equal"""
    def __init__(self, sentrix_id: str):
        self.message = f"IDAT file sizes for sentrix ID: {sentrix_id} are not equal."
        super().__init__(self.message)