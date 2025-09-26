from enum import Enum, unique

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

def get_enum_from_string(value: str) -> PreprocessingMethods | None:
    for name, member in PreprocessingMethods.__members__.items():
        if member.value == value.lower():
            return member
    return None