from pathlib import Path
from cnquant_dependencies.enums.ArrayType import ArrayType

def check_for_missing_manifest_parquet_files(manifest_files_and_names: dict[ArrayType, dict[str, str | Path]]) -> list[ArrayType]:
    """
    Check for array types that are missing manifest-related files.

    This function identifies Illumina array types that do not have all required
    manifest files available. It checks for the existence of four types of files
    for each valid array type: the raw Illumina manifest file, the raw Parquet
    manifest, the probes Parquet table, and the controls Parquet table.

    An array type is considered missing if any of these files do not exist in
    the paths specified in the configuration.

    Returns:
        list[ArrayType]: A list of ArrayType enums for which at least one
            manifest-related file is missing. If all files are present for all
            array types, an empty list is returned.

    Raises:
        KeyError: If a required key is missing from config.MANIFEST_FILES_AND_NAMES
            for any array type.
    """
    valid_array_types: list[ArrayType] = ArrayType.valid_array_types()
    
    available_illumina_manifest_files: set[ArrayType] = set([
        array_type for array_type in valid_array_types 
        if Path(manifest_files_and_names[array_type]["file_path"]).exists()
    ])
    available_raw_parquet_manifests: set[ArrayType] = set([
        array_type for array_type in valid_array_types 
        if Path(manifest_files_and_names[array_type]["raw_manifest_parquet_path"]).exists()
    ])
    available_probes_tables: set[ArrayType] = set([
        array_type for array_type in valid_array_types 
        if Path(manifest_files_and_names[array_type]["manifest_probes_parquet_path"]).exists()
    ])
    available_controls_tables: set[ArrayType] = set([
        array_type for array_type in valid_array_types 
        if Path(manifest_files_and_names[array_type]["manifest_controls_parquet_path"]).exists()
    ])
    
    # Compute the intersection of all sets (array types available in all categories)
    common_available = (
        available_illumina_manifest_files 
        & available_raw_parquet_manifests 
        & available_probes_tables 
        & available_controls_tables
    )
    
    # Missing array types are those in valid_array_types but not in the intersection
    missing_manifest_parquet_files_for_array_types = [
        array_type for array_type in valid_array_types 
        if array_type not in common_available
    ]
    
    return missing_manifest_parquet_files_for_array_types