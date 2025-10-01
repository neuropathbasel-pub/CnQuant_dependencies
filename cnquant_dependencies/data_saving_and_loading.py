import polars as pl
import pandas as pd
import hashlib
import zstandard as zstd
from pathlib import Path

def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file=file_path, mode="rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def save_to_parquet_with_checksum(dataframe: pl.DataFrame, file_path: Path) -> None:
    """Save a Polars DataFrame to Zstandard-compressed Parquet and generate SHA256 checksum."""
    # Save to Parquet with Zstandard compression
    dataframe.write_parquet(file=file_path, compression="zstd")
    
    # Compute and save checksum
    checksum = compute_sha256(file_path=file_path)
    checksum_file = file_path.with_suffix(suffix=file_path.suffix + ".sha256")
    with open(file=checksum_file, mode="w") as f:
        f.write(f"{checksum}  {file_path.name}\n")

def save_pandas_to_parquet_with_checksum(dataframe: pd.DataFrame, file_path: Path) -> None:
    """Save a Pandas DataFrame to Zstandard-compressed Parquet and generate SHA256 checksum."""
    # Save to Parquet with Zstandard compression
    dataframe.to_parquet(path=file_path, compression = "zstd")
    
    # Compute and save checksum
    checksum = compute_sha256(file_path=file_path)
    checksum_file = file_path.with_suffix(suffix=file_path.suffix + ".sha256")
    with open(file=checksum_file, mode="w") as f:
        f.write(f"{checksum}  {file_path.name}\n")


def load_parquet_with_checksum_verification(file_path: Path) -> pl.DataFrame:
    """Load a Parquet file and verify its SHA256 checksum."""
    checksum_file = file_path.with_suffix(suffix=file_path.suffix + ".sha256")
    if not checksum_file.exists():
        raise FileNotFoundError(f"Checksum file {checksum_file} not found.")
    
    # Read expected checksum
    with open(file=checksum_file, mode="r") as f:
        expected_checksum = f.read().split()[0]
    
    # Compute actual checksum
    actual_checksum = compute_sha256(file_path=file_path)
    
    if actual_checksum != expected_checksum:
        raise ValueError(f"Checksum mismatch for {file_path}. File may be corrupt.")
    
    # Load the DataFrame
    return pl.read_parquet(source=file_path)

def save_json_plot(json_str, plot_save_path: Path) -> None:
    """
    Saves a JSON string as a Zstandard-compressed file and generates a SHA256 checksum for integrity verification.

    The JSON data is encoded to bytes, compressed using Zstandard, and written to the specified path.
    A SHA256 checksum of the compressed data is computed and saved to a separate .sha256 file.

    Args:
        json_str (str): The JSON data as a string to be saved.
        plot_save_path (Path): The file path where the compressed JSON will be saved (should have .zst extension).

    Returns:
        None

    Notes:
        - The checksum file is saved with the same name as plot_save_path but with a .sha256 suffix.
        - Use load_json_plot_with_checksum_verification (if implemented) to load and verify the file.
    """
    json_bytes = json_str.encode("utf-8")
    cctx = zstd.ZstdCompressor()
    compressed = cctx.compress(data=json_bytes)
    
    # Write compressed data
    with open(file=plot_save_path, mode="wb") as f:
        f.write(compressed)
    
    # Compute and save SHA256 checksum
    sha256_hash = hashlib.sha256(string=compressed).hexdigest()
    checksum_path = plot_save_path.with_suffix('.sha256')
    with open(file=checksum_path, mode='w') as f:
        f.write(f"{sha256_hash}  {plot_save_path.name}\n")