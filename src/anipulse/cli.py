from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anipulse",
        description="Generate and schedule AnimeSphere content drafts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned content without writing to Notion.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.dry_run:
        print("AniPulse dry run: content planning scaffold is ready.")
        return

    print("AniPulse scaffold is ready. Notion integration is not implemented yet.")


if __name__ == "__main__":
    main()
