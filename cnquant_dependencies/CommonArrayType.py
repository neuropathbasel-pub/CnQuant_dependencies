from enum import Enum, unique
from cnquant_dependencies.ArrayType import ArrayType
from typing import Sequence, cast
# TODO: Make the enum more understandable
@unique
class CommonArrayType(Enum):
    """Provides constants lists for the final downsized array type."""
    NO_DOWNSIZING = "NO_DOWNSIZING"
    EPIC_v2_EPIC_v1_to_HM450K = "EPIC_v2_EPIC_v1_to_HM450K"
    EPIC_v2_EPIC_v1_HM450_to_MSA48 = "EPIC_v2_EPIC_v1_HM450_to_MSA48"

    @classmethod
    def get_array_types(cls, convert_from_to: "CommonArrayType") -> list[ArrayType]:
        """Returns the list of ArrayType instances for the given CommonArrayType enum value."""
        if convert_from_to == cls.EPIC_v2_EPIC_v1_to_HM450K:
            return [
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        elif convert_from_to == cls.EPIC_v2_EPIC_v1_HM450_to_MSA48:
            return [
                ArrayType.ILLUMINA_MSA48,
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        else:
            raise ValueError(f"Unknown CommonArrayType value: {convert_from_to}")
        
    @classmethod
    def may_be_converted_to(cls, array_type: ArrayType) -> list["CommonArrayType"]:
        """Returns the list of CommonArrayType enum values that allow conversion from the given ArrayType."""
        if array_type not in ArrayType.valid_array_types():
            raise ValueError(f"Unknown ArrayType value: {array_type}")
        
        if array_type in cls.get_array_types(cls.EPIC_v2_EPIC_v1_to_HM450K):
            return [
                cls.EPIC_v2_EPIC_v1_to_HM450K,
            ]
        elif array_type == ArrayType.ILLUMINA_MSA48:
            return [
                cls.EPIC_v2_EPIC_v1_HM450_to_MSA48,
            ]
        else:
            raise ValueError(f"No conversion available for ArrayType value: {array_type}")
        

    @classmethod
    def value_to_key_mapping(cls, common_array_types: list["CommonArrayType"]) -> dict[str, str]:
        """Returns a dict mapping ArrayType values to their enum names (keys)."""
        return {at.value: at.name for at in common_array_types}
    
    @classmethod
    def members_list(cls) -> Sequence["CommonArrayType"]:
        """Returns a list of all CommonArrayType enum members."""
        return cast(Sequence["CommonArrayType"], list(cls._member_map_.values()))


if __name__ == "__main__":
    print(CommonArrayType.value_to_key_mapping([CommonArrayType.EPIC_v2_EPIC_v1_HM450_to_MSA48]))
    # print(CommonArrayType.value_to_key_mapping(CommonArrayType.members_list()))
    # print(CommonArrayType.value_to_key_mapping(CommonArrayType.EPIC_v2_EPIC_v1_to_HM450K))
    # print(CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_EPIC_v1_HM450_to_MSA48))