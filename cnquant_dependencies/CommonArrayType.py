from enum import Enum, unique
from .ArrayType import ArrayType
from typing import Sequence, cast
# TODO: Make the enum more understandable
@unique
class CommonArrayType(Enum):
    """Provides constants lists for the final downsized array type."""
    EPIC_v2_to_HM450K = "EPIC_v2_to_HM450K"
    EPIC_v2_to_MSA48 = "EPIC_v2_to_MSA48"

    @classmethod
    def get_array_types(cls, convert_from_to: "CommonArrayType") -> list[ArrayType]:
        """Returns the list of ArrayType instances for the given CommonArrayType enum value."""
        if convert_from_to == cls.EPIC_v2_to_HM450K:
            return [
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        elif convert_from_to == cls.EPIC_v2_to_MSA48:
            return [
                ArrayType.ILLUMINA_MSA48,
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        else:
            raise ValueError(f"Unknown CommonArrayType value: {convert_from_to}")

    @classmethod
    def value_to_key_mapping(cls, common_array_types: list["CommonArrayType"]) -> dict[str, str]:
        """Returns a dict mapping ArrayType values to their enum names (keys)."""
        return {at.value: at.name for at in common_array_types}
    
    @classmethod
    def members_list(cls) -> Sequence["CommonArrayType"]:
        """Returns a list of all CommonArrayType enum members."""
        return cast(Sequence["CommonArrayType"], list(cls._member_map_.values()))

