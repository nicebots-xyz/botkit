# Copyright (c) NiceBots
# SPDX-License-Identifier: MIT

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from .convert import env_to_yaml, yaml_to_env


def main() -> None:  # noqa: PLR0912
    parser = argparse.ArgumentParser(description="Convert config between YAML and env formats.")
    parser.add_argument("-i", "--input", help="Input file path", default=None)
    parser.add_argument("--input-format", help="Input format (yaml, yml, env)", default=None)
    parser.add_argument("--output", help="Output file path", default=None)
    parser.add_argument("--output-format", help="Output format (yaml, yml, env)", default=None)
    parser.add_argument("--terminal", action="store_true", help="Output to terminal instead of file")

    args = parser.parse_args()

    input_path = Path(args.input) if args.input else None
    output_path = Path(args.output) if args.output else None
    input_format = args.input_format
    output_format = args.output_format
    terminal = args.terminal

    if not input_path:
        if Path("config.yaml").exists():
            input_path = Path("config.yaml")
        elif Path("config.yml").exists():
            input_path = Path("config.yml")
        elif Path(".env").exists():
            input_path = Path(".env")
        else:
            print("No input file found.")
            sys.exit(1)

    input_format = input_format or input_path.suffix[1:] if input_path.name != ".env" else "env"

    if not output_format:
        output_format = "env" if input_format in ["yaml", "yml"] else "yaml"

    if terminal:
        output_path = None
    elif not output_path:
        if output_format == "env":
            output_path = Path(".env")
            if output_path.exists() and output_path.stat().st_size != 0:
                response = input(".env file is not empty. Overwrite? (y/n): ")
                if response.lower() != "y":
                    output_path = Path(f"{datetime.now(tz=UTC).strftime('%Y%m%d%H%M%S')}.converted.env")
        else:
            output_path = Path("config.yaml")

    # Fixed conversion logic
    if input_format in ["yaml", "yml"] and output_format == "env":
        yaml_to_env(input_path, output_path)
    elif input_format == "env" and output_format in ["yaml", "yml"]:
        env_to_yaml(input_path, output_path)
    else:
        print(f"Invalid conversion from '{input_format}' to '{output_format}'")
        print("Supported conversions: yaml->env, yml->env, env->yaml, env->yml")
        sys.exit(1)


if __name__ == "__main__":
    main()
