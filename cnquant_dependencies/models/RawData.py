from functools import reduce
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from cnquant_dependencies.enums.ArrayType import ArrayType
from cnquant_dependencies.models.IdatParser import IdatParser
from cnquant_dependencies.custom_errors import Unsupported_array_type
from cnquant_dependencies.paths_functions import idat_basepaths, idat_paths_from_basenames

ENDING_GRN = "_Grn.idat"
ENDING_RED = "_Red.idat"
ENDING_GZ = ".gz"
ENDING_SUFFIXES = ("_Grn.idat", "_Red.idat", "_Grn.idat.gz", "_Red.idat.gz")


class RawData:
    """Represents raw intensity data from IDAT files for Illumina arrays.

    Parses IDAT files to extract green and red channel intensity data, storing them as arrays
    and dataframes. Optionally filters data by indices.

    Attributes:
        sentrix_ids (list[str]): Names of IDAT files (without extensions).
        array_type (ArrayType): Type of Illumina array.
        ids (np.ndarray): Array of probe IDs.
        _grn (np.ndarray): Green channel intensity arrays (uint16).
        _red (np.ndarray): Red channel intensity arrays (uint16).
        _grn_df (pd.DataFrame): Green channel intensities as dataframe.
        _red_df (pd.DataFrame): Red channel intensities as dataframe.
        grn (pd.DataFrame): Alias for _grn_df.
        red (pd.DataFrame): Alias for _red_df.
        methylated (None): Placeholder for methylated data.
        unmethylated (None): Placeholder for unmethylated data.

    Methods:
        keep_only_given_indices(indices): Filter data to keep only specified indices.
        __repr__(): String representation of the object.

    Args:
        basenames (list): List of basepaths to IDAT files (with or without .idat/.gz extension).
    """

    def __init__(
        self,
        basenames,
    ):
        _basenames: list[Path] = idat_basepaths(files=basenames)

        self.sentrix_ids: list[str] = [path.name.replace(ENDING_GZ, "") for path in _basenames]

        grn_idat_files, red_idat_files = idat_paths_from_basenames(basenames=_basenames)

        grn_idat: list[IdatParser] = [
            IdatParser(file_path=str(object=filepath), intensity_only=True)
            for filepath in grn_idat_files
        ]
        red_idat: list[IdatParser] = [
            IdatParser(file_path=str(object=filepath), intensity_only=True)
            for filepath in red_idat_files
        ]

        array_types: list[ArrayType] = [
            ArrayType.from_probe_count(probe_count=len(idat.illumina_ids))
            for idat in grn_idat + red_idat
        ]

        if len(set(array_types)) != 1:
            msg = "Array types must all be the same."
            raise ValueError(msg)
        self.array_type: ArrayType = array_types[0]

        if self.array_type not in ArrayType.valid_array_types():
            raise Unsupported_array_type(
                message=f"Array type of '{self.array_type}' by Sentrix ID {', '.join(self.sentrix_ids)} is not in the following supported array types: {', '.join([array_type.value for array_type in ArrayType.valid_array_types()])}",
                array_type=self.array_type.value,
            )

        all_illumina_ids: list = [idat.illumina_ids for idat in grn_idat + red_idat]

        if all(np.array_equal(all_illumina_ids[0], arr) for arr in all_illumina_ids):
            self.ids = all_illumina_ids[0]
            self._grn: np.ndarray = np.array(object=[idat.probe_means for idat in grn_idat])
            self._red: np.ndarray = np.array(object=[idat.probe_means for idat in red_idat])
        else:
            self.ids = reduce(np.intersect1d, [idat.illumina_ids for idat in grn_idat])
            self._grn: np.ndarray = np.array(
                object=[
                    idat.probe_means[
                        np.isin(
                            element=idat.illumina_ids,
                            test_elements=self.ids,
                            assume_unique=True,
                        )
                    ]
                    for idat in grn_idat
                ]
            )
            self._red: np.ndarray = np.array(
                object=[
                    idat.probe_means[
                        np.isin(
                            element=idat.illumina_ids,
                            test_elements=self.ids,
                            assume_unique=True,
                        )
                    ]
                    for idat in red_idat
                ]
            )

        self._grn_df: pd.DataFrame = pd.DataFrame(
            data=self._grn.T, index=self.ids, columns=self.sentrix_ids, dtype="int32"
        )

        self._red_df: pd.DataFrame = pd.DataFrame(
            data=self._red.T, index=self.ids, columns=self.sentrix_ids, dtype="int32"
        )
        self.grn: pd.DataFrame = self._grn_df
        self.red: pd.DataFrame = self._red_df
        self.methylated = None
        self.unmethylated = None

        assert (
            self.grn.shape[0]
            == self.red.shape[0]
            == len(self.ids)
            == len(self._grn[0])
            == len(self._red[0])
        ), "RawData class outputs incorrect dimensions"

    def keep_only_given_indices(self, indices: Optional[pd.Index]):
        """Filter dataframes and arrays to keep only specified indices.

        Args:
            indices: Pandas Index or None. If provided, filters rows in `_grn_df`, `_red_df`, `ids`,
                    and corresponding arrays in `_grn` and `_red` to match given indices.

        Returns:
            Self: The modified object with filtered data.
        """
        if indices is not None:
            self._grn_df = self._grn_df.iloc[indices, :]
            self._red_df = self._red_df.iloc[indices, :]
            self.ids = self.ids[indices]
            self._grn = np.array(
                object=[array[indices] for array in self._grn], dtype=np.uint16
            )
            self._red = np.array(
                object=[array[indices] for array in self._red], dtype=np.uint16
            )
        return self

    def __repr__(self):
        title: str = "RawData():"
        lines: list[str] = [
            title + "\n" + "*" * len(title),
            f"array_type: {self.array_type}",
            f"probes:\n{self.sentrix_ids}",
            f"ids:\n{self.ids}",
            f"_grn:\n{self._grn}",
            f"_red:\n{self._red}",
            f"grn:\n{self.grn}",
            f"red:\n{self.red}",
        ]
        return "\n\n".join(lines)
