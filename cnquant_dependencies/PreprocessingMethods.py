from enum import Enum, unique
from typing import Sequence, cast, Union
@unique
class PreprocessingMethods(Enum):
    "Enum class holding all acceptable preprocessing methods for CnQuant"
    ILLUMINA = "illumina"
    NOOB = "noob"
    SWAN = "swan"
    RAW = "raw"

    @classmethod
    def list(cls):
        return list(cls)
    
    @classmethod
    def get_enum_from_string(cls, value: str) -> Union["PreprocessingMethods", None]:
        for name, member in cls.__members__.items():
            if member.value == value.lower():
                return member
        return None
    
    @classmethod
    def members_list(cls) -> Sequence[str]:
        """Returns a sequence of the PreprocessingMethods enum members."""
        return cast(Sequence[str], [member.value for member in cls])
    
    @classmethod
    def valid_preprocessing_methods(cls) -> Sequence["PreprocessingMethods"]:
        """Returns a list of array types currently supported by CnQuant."""
        return cast(Sequence[PreprocessingMethods], [member for member in cls])
    
    @classmethod
    def get_member_from_string(cls, value: str) -> "PreprocessingMethods":
        """Returns the PreprocessingMethods enum member corresponding to the given value string.
        
        Args:
            value (str): The string value of the enum member
            
        Returns:
            CommonArrayType: The matching enum member.
            
        Raises:
            ValueError: If no enum member matches the provided value.
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid value '{value}' for PreprocessingMethods. Valid values are: {[member.value for member in cls]}")

def get_enum_from_string(value: str) -> PreprocessingMethods | None:
    for name, member in PreprocessingMethods.__members__.items():
        if member.value == value.lower():
            return member
    return None

    