def make_bin_settings_string(bin_size: str|int, min_probes_per_bin: str|int) -> str:
    """Creates a formatted string representing bin settings for bin size and minimum probes per bin.
    
    Args:
        bin_size (str | int): The size of the bin, as a string or integer.
        min_probes_per_bin (str | int): The minimum number of probes per bin, as a string or integer.
    
    Returns:
        str: A formatted string in the form 'bin_size_{bin_size}_min_probes_per_bin_{min_probes_per_bin}'.
    
    Raises:
        TypeError: If bin_size or min_probes_per_bin is not a string or integer.
    """
    if not isinstance(bin_size, (str, int)):
        raise TypeError("bin_size must be a string or an integer")
    if not isinstance(min_probes_per_bin, (str, int)):
        raise TypeError("min_probes_per_bin must be a string or an integer")
    return f"bin_size_{bin_size}_min_probes_per_bin_{min_probes_per_bin}"