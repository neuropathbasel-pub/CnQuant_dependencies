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