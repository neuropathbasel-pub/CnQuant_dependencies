from collections import defaultdict
def get_available_methylation_classes_and_their_options(
    available_summary_plots: dict[str, dict[tuple[int, int], dict[str, list[str]]]],
):
    """Transforms available summary plots data into a nested structure organized by methylation class options.
    
    This function reorganizes the input data to group methylation classes (annotations) with their
    associated downsizing targets, preprocessing methods, and bin settings.
    
    Args:
        available_summary_plots (dict[str, dict[tuple[int, int], dict[str, list[str]]]]): 
            A nested dictionary where keys are preprocessing methods, values are dicts with bin settings 
            (tuples of (bin_size, min_probes_per_bin)) as keys, and values are dicts with annotations 
            as keys and lists of downsizing targets as values.
    
    Returns:
        defaultdict: A nested defaultdict structure where:
            - Top-level keys are annotations (methylation classes).
            - Next level has "downsized_to" as key.
            - Then downsizing targets as keys.
            - Then preprocessing methods as keys.
            - Values are sets of bin settings (tuples of (bin_size, min_probes_per_bin)).
    
    Notes:
        Uses defaultdict to automatically create nested structures without explicit checks.
    """
    available_methylation_classes_and_their_options = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    )
    for preprocessing_method in available_summary_plots:
        for bin_settings in available_summary_plots[preprocessing_method]:
            bin_size, min_probes_per_bin = bin_settings
            for annotation in available_summary_plots[preprocessing_method][
                bin_settings
            ]:
                for downsizing_target in available_summary_plots[preprocessing_method][
                    bin_settings
                ][annotation]:
                    # No need for if checks—defaultdict handles creation automatically
                    available_methylation_classes_and_their_options[annotation][
                        "downsized_to"
                    ][downsizing_target][preprocessing_method].add(bin_settings)

    return available_methylation_classes_and_their_options