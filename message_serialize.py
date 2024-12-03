import datetime
import sys
import argparse
import logging

from message_serializer.directory import Directory
from message_serializer.code_generators import pythonGenerator, CppGenerator

# Define command line arguments
arguments = [
    {
        "name": "I",
        "metavar": "input_dir",
        "help": "Input directory containing message definitions",
    },
    {
        "name": "D",
        "metavar": "output_dir",
        "help": "Output directory for generated code files",
    },
    {
        "name": "O",
        "metavar": "output_file",
        "help": "Output file name for generated code",
    },
    {
        "name": "-L",
        "metavar": "--lang",
        "help": "Language for generated code",
        "choices": ["cpp", "python"],
        "default": "cpp",
    },
]

parser = argparse.ArgumentParser(
    prog="python.exe message_serialize.py",
    description="Generate code for message serialization/de-serialization structs into byte arrays",
)

for arg in arguments:
    if "choices" in arg:
        parser.add_argument(
            arg["name"],
            help=arg["help"],
            choices=arg["choices"],
            default=arg["default"],
            metavar=arg["metavar"],
        )
    else:
        parser.add_argument(
            arg["name"],
            help=arg["help"],
            metavar=arg["metavar"],
        )

# set up logger
logger = logging.getLogger("message_serialize")


def directory_setup():
    # Create a directory structure for testing
    import os

    os.makedirs("log", exist_ok=True)


if __name__ == "__main__":
    directory_setup()

    # Set up logging
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    datetime = datetime.datetime.now()
    datetime = datetime.strftime("%Y-%m-%d_%H-%M-%S")

    session_file_handler = logging.FileHandler(
        f"log/{datetime}_message_serialize.log",
        mode="w",
    )
    session_file_handler.setLevel(logging.DEBUG)

    log_file_handler = logging.FileHandler(
        "log/message_serialize.log",
        mode="a",
    )
    log_file_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            log_file_handler,
            session_file_handler,
            stream_handler,
        ],
    )

    args = parser.parse_args()
    logger.debug(
        "Command Line Arguments:\n"
        f"\t\tInput directory: {args.I}\n"
        f"\t\tOutput directory: {args.D}\n"
        f"\t\tOutput file: {args.O}\n"
        f"\t\tLanguage: {args.L}\n"
    )

    # sys.tracebacklimit = 0
    # Directory._debug = True
    try:
        D = Directory(args.I)
        tree = D.validate()
    except Exception as e:
        logger.fatal(f"Error: {e}")
        exit(1)

    code_generators = {
        "cpp": CppGenerator,
        "python": pythonGenerator,
    }

    if args.L not in code_generators.keys():
        print(f"Language {args.L} not supported")
        exit(1)
    
    codeGen = code_generators[args.L](tree)
    codeGen.generate_source_files(args.D, args.O)
