"""CLI для экспорта протокола встречи в Word. Реализация — на этапе 3."""

import argparse


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
    parser.parse_args()
    raise NotImplementedError("Export will be implemented in stage 3")


if __name__ == "__main__":
    main()
