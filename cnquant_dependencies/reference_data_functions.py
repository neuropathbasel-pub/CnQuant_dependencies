import polars as pl
from cnquant_dependencies.enums.ArrayType import ArrayType
from pathlib import Path
import logging


def load_reference_data_annotation(
    csv_path: str | Path,
    logger: logging.Logger = logging.getLogger(__name__),
    minimum_number_of_reference_samples: int = 5,
) -> dict[ArrayType, list[str]]:
    """
    Loads reference data annotation from a CSV file and organizes Sentrix IDs by array type.

    Args:
        csv_path (str | Path): Path to the CSV file containing reference data annotations.

    Returns:
        dict[ArrayType, list[str]]: A dictionary mapping each ArrayType to a list of Sentrix IDs
        corresponding to that array type.

    The CSV file is expected to have at least the columns 'array_type' and 'Sentrix_id'.
    Recognized array types include '450k', 'epic_v1', 'epic_v2', and 'msa48'.
    """
    reference_dataframe = pl.read_csv(source=csv_path)

    reference_450k_reference_samples = (
        reference_dataframe.filter(
            pl.col("array_type") == ArrayType.ILLUMINA_450K.value
        )
        .select("Sentrix_id")
        .to_series()
        .to_list()
    )
    EPIC_v1_reference_samples = (
        reference_dataframe.filter(
            pl.col("array_type") == ArrayType.ILLUMINA_EPIC.value
        )
        .select("Sentrix_id")
        .to_series()
        .to_list()
    )
    EPIC_v2_reference_samples = (
        reference_dataframe.filter(
            pl.col("array_type") == ArrayType.ILLUMINA_EPIC_V2.value
        )
        .select("Sentrix_id")
        .to_series()
        .to_list()
    )
    msa48_reference_samples = (
        reference_dataframe.filter(
            pl.col("array_type") == ArrayType.ILLUMINA_MSA48.value
        )
        .select("Sentrix_id")
        .to_series()
        .to_list()
    )

    reference_data_sentrix_ids_and_types: dict[ArrayType, list[str]] = {
        ArrayType.ILLUMINA_450K: reference_450k_reference_samples,
        ArrayType.ILLUMINA_EPIC: EPIC_v1_reference_samples,
        ArrayType.ILLUMINA_EPIC_V2: EPIC_v2_reference_samples,
        ArrayType.ILLUMINA_MSA48: msa48_reference_samples,
    }

    for key in reference_data_sentrix_ids_and_types.keys():
        if (
            len(reference_data_sentrix_ids_and_types[key])
            < minimum_number_of_reference_samples
        ):
            logger.warning(
                msg=f"Only {len(reference_data_sentrix_ids_and_types[key])} reference samples found for {key.value} array type. "
                f"At least {minimum_number_of_reference_samples} are recommended for reliable analysis."
            )

    return reference_data_sentrix_ids_and_types
