import sys
import argparse

from message_serializer.directory import Directory
from message_serializer.generator_cpp import CppGenerator


# Define command line arguments
arguments = [
    {
        "name": "--I",
        "help": "Input directory containing message definitions",
        "required": True,
    },
    {
        "name": "--L",
        "help": "Language for generated code",
        "choices": ["cpp"],
        "default": "cpp",
    },
    {
        "name": "--O",
        "help": "Output directory for generated code files",
        "required": True,
    },
]

parser = argparse.ArgumentParser(
    description="Generate code for message serialization/de-serialization for use in networking"
)

for arg in arguments:
    if "choices" in arg:
        parser.add_argument(
            arg["name"],
            help=arg["help"],
            choices=arg["choices"],
            default=arg["default"],
        )
    else:
        parser.add_argument(
            arg["name"], help=arg["help"], required=arg.get("required", False)
        )


if __name__ == "__main__":

    args = parser.parse_args()

    # sys.tracebacklimit = 0
    # Directory._debug = True
    D = Directory(args.I)
    tree, error_count = D.validate()
    if error_count > 0:
        print("Validation failed")
        exit(1)

    if args.L == "cpp":
        codeGen = CppGenerator(tree)
    else:
        print(f"Language {args.L} not supported")
        exit(1)

    codeGen.generate_source_files(args.O)

