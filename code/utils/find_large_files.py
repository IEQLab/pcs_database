"""
Utility: Find files larger than a given threshold (default: 50 MB) in this repo.

Usage examples:
  - Default scan from repo root with 50 MB threshold (auto-saves to data/others/):
      python code/utils/find_large_files.py

  - Custom threshold and extra excludes:
      python code/utils/find_large_files.py --min-size-mb 25 --exclude .git --exclude venv

  - Save results to custom location (csv, tsv, json, or txt):
      python code/utils/find_large_files.py --save data/custom_large_files_report.csv
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Dict

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from code.config.configuration import Config


DEFAULT_EXCLUDES = {
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "__pycache__",
    ".ipynb_checkpoints",
    "out",
    "build",
    "dist",
    ".docusaurus",
}


def bytes_to_human(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:.2f} {u}"
        size /= 1024.0


def find_repo_root() -> Path:
    # This file lives at repo_root/code/utils/find_large_files.py
    here = Path(__file__).resolve()
    # Two parents up should be the repo root
    return here.parents[2]


def scan_large_files(
    root: Path,
    min_size_bytes: int,
    exclude_dirs: Iterable[str] = (),
) -> List[Dict[str, str]]:
    exclude_set = set(exclude_dirs)
    results: List[Dict[str, str]] = []

    for current_root, dirs, files in os.walk(root, topdown=True):
        # Prune excluded directories in-place for efficiency
        dirs[:] = [d for d in dirs if d not in exclude_set]

        for fname in files:
            fpath = Path(current_root) / fname
            try:
                size = fpath.stat().st_size
            except OSError:
                # Skip files we can't stat (permissions, broken links, etc.)
                continue

            if size >= min_size_bytes:
                rel = fpath.relative_to(root)
                results.append(
                    {
                        "path": str(rel).replace("\\", "/"),
                        "size_bytes": size,
                        "size_human": bytes_to_human(size),
                    }
                )

    # Sort by size desc
    results.sort(key=lambda x: x["size_bytes"], reverse=True)
    return results


def save_results(path: Path, rows: List[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        with path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    elif path.suffix.lower() in {".csv", ".tsv"}:
        sep = "," if path.suffix.lower() == ".csv" else "\t"
        import csv

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=sep)
            writer.writerow(["path", "size_bytes", "size_human"])
            for r in rows:
                writer.writerow([r["path"], r["size_bytes"], r["size_human"]])
    else:
        # Plain text
        with path.open("w", encoding="utf-8") as f:
            if not rows:
                f.write("No files exceed the threshold.\n")
            else:
                f.write("Files exceeding threshold:\n")
                for r in rows:
                    f.write(f"{r['size_human']}\t{r['path']}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Find files larger than a given size in this repository.")
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Root directory to scan (default: repository root)",
    )
    parser.add_argument(
        "--min-size-mb",
        type=float,
        default=50.0,
        help="Minimum file size in MB (default: 50)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Directory name to exclude (can be repeated). Defaults include common build/venv dirs.",
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Optional path to save results (csv, tsv, json, or txt)",
    )

    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else find_repo_root()
    min_size_bytes = int(args.min_size_mb * 1024 * 1024)

    exclude_dirs = set(DEFAULT_EXCLUDES)
    if args.exclude:
        exclude_dirs.update(args.exclude)

    rows = scan_large_files(root=root, min_size_bytes=min_size_bytes, exclude_dirs=exclude_dirs)

    if rows:
        print(f"Found {len(rows)} file(s) over {args.min_size_mb:.2f} MB under: {root}")
        for r in rows:
            print(f"{r['size_human']}: {r['path']}")
    else:
        print(f"No files over {args.min_size_mb:.2f} MB under: {root}")

    if args.save:
        save_results(Path(args.save), rows)
        print(f"Saved results to: {args.save}")
    else:
        # Default save location using Config.DataPaths.OTHERS_DIR
        if rows:  # Only save if there are results
            csv_path = os.path.join(Config.DataPaths.OTHERS_DIR, f"large_files_over_{args.min_size_mb:.0f}mb.csv")
            json_path = os.path.join(Config.DataPaths.OTHERS_DIR, f"large_files_over_{args.min_size_mb:.0f}mb.json")
            
            # Ensure the others directory exists
            os.makedirs(Config.DataPaths.OTHERS_DIR, exist_ok=True)
            
            save_results(Path(csv_path), rows)
            save_results(Path(json_path), rows)
            print(f"Results automatically saved to:")
            print(f"  CSV: {csv_path}")
            print(f"  JSON: {json_path}")

    # Exit code 0 if none found, 1 if some found (useful for CI checks)
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
