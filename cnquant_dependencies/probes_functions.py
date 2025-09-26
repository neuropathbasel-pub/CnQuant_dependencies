import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Optional
from .probes import ProbeType, Channel


def probe_info_fn(
    manifest_df: pd.DataFrame,
    probe_type: ProbeType,
    channel: Optional[Channel] = None,
    indices_to_keep: Optional[pd.DataFrame] = None,
):
    """Retrieves information about probes of a specified type and channel.

    Args:
        probe_type (ProbeType): The type of probe (I, II, SnpI, SnpII,
            Control).
        channel (Channel, optional): The color channel (RED or GRN).
            Defaults to None.

    Returns:
        DataFrame: DataFrame containing information about the specified
            probes.

    Raises:
        ValueError: If probe_type is not a valid ProbeType or if channel is
        not a valid Channel.
    """
    if not isinstance(probe_type, ProbeType):
        msg = "probe_type is not a valid ProbeType"
        raise TypeError(msg)

    if channel and not isinstance(channel, Channel):
        msg = "channel not a valid Channel"
        raise TypeError(msg)

    probe_type_mask = manifest_df["Probe_Type"].values == probe_type.value

    if indices_to_keep is not None:
        indices_to_keep_mask = manifest_df["IlmnID"].isin(
            values=indices_to_keep["IlmnID"]
        )
        probe_type_mask = probe_type_mask & indices_to_keep_mask

    if channel is None:
        return manifest_df[probe_type_mask]

    channel_mask = manifest_df["Color_Channel"].values == channel.value

    return manifest_df[probe_type_mask & channel_mask]


def get_methylation_probes(data_frame: pd.DataFrame) -> NDArray[np.str_]:
    """Extract methylation probe IDs from a DataFrame.

    Args:
        data_frame (pd.DataFrame): DataFrame containing probe information with an 'IlmnID' column.

    Returns:
        NDArray[np.str_]: Array of IlmnID values for methylation probes.

    Raises:
        KeyError: If 'IlmnID' column is missing from data_frame.
    """
    if "IlmnID" not in data_frame.columns:
        raise KeyError("DataFrame must contain 'IlmnID' column")

    type_1 = probe_info_fn(manifest_df=data_frame, probe_type=ProbeType.ONE)
    type_2 = probe_info_fn(manifest_df=data_frame, probe_type=ProbeType.TWO)
    idx = np.sort(
        np.concatenate(
            [
                type_1.IlmnID.index,
                type_2.IlmnID.index,
            ]
        )
    )
    methylation_probes = np.asarray(data_frame.loc[idx, "IlmnID"].values, dtype=np.str_)
    return methylation_probes
