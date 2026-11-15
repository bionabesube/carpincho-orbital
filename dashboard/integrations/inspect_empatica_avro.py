"""Inspect an Empatica Avro file's schema and top-level record keys.

This intentionally does not derive physiological metrics. Confirm the schema,
units, sampling rates, timestamps, and vendor documentation before mapping data.

Install optional dependency:
    pip install fastavro

Usage:
    python integrations/inspect_empatica_avro.py path/to/sample.avro
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from fastavro import reader
except ImportError as exc:
    raise SystemExit("Install fastavro first: pip install fastavro") from exc


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python integrations/inspect_empatica_avro.py sample.avro")

    path = Path(sys.argv[1])
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")

    with path.open("rb") as fh:
        avro_reader = reader(fh)
        print("=== AVRO WRITER SCHEMA ===")
        print(json.dumps(avro_reader.writer_schema, indent=2, ensure_ascii=False))
        first = next(iter(avro_reader), None)

    print("\n=== FIRST RECORD ===")
    if first is None:
        print("No records found")
        return
    print("Top-level keys:", list(first.keys()))
    # Avoid dumping high-frequency raw values or participant metadata by default.
    for key, value in first.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            print(f"{key}: {value}")
        elif isinstance(value, (list, tuple)):
            print(f"{key}: {type(value).__name__}, length={len(value)}")
        elif isinstance(value, dict):
            print(f"{key}: object keys={list(value.keys())}")
        else:
            print(f"{key}: {type(value).__name__}")


if __name__ == "__main__":
    main()
