from enum import Enum, unique
from .ArrayType import ArrayType

@unique
class CommonArrayType(Enum):
    """Provides constants lists for the final downsized array type."""
    EPIC_v2_to_HM450K = "EPIC_v2_to_HM450K"
    EPIC_v2_to_MSA48 = "EPIC_v2_to_MSA48"

    @classmethod
    def get_array_types(cls, smallest_array: "CommonArrayType") -> list[ArrayType]:
        """Returns the list of ArrayType instances for the given CommonArrayType enum value."""
        if smallest_array == cls.EPIC_v2_to_HM450K:
            return [
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        elif smallest_array == cls.EPIC_v2_to_MSA48:
            return [
                ArrayType.ILLUMINA_MSA48,
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        else:
            raise ValueError(f"Unknown CommonArrayType value: {smallest_array}")

    @classmethod
    def value_to_key_mapping(cls, array_types: list[ArrayType]) -> dict[str, str]:
        """Returns a dict mapping ArrayType values to their enum names (keys)."""
        return {at.value: at.name for at in array_types}