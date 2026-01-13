import logging
from pathlib import Path
from typing import Optional, Protocol

import polars as pl


class AnnotatedCasesLoaderProtocol(Protocol):
    """
    Protocol for annotated cases loader to enable dependency injection.
    """

    def load_annotated_cases(
        self,
    ) -> pl.DataFrame: ...
    def get_methylation_classes_selection(
        self,
        chosen_methylation_class: Optional[str] = None,
    ) -> list[str]: ...

    def get_annotated_sentrix_ids(
        self,
        methylation_classes_selection: list[str],
    ) -> list[str]: ...


class AnnotatedCasesLoader(AnnotatedCasesLoaderProtocol):
    """
    A class for loading and processing annotated cases from a CSV file.

    This class handles loading annotation data, filtering out blacklisted methylation classes,
    and providing methods to retrieve methylation classes and associated Sentrix IDs.
    """

    def __init__(
        self,
        annotation_file_path: Path,
        sentrix_ids_column_in_annotation_file: str,
        methylation_classes_column_in_annotation_file: str,
        blacklisted_methylation_classes: list[str],
        logger: logging.Logger = logging.getLogger(name=__name__),
    ):
        """
        Initializes the AnnotatedCasesLoader.

        Args:
            annotation_file_path (Path): Path to the annotation CSV file.
            sentrix_ids_column_in_annotation_file (str): Name of the column containing Sentrix IDs.
            methylation_classes_column_in_annotation_file (str): Name of the column containing methylation classes.
            blacklisted_methylation_classes (list[str]): List of methylation classes to exclude.
            logger (logging.Logger, optional): Logger instance for logging messages. Defaults to a logger named after the module.
        """
        self.logger: logging.Logger = logger
        self.annotation_file_path: Path = annotation_file_path
        self.sentrix_ids_column_in_annotation_file: str = (
            sentrix_ids_column_in_annotation_file
        )
        self.methylation_classes_column_in_annotation_file: str = (
            methylation_classes_column_in_annotation_file
        )
        self.blacklisted_methylation_classes: list[str] = (
            blacklisted_methylation_classes
        )
        self.annotation = self.load_annotated_cases()

    def load_annotated_cases(self) -> pl.DataFrame:
        """
        Loads and processes the annotated cases from the CSV file.

        Filters out rows with blacklisted methylation classes, drops rows with NaN values,
        and replaces "/" with "_" in the methylation classes column.

        Returns:
            pl.DataFrame: Processed Polars DataFrame containing the annotation data.
        """
        return (
            pl.read_csv(source=self.annotation_file_path)
            .filter(
                ~pl.col(name=self.methylation_classes_column_in_annotation_file).is_in(
                    other=self.blacklisted_methylation_classes
                )
            )
            .drop_nans()
            .with_columns(
                pl.col(
                    name=self.methylation_classes_column_in_annotation_file
                ).str.replace(pattern="/", value="_")
            )
        )

    def update_annotated_cases(self) -> None:
        """
        Reloads and processes the annotated cases from the CSV file.
        """
        self.annotation = self.load_annotated_cases()

    def get_methylation_classes_selection(
        self, chosen_methylation_class: Optional[str] = None
    ) -> list[str]:
        """
        Retrieves the selection of methylation classes based on the chosen class or all available classes.

        Args:
            chosen_methylation_class (Optional[str], optional): Specific methylation class to select. If None, returns all available classes. Defaults to None.

        Returns:
            list[str]: List of selected methylation classes.

        Raises:
            ValueError: If the chosen methylation class is not present in the annotation file.
        """
        methylation_classes: list[str] = (
            self.annotation.select(self.methylation_classes_column_in_annotation_file)
            .unique()
            .to_series()
            .to_list()
        )
        if chosen_methylation_class is None:
            methylation_classes_selection: list[str] = methylation_classes

        else:
            if chosen_methylation_class in methylation_classes:
                methylation_classes_selection = [chosen_methylation_class]
            else:
                self.logger.error(
                    msg=f"The chosen methylation class '{chosen_methylation_class}' is not present in the annotation file. Available classes are: {methylation_classes}. No plots will be generated."
                )
                raise ValueError(
                    f"Invalid methylation class: {chosen_methylation_class}"
                )
        return methylation_classes_selection

    def get_annotated_sentrix_ids(
        self,
        methylation_classes_selection: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Retrieves the unique Sentrix IDs associated with the selected methylation classes.

        Args:
            methylation_classes_selection (list[str]): List of methylation classes to filter by.

        Returns:
            list[str]: List of unique Sentrix IDs for the selected methylation classes.
        """
        if methylation_classes_selection is None:
            return (
                self.annotation.select(self.sentrix_ids_column_in_annotation_file)
                .unique()
                .to_series()
                .to_list()
            )

        annotated_sentrix_ids: list[str] = (
            self.annotation.filter(
                pl.col(name=self.methylation_classes_column_in_annotation_file).is_in(
                    other=methylation_classes_selection
                )
            )
            .select(self.sentrix_ids_column_in_annotation_file)
            .unique()
            .to_series()
            .to_list()
        )
        return annotated_sentrix_ids
