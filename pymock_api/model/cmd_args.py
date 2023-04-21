from argparse import Namespace
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ParserArguments:
    """*The data object for the arguments from parsing the command line of PyMock-API program*"""

    subparser_name: Optional[str]


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):
    config: str
    app_type: str
    bind: str
    workers: int
    log_level: str


@dataclass(frozen=True)
class SubcmdConfigArguments(ParserArguments):
    generate_sample: bool
    print_sample: bool
    sample_output_path: str


class DeserializeParsedArgs:
    """*Deserialize the object *argparse.Namespace* to *ParserArguments*"""

    @classmethod
    def subcommand_run(cls, args: Namespace) -> SubcmdRunArguments:
        return SubcmdRunArguments(
            subparser_name=args.subcommand,
            config=args.config,
            app_type=args.app_type,
            bind=args.bind,
            workers=args.workers,
            log_level=args.log_level,
        )

    @classmethod
    def subcommand_config(cls, args: Namespace) -> SubcmdConfigArguments:
        return SubcmdConfigArguments(
            subparser_name=args.subcommand,
            generate_sample=args.generate_sample,
            print_sample=args.print_sample,
            sample_output_path=args.file_path,
        )
