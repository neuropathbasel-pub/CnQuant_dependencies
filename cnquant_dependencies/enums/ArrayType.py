"""Contains the ArrayType used to represent different Illumina array types."""

from enum import Enum, unique
from pathlib import Path
from typing import cast, Sequence
from cnquant_dependencies.models.IdatParser import IdatParser


def _find_valid_path(path):
    """Tries to find a valid IDAT file associated with the given path."""
    base_path = Path(path)
    if base_path.exists():
        return base_path
    grn_path = Path(str(base_path) + "_Grn.idat")
    if grn_path.exists():
        return grn_path
    grn_gz_path = Path(str(base_path) + "_Grn.idat.gz")
    if grn_gz_path.exists():
        return grn_gz_path
    msg = f"No valid file found for path: {path}"
    raise ValueError(msg)


@unique
class ArrayType(Enum):
    """Provides constants for the different Illumina array types.

    Enum representing different Illumina array types with method to infer
    type from probe count.
    """

    ILLUMINA_27K = "27k"
    ILLUMINA_450K = "450k"
    ILLUMINA_EPIC = "epic_v1"
    ILLUMINA_EPIC_V2 = "epic_v2"
    ILLUMINA_MSA48 = "msa48"
    ILLUMINA_MOUSE = "mouse"
    UNKNOWN = "unknown"

    @classmethod
    def valid_array_types(cls) -> list["ArrayType"]:
        """Returns a list of array types currently supported by CnQuant."""
        return [
            ArrayType.ILLUMINA_450K,
            ArrayType.ILLUMINA_EPIC,
            ArrayType.ILLUMINA_EPIC_V2,
            ArrayType.ILLUMINA_MSA48,
        ]

    def __str__(self):
        return self.value

    @classmethod
    def from_probe_count(cls, probe_count):
        """Infers array type based on the number of probes in an idat file."""
        if 622000 <= probe_count <= 623000:
            return cls.ILLUMINA_450K

        if 1050000 <= probe_count <= 1053000:
            return cls.ILLUMINA_EPIC

        if 1032000 <= probe_count <= 1033000:
            return cls.ILLUMINA_EPIC

        if 1100000 <= probe_count <= 1108000:
            return cls.ILLUMINA_EPIC_V2

        if 384400 <= probe_count <= 384600:
            return cls.ILLUMINA_MSA48

        if 55200 <= probe_count <= 55400:
            return cls.ILLUMINA_27K

        if 315000 <= probe_count <= 362000:
            return cls.ILLUMINA_MOUSE

        return cls.UNKNOWN

    @classmethod
    def from_idat(cls, path):
        """Infers array type from idat_file."""
        valid_path = _find_valid_path(path=path)
        probe_count = IdatParser(file_path=valid_path, array_type_only=True).n_snps_read
        return ArrayType.from_probe_count(probe_count=probe_count)
    
    @classmethod
    def value_to_key_mapping(cls, array_types: list["ArrayType"]) -> dict[str, str]:
        f"""Returns a dict mapping {cls.__name__} values to their enum names (keys)."""
        return {at.value: at.name for at in array_types}
    
    @classmethod
    def members_list(cls) -> Sequence["ArrayType"]:
        """Returns a list of all CommonArrayType enum members."""
        return cast(Sequence["ArrayType"], list(cls._member_map_.values()))
    
    
    @classmethod
    def get_member_from_string(cls, value: str) -> "ArrayType":
        f"""Returns the {cls.__name__} enum member corresponding to the given value string.
        
        Args:
            value (str): The string value of the enum member (e.g., "450k").
            
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
    def make_pretty_array_type_string(cls, array_type: "ArrayType") -> str:
        """Converts an ArrayType enum member to a more human-readable string."""
        pretty_mappings = {
            cls.ILLUMINA_27K : "HumanMethylation27",
            cls.ILLUMINA_450K : "Infinium HumanMethylation450K",
            cls.ILLUMINA_EPIC : "Infinium MethylationEPIC v1.0",
            cls.ILLUMINA_EPIC_V2 : "Infinium MethylationEPIC v2.0",
            cls.ILLUMINA_MSA48 : "Infinium Methylation Screening Array-48",
        }
        return pretty_mappings.get(array_type, "Unknown Array Type")

if __name__ == "__main__":
    print(ArrayType.__name__)