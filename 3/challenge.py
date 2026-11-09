
import argparse
import os
import sys
from pathlib import Path

FLAG = "CTF{argparse_env_subprocess_files}"


def main():
    parser = argparse.ArgumentParser(
        description="CTF: CLI Lab. Begin with --stage 1"
    )

    parser.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4],
        required=True
    )

    parser.add_argument("--name")
    parser.add_argument("--answer", type=int)
    parser.add_argument("--mode", choices=["debug", "ctf"])
    parser.add_argument("--file", type=Path)

    args = parser.parse_args()

    # Этап 1: передача аргументов
    if args.stage == 1:
        if args.name != "student":
            parser.error("Stage 1: pass --name student")

        print("OK|stage=1")
        print("NEXT|--stage 2 --answer <sum of 14, 9, 7>")

    # Этап 2: вычисление ответа
    elif args.stage == 2:
        if args.answer != 30:
            parser.error(
                "Stage 2: calculate 14 + 9 + 7 and pass --answer"
            )

        print("OK|stage=2")
        print("NEXT|--stage 3 --mode ctf")
        print("HINT|set environment variable CTF_KEY=python")

    # Этап 3: переменные окружения
    elif args.stage == 3:
        if (
            args.mode != "ctf"
            or os.environ.get("CTF_KEY") != "python"
        ):
            parser.error(
                "Stage 3: use --mode ctf and CTF_KEY=python"
            )

        print("OK|stage=3")
        print("NEXT|--stage 4 --file <path>")
        print(
            "HINT|Create UTF-8 text file "
            "containing exactly: open-sesame"
        )

    # Этап 4: работа с файлом
    elif args.stage == 4:
        if args.file is None:
            parser.error("Stage 4: pass --file <path>")

        try:
            contents = args.file.read_text(
                encoding="utf-8"
            ).strip()
        except OSError as exc:
            parser.error(f"Cannot open file: {exc}")

        if contents != "open-sesame":
            parser.error("Stage 4: incorrect file contents")

        print("OK|stage=4")
        print(f"FLAG|{FLAG}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
