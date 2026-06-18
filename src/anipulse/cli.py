from __future__ import annotations

import argparse
import json

from .config import load_settings
from .pipeline import AniPulsePipeline


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
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override the daily content limit.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print planned content as JSON.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()
    result = AniPulsePipeline(settings).run(dry_run=args.dry_run, limit=args.limit)

    if args.json:
        print(json.dumps([draft.model_dump(mode="json") for draft in result.drafts], indent=2, ensure_ascii=False))
        return

    print(f"AniPulse generated {len(result.drafts)} content draft(s).")
    for draft in result.drafts:
        print(draft.digest_line())
    if result.notion_page_ids:
        print(f"Created {len(result.notion_page_ids)} Notion page(s).")
    elif args.dry_run:
        print("Dry-run enabled: no Notion page or Resend email was created.")


if __name__ == "__main__":
    main()
