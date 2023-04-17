from argparse import Namespace
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParserArguments:
    """*The data object for the arguments from parsing the command line of PyMock-API program*"""

    subparser_name: Optional[str] = None


@dataclass(frozen=True)
class SubcmdRunArguments(ParserArguments):
    config: Optional[str] = None
    app_type: Optional[str] = None
    bind: Optional[str] = None
    workers: Optional[int] = None
    log_level: Optional[str] = None


@dataclass(frozen=True)
class SubcmdConfigArguments(ParserArguments):
    generate_sample: Optional[bool] = None
    print_sample: Optional[bool] = None
    sample_output_path: Optional[str] = ""


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
