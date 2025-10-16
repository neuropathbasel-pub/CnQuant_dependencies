import pandas as pd
import numpy as np
chromosome_data = {
    "name": [
        "chr1",
        "chr2",
        "chr3",
        "chr4",
        "chr5",
        "chr6",
        "chr7",
        "chr8",
        "chr9",
        "chr10",
        "chr11",
        "chr12",
        "chr13",
        "chr14",
        "chr15",
        "chr16",
        "chr17",
        "chr18",
        "chr19",
        "chr20",
        "chr21",
        "chr22",
        "chrX",
        "chrY",
    ],
    "len": [
        249250621,
        243199373,
        198022430,
        191154276,
        180915260,
        171115067,
        159138663,
        146364022,
        141213431,
        135534747,
        135006516,
        133851895,
        115169878,
        107349540,
        102531392,
        90354753,
        81195210,
        78077248,
        59128983,
        63025520,
        48129895,
        51304566,
        155270560,
        59373566,
    ],
    "centromere_start": [
        121535434,
        92326171,
        90504854,
        49660117,
        46405641,
        58830166,
        58054331,
        43838887,
        47367679,
        39254935,
        51644205,
        34856694,
        16000000,
        16000000,
        17000000,
        35335801,
        22263006,
        15460898,
        24681782,
        26369569,
        11288129,
        13000000,
        58632012,
        10104553,
    ],
    "centromere_end": [
        124535434,
        95326171,
        93504854,
        52660117,
        49405641,
        61830166,
        61054331,
        46838887,
        50367679,
        42254935,
        54644205,
        37856694,
        19000000,
        19000000,
        20000000,
        38335801,
        25263006,
        18460898,
        27681782,
        29369569,
        14288129,
        16000000,
        61632012,
        13104553,
    ],
}

class Genome:
    """Data container for reference genome data.

    Attributes:
        chrom: DataFrame with chromosome data (len, centromere_start, centromere_end, offset, center, centromere_offset).
        length: Total genome length.

    Methods:
        __iter__: Enables iteration over chromosomes.
        __len__: Returns total genome length.
        __str__: Provides string overview for debugging.
        __repr__: Returns string representation.
    """

    def __init__(self):
        """Initialize genome with chromosome data, offsets, centers, and total length."""
        self.chrom = pd.DataFrame(data=chromosome_data)
        self.chrom["offset"] = [0] + np.cumsum(a=self.chrom["len"]).tolist()[:-1]
        self.chrom["center"] = self.chrom["offset"] + self.chrom["len"] // 2
        self.chrom["centromere_offset"] = (
            self.chrom["offset"]
            + (self.chrom["centromere_start"] + self.chrom["centromere_end"]) // 2
        )
        self.length = self.chrom["offset"].iloc[-1] + self.chrom["len"].iloc[-1]

    def __iter__(self):
        """Enables looping over chromosomes."""
        return self.chrom.itertuples()

    def __len__(self):
        return self.length

    def __str__(self):
        """Prints overview of object for debugging purposes."""
        lines = [
            "Genome object:",
            f"length: {self.length}",
            f"chrom:\n{self.chrom}",
        ]
        return "\n".join(lines)

    def __repr__(self):
        return str(object=self)