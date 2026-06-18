from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_settings
from .exporter import DraftExporter
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
        "--write",
        action="store_true",
        help="Write to Notion and send the Resend digest. Overrides ANIPULSE_DRY_RUN.",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send the Resend digest without requiring Notion writes.",
    )
    parser.add_argument(
        "--skip-notion",
        action="store_true",
        help="Do not write Notion pages, even with --write.",
    )
    parser.add_argument(
        "--skip-email",
        action="store_true",
        help="Do not send the Resend digest, even with --write.",
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
    parser.add_argument(
        "--export-dir",
        default=None,
        help="Write JSON and Markdown exports to this directory.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = load_settings()
    wants_side_effect = args.write or args.send_email
    dry_run = args.dry_run or (settings.default_dry_run and not wants_side_effect)
    write_notion = args.write and not args.skip_notion
    send_email = (args.write or args.send_email) and not args.skip_email
    result = AniPulsePipeline(settings).run(
        dry_run=dry_run,
        limit=args.limit,
        write_notion=write_notion,
        send_email=send_email,
    )

    export_dir = args.export_dir
    if export_dir:
        export_result = DraftExporter(settings.export_dir if export_dir == "default" else Path(export_dir)).export(result.drafts)
        print(f"Exported JSON: {export_result.json_path}")
        print(f"Exported Markdown: {export_result.markdown_path}")

    if args.json:
        print(json.dumps([draft.model_dump(mode="json") for draft in result.drafts], indent=2, ensure_ascii=False))
        return

    print(f"AniPulse generated {len(result.drafts)} content draft(s).")
    for draft in result.drafts:
        print(draft.digest_line())
    if result.notion_page_ids:
        print(f"Created {len(result.notion_page_ids)} Notion page(s).")
        for page_id in result.notion_page_ids:
            print(f"- Notion page: https://app.notion.com/p/{page_id.replace('-', '')}")
    elif dry_run:
        print("Dry-run enabled: no Notion page or Resend email was created.")
    elif args.skip_notion:
        print("Notion write skipped.")

    if result.resend_email_id:
        print(f"Sent Resend email: {result.resend_email_id}")
    elif result.resend_skipped_reason and not dry_run:
        print(f"Resend email skipped: {result.resend_skipped_reason}")


if __name__ == "__main__":
    main()
