import polars as pl
import pandas as pd
import orjson
import hashlib
import pickle
import zstandard as zstd
from pathlib import Path
from typing import Any
from cnquant_dependencies.custom_errors import FileCorruptionError

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
    dataframe.to_parquet(path=file_path, compression = "zstd", index = False)
    
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
        raise FileCorruptionError(f"Checksum mismatch for {file_path}. The file might be corrupt.")
    
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
    checksum_path = plot_save_path.with_suffix(suffix=plot_save_path.suffix + ".sha256")
    with open(file=checksum_path, mode='w') as f:
        f.write(f"{sha256_hash}  {plot_save_path.name}\n")

################################ Saving and loading manifest objects #########################################
def save_pickle_with_checksum(obj: Any, file_path: Path) -> None:
    """
    Saves an object to a pickle file and generates a SHA256 checksum for verification.

    Args:
        obj: The Python object to serialize and save.
        file_path: The path to save the pickle file (e.g., 'data.pkl').

    Raises:
        Exception: If saving or hashing fails.
    """
    # Serialize the object
    pickle_bytes = pickle.dumps(obj)
    
    # Compute SHA256 hash
    sha256_hash = hashlib.sha256(pickle_bytes).hexdigest()
    
    # Save the pickle file
    with open(file_path, 'wb') as f:
        f.write(pickle_bytes)
    
    # Save the checksum to a .sha256 file
    checksum_path = file_path.with_suffix(suffix=file_path.suffix + ".sha256")
    with open(checksum_path, 'w') as f:
        f.write(f"{sha256_hash}  {file_path.name}\n")

def load_pickle_with_checksum(file_path: Path) -> Any:
    """
    Loads an object from a pickle file and verifies its SHA256 checksum.

    Args:
        file_path: The path to the pickle file (e.g., 'data.pkl').

    Returns:
        The deserialized Python object.

    Raises:
        FileNotFoundError: If the pickle or checksum file is missing.
        FileCorruptionError: If the checksum does not match.
        Exception: For other loading or verification errors.
    """
    checksum_path = file_path.with_suffix('.sha256')
    
    if not file_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {file_path}")
    if not checksum_path.exists():
        raise FileNotFoundError(f"Checksum file not found: {checksum_path}")
    
    # Read the pickle file
    with open(file_path, 'rb') as f:
        pickle_bytes = f.read()
    
    # Compute the hash of the loaded bytes
    actual_hash = hashlib.sha256(pickle_bytes).hexdigest()
    
    # Read the expected hash from the checksum file
    with open(checksum_path, 'r') as f:
        expected_hash = f.read().split()[0]
    
    # Verify
    if actual_hash != expected_hash:
        raise FileCorruptionError(file_path=f"Checksum mismatch for {file_path}. The file might be corrupt.")
    
    # Deserialize and return
    return pickle.loads(pickle_bytes)


def load_zstd_json_plot_to_dict(file_path: Path) -> dict:
    """Loads a Zstandard-compressed JSON file into a dictionary and verifies its SHA256 checksum.
    
    Args:
        file_path (Path): The path to the compressed JSON file (.json.zst).
    
    Returns:
        dict: The deserialized JSON data as a dictionary.
    
    Raises:
        FileNotFoundError: If the file or its checksum file (.sha256) does not exist.
        ValueError: If the checksum verification fails, indicating potential file corruption.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file=file_path, mode='rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(source=f) as reader:
            file_content = reader.read()
            data = orjson.loads(file_content)

    checksum_file = file_path.with_suffix(suffix=file_path.suffix + ".sha256")
    if not checksum_file.exists():
        raise FileNotFoundError(f"Checksum file {checksum_file} not found.")
    
    # Read expected checksum
    with open(file=checksum_file, mode="r") as f:
        expected_checksum = f.read().split()[0]

    # Compute actual checksum
    actual_checksum = compute_sha256(file_path=file_path)
    
    if actual_checksum != expected_checksum:
        raise FileCorruptionError(f"Checksum mismatch for {file_path}. The file may be corrupt.")

    return data