import os
import shutil
from pathlib import Path

import polars as pl
import pyarrow as pa
import pyarrow.dataset as ds
import pyreadstat


def main():
    src = "nbbo_vgrd_etfs.sas7bdat"
    out = Path("taq_vgd_etfs")

    # Remove old output if rerunning
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # Hive-style partitioning: output/SYM_ROOT=AAPL/...
    partitioning = ds.partitioning(
        pa.schema([("SYM_ROOT", pa.string())]),
        flavor="hive",
    )

    parquet_format = ds.ParquetFileFormat()
    parquet_options = parquet_format.make_write_options(
        compression="zstd",
    )

    reader = pyreadstat.read_file_in_chunks(
        pyreadstat.read_sas7bdat,
        src,
        chunksize=1_000_000,
        multiprocess=True,
        num_processes=os.cpu_count(),
        output_format="polars",
        disable_datetime_conversion=True,
    )

    for chunk_i, (df, meta) in enumerate(reader):
        if "SYM_ROOT" not in df.columns:
            raise ValueError("Column SYM_ROOT not found in SAS file")

        # Ensure partition column is string-like
        df = df.with_columns(pl.col("SYM_ROOT").cast(pl.Utf8))

        table = df.to_arrow()

        ds.write_dataset(
            table,
            base_dir=str(out),
            format=parquet_format,
            file_options=parquet_options,
            partitioning=partitioning,
            existing_data_behavior="overwrite_or_ignore",
            # Important: unique names per chunk, so chunks do not overwrite each other
            basename_template=f"chunk-{chunk_i:05d}-part-{{i}}.parquet",
            # Useful for large TAQ/NBBO-style files
            max_partitions=20_000,
            max_open_files=128,
            max_rows_per_file=1_000_000,
            max_rows_per_group=250_000,
        )

    print(f"Wrote partitioned Parquet dataset to: {out}")


if __name__ == "__main__":
    main()
