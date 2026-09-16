"""CLI для экспорта протокола встречи в Word."""

import argparse
import asyncio
import sys
from pathlib import Path

from src.core.abc.result import FailResult, SuccessResult
from src.core.application.protocol import ExportProtocolDTO, ExportProtocolResult
from src.core.application.protocol.export_protocol_uc import ExportProtocolToDocxUC
from src.infra.di import create_container


async def _export(text: str) -> SuccessResult | FailResult:
    container = create_container()
    try:
        async with container() as scope:
            uc = await scope.get(ExportProtocolToDocxUC)
            return uc.execute(ExportProtocolDTO(text=text))
    finally:
        await container.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Export meeting protocol to DOCX")
    parser.add_argument(
        "--in",
        dest="input_path",
        required=True,
        help="Input markdown file",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        required=True,
        help="Output DOCX file",
    )
    args = parser.parse_args()

    text = Path(args.input_path).read_text(encoding="utf-8")
    result = asyncio.run(_export(text))

    if isinstance(result, FailResult):
        print(result.message, file=sys.stderr)
        raise SystemExit(1)

    assert isinstance(result, SuccessResult)
    assert isinstance(result.data, ExportProtocolResult)
    Path(args.output_path).write_bytes(result.data.content)


if __name__ == "__main__":
    main()
