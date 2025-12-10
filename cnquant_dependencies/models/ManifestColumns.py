import pandas as pd

PROBES_COLUMNS: list[str] = [
    "IlmnID",
    "Name",
    "AddressA_ID",
    "AddressB_ID",
    "Infinium_Design_Type",
    "Color_Channel",
    "CHR",
    "Chr",
    "Chromosome",
    "MAPINFO",
    "AlleleA_ProbeSeq",
    "AlleleB_ProbeSeq",
    "Forward_Sequence",
]


CONTROL_COLUMNS: tuple[str, str, str, str] = (
    "Address_ID",
    "Control_Type",
    "Color",
    "Extended_Type",
)
NONE: int = -1

def clean_gene_names(value):
    if pd.isna(value):
        return value  # Keep NaN as is
    # Split by ";", remove duplicates with set, join back
    return ";".join(set(value.split(";")))


valid_manifest_chromosomes: list[str] = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "X",
    "Y",
]