"""The ``usd-inspect`` command."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pxr import Tf, Usd

from usd_inspect import __version__
from usd_inspect.scene import find_missing_assets, list_attributes, list_prims, open_stage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="usd-inspect",
        description="Inspect prims, attributes, and missing files in a USD scene.",
    )
    parser.add_argument("file", help="the .usda or .usd file to inspect")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--prim",
        metavar="PATH",
        help="list the attributes authored on the prim at PATH, such as /World/Ball",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="list references and payloads whose files are missing; exit with status 1 if any are",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _print_table(rows: list[tuple[str, ...]]) -> None:
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]) - 1)]
    for row in rows:
        cells = [cell.ljust(width) for cell, width in zip(row, widths)] + [row[-1]]
        print("  ".join(cells).rstrip())


def _open_quietly(path: str) -> Usd.Stage:
    # USD prints a warning for each missing reference or payload while it opens
    # the stage. --check reports those itself, so discard the duplicates.
    with Tf.DiagnosticTrap() as trap:
        stage = open_stage(path)
        trap.ClearWarnings()
    return stage


def main(argv: Sequence[str] | None = None) -> int:
    """Run ``usd-inspect`` and return its exit status.

    Args:
        argv: The command-line arguments, without the program name. Defaults to
            ``sys.argv[1:]``.

    Returns:
        0 on success, 1 if ``--check`` finds missing files, or 2 if the
        arguments, file, or prim path are invalid.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        stage = _open_quietly(args.file)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    if args.check:
        missing = find_missing_assets(stage)
        if not missing:
            print("No missing files.")
            return 0
        _print_table([(item.prim_path, item.arc, item.asset_path) for item in missing])
        return 1

    if args.prim:
        try:
            attributes = list_attributes(stage, args.prim)
        except ValueError as error:
            parser.error(str(error))
        if not attributes:
            print(f"No authored attributes on {args.prim}.")
            return 0
        _print_table([(attr.name, attr.type_name, str(attr.value)) for attr in attributes])
        return 0

    prims = list_prims(stage)
    if not prims:
        print("No prims.")
        return 0
    _print_table([(prim.path, prim.type_name) for prim in prims])
    return 0


if __name__ == "__main__":
    sys.exit(main())
