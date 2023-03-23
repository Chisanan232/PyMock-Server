from typing import List, Tuple

import pytest

from pymock_api.server.sgi.cmdoption import ASGICmdOption, WSGICmdOption

from ...._values import _Bind_Host_And_Port, _Log_Level, _Workers_Amount


class TestWSGICmdOption:
    @pytest.fixture(scope="function")
    def cmd_option(self) -> WSGICmdOption:
        return WSGICmdOption()

    def test_help(self, cmd_option: WSGICmdOption):
        assert cmd_option.help() == "--help"

    def test_version(self, cmd_option: WSGICmdOption):
        assert cmd_option.version() == "--version"

    @pytest.mark.parametrize(
        ("address", "args", "expect"),
        [
            ([_Bind_Host_And_Port.value], ("address",), _Bind_Host_And_Port.value),
            (_Bind_Host_And_Port.value.split(":"), ("host", "port"), _Bind_Host_And_Port.value),
        ],
    )
    def test_bind(self, cmd_option: WSGICmdOption, address: List[str], args: Tuple[str], expect: str):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad

        assert cmd_option.bind(**bind_args) == f"--bind {expect}"

    @pytest.mark.parametrize(
        ("address", "args", "exc_type", "err_msg"),
        [
            (
                [None, "test"],
                ("host", "port"),
                ValueError,
                "There are 2 ways to pass arguments: using *address* or using *host* and *port*.",
            ),
            (
                ["test", None],
                ("host", "port"),
                ValueError,
                "There are 2 ways to pass arguments: using *address* or using *host* and *port*.",
            ),
        ],
    )
    def test_bind_with_invalid_args(
        self, cmd_option: WSGICmdOption, address: List[str], args: Tuple[str], exc_type: Exception, err_msg: str
    ):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad
        with pytest.raises(exc_type) as exc_info:
            cmd_option.bind(**bind_args)

        assert str(exc_info.value) == err_msg

    def test_workers(self, cmd_option: WSGICmdOption):
        workers_amt = _Workers_Amount.value
        assert cmd_option.workers(w=workers_amt) == f"--workers {workers_amt}"

    def test_log_level(self, cmd_option: WSGICmdOption):
        log_level = _Log_Level.value
        assert cmd_option.log_level(level=log_level) == f"--log-level {log_level}"


class TestASGICmdOption:
    @pytest.fixture(scope="function")
    def cmd_option(self) -> ASGICmdOption:
        return ASGICmdOption()

    def test_help(self, cmd_option: ASGICmdOption):
        assert cmd_option.help() == "--help"

    def test_version(self, cmd_option: ASGICmdOption):
        assert cmd_option.version() == "--version"

    @pytest.mark.parametrize(
        ("address", "args", "expect"),
        [
            ([_Bind_Host_And_Port.value], ("address",), _Bind_Host_And_Port.value.split(":")),
            (_Bind_Host_And_Port.value.split(":"), ("host", "port"), _Bind_Host_And_Port.value.split(":")),
        ],
    )
    def test_bind(self, cmd_option: ASGICmdOption, address: List[str], args: Tuple[str], expect: List[str]):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad

        assert cmd_option.bind(**bind_args) == f"--host {expect[0]} --port {expect[1]}"

    @pytest.mark.parametrize(
        ("address", "args", "exc_type", "err_msg"),
        [
            (
                ["invalid IPv4 address", None, None],
                ("address", "host", "port"),
                ValueError,
                "The address info is invalid. Please entry value format should be as <IPv4 address>:<Port>.",
            ),
            (
                [None, "test"],
                ("host", "port"),
                ValueError,
                "There are 2 ways to pass arguments: using *address* or using *host* and *port*.",
            ),
            (
                ["test", None],
                ("host", "port"),
                ValueError,
                "There are 2 ways to pass arguments: using *address* or using *host* and *port*.",
            ),
        ],
    )
    def test_bind_with_invalid_args(
        self, cmd_option: ASGICmdOption, address: List[str], args: Tuple[str], exc_type: Exception, err_msg: str
    ):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad
        with pytest.raises(exc_type) as exc_info:
            cmd_option.bind(**bind_args)

        assert str(exc_info.value) == err_msg

    def test_workers(self, cmd_option: ASGICmdOption):
        workers_amt = _Workers_Amount.value
        assert cmd_option.workers(w=workers_amt) == f"--workers {workers_amt}"

    def test_log_level(self, cmd_option: ASGICmdOption):
        log_level = _Log_Level.value
        assert cmd_option.log_level(level=log_level) == f"--log-level {log_level}"
