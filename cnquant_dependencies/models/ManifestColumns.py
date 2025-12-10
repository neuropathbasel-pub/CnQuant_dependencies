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