from enum import Enum, unique
from cnquant_dependencies.ArrayType import ArrayType
from typing import Sequence, cast, Union

def map_array_types_to_human_readable_name(array_type: ArrayType) -> str:
    array_names = {
        ArrayType.ILLUMINA_450K: "HM450K",
        ArrayType.ILLUMINA_EPIC: "EPIC v1",
        ArrayType.ILLUMINA_EPIC_V2: "EPIC v2",
        ArrayType.ILLUMINA_MSA48: "MSA-48",
        ArrayType.ILLUMINA_27K: "27K",
        ArrayType.ILLUMINA_MOUSE: "Mouse",
        ArrayType.UNKNOWN: "Unknown",
    }
    if array_type not in array_names:
        raise ValueError(f"Unknown ArrayType value: {array_type}")
    return array_names[array_type]



# TODO: Make the enum more understandable
@unique
class CommonArrayType(Enum):
    """Provides constants lists for the final downsized array type."""
    NO_DOWNSIZING = "NO_DOWNSIZING"
    EPIC_v2_EPIC_v1_to_HM450K = "EPIC_v2_EPIC_v1_to_HM450K"
    EPIC_v2_EPIC_v1_HM450_to_MSA48 = "EPIC_v2_EPIC_v1_HM450_to_MSA48"

    @classmethod
    def get_array_types(cls, convert_from_to: "CommonArrayType", verbose=False) -> Sequence[Union[str,ArrayType]]:
        """Returns the list of ArrayType instances for the given CommonArrayType enum value."""
        EPIC_v2_EPIC_v1_to_HM450K_array_types: list[ArrayType] = [
                ArrayType.ILLUMINA_450K,
                ArrayType.ILLUMINA_EPIC,
                ArrayType.ILLUMINA_EPIC_V2,
            ]
        EPIC_v2_EPIC_v1_HM450_to_MSA48_array_types: list[ArrayType] = [
                    ArrayType.ILLUMINA_MSA48,
                    ArrayType.ILLUMINA_450K,
                    ArrayType.ILLUMINA_EPIC,
                    ArrayType.ILLUMINA_EPIC_V2,
                ]

        if convert_from_to == cls.EPIC_v2_EPIC_v1_to_HM450K:
            
            if verbose:
                return [map_array_types_to_human_readable_name(array_type_name) for array_type_name in EPIC_v2_EPIC_v1_to_HM450K_array_types]
            else:
                return EPIC_v2_EPIC_v1_to_HM450K_array_types
            
        elif convert_from_to == cls.EPIC_v2_EPIC_v1_HM450_to_MSA48:
            if verbose:
                return[map_array_types_to_human_readable_name(array_type_name) for array_type_name in EPIC_v2_EPIC_v1_HM450_to_MSA48_array_types]
            else:
                return EPIC_v2_EPIC_v1_HM450_to_MSA48_array_types
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
    def is_convertible_to(cls, array_type: ArrayType, convert_from_to: "CommonArrayType") -> bool:
        """Returns the list of CommonArrayType enum values that allow conversion from the given ArrayType."""
        if array_type not in ArrayType.valid_array_types():
            raise ValueError(f"Unknown ArrayType value: {array_type}")
        
        if (array_type in cls.get_array_types(convert_from_to=cls.EPIC_v2_EPIC_v1_to_HM450K) and convert_from_to == cls.EPIC_v2_EPIC_v1_to_HM450K):
            return True
        elif array_type == ArrayType.ILLUMINA_MSA48 and convert_from_to == cls.EPIC_v2_EPIC_v1_HM450_to_MSA48:
            return True
        else:
            return False
        

    @classmethod
    def value_to_key_mapping(cls, common_array_types: list["CommonArrayType"]) -> dict[str, str]:
        """Returns a dict mapping ArrayType values to their enum names (keys)."""
        return {at.value: at.name for at in common_array_types}
    
    @classmethod
    def members_list(cls) -> Sequence[str]:
        """Returns a sequence of the string values of all CommonArrayType enum members."""
        return cast(Sequence[str], [member.value for member in cls])

    @classmethod
    def get_member_from_string(cls, value: str) -> "CommonArrayType":
        f"""Returns the {cls.__name__} enum member corresponding to the given value string.
        
        Args:
            value (str): The string value of the enum member (e.g., "NO_DOWNSIZING").
            
        Returns:
            {cls.__name__}: The matching enum member.
            
        Raises:
            ValueError: If no enum member matches the provided value.
        """
        try:
            return cls(value)
        except ValueError:
            try:
                return getattr(cls, value.upper())  # Fallback to by name
            except AttributeError:
                valid_values = [member.value for member in cls]
                valid_names = [member.name for member in cls]
                raise ValueError(f"Invalid value or name '{value}' for {cls.__name__}. Valid values: {valid_values}. Valid names: {valid_names}")
            except ValueError:
                raise ValueError(f"Invalid value '{value}' for {cls.__name__}. Valid values are: {[member.value for member in cls]}")

    @classmethod
    def available_downsizing_targets(cls, array_type: str) -> "list[CommonArrayType]":

        try:
            array_type_member = ArrayType.get_member_from_string(array_type)
        except ValueError as e:
            raise ValueError(f"Invalid ArrayType value '{array_type}'. Valid values are: {[member.value for member in ArrayType]}") from e
        
        return cls.may_be_converted_to(array_type=array_type_member)


if __name__ == "__main__":
    # print(CommonArrayType.get_array_types(convert_from_to=CommonArrayType.EPIC_v2_EPIC_v1_to_HM450K, verbose=True))  # List of ArrayType
    # print(', '.join(CommonArrayType.members_list()))
    # print(CommonArrayType.get_member_from_string(value="EPIC_v2_EPIC_v1_HM450_to_MSA48"))
    print(CommonArrayType.available_downsizing_targets("450k"))
    # print(CommonArrayType.value_to_key_mapping(CommonArrayType.members_list()))
    # print(CommonArrayType.value_to_key_mapping(CommonArrayType.EPIC_v2_EPIC_v1_to_HM450K))
    # print(CommonArrayType.get_array_types(CommonArrayType.EPIC_v2_EPIC_v1_HM450_to_MSA48))