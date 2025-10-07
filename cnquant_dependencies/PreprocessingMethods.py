from enum import Enum, unique
from typing import Sequence, cast
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
    def members_list(cls) -> Sequence["PreprocessingMethods"]:
        """Returns a sequence of the string values of all CommonArrayType enum members."""
        return cast(Sequence[PreprocessingMethods], [member for member in cls])
    
    @classmethod
    def valid_preprocessing_methods(cls) -> Sequence[str]:
        """Returns a list of array types currently supported by CnQuant."""
        return cast(Sequence[str], [member.value for member in cls])

def get_enum_from_string(value: str) -> PreprocessingMethods | None:
    for name, member in PreprocessingMethods.__members__.items():
        if member.value == value.lower():
            return member
    return None

    