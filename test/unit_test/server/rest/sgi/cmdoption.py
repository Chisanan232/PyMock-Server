from abc import ABCMeta, abstractmethod
from typing import List, Tuple

import pytest

from pymock_server.server.rest.sgi.cmdoption import (
    ASGICmdOption,
    BaseCommandOption,
    WSGICmdOption,
)

from ....._values import _Bind_Host_And_Port, _Log_Level, _Workers_Amount


class BaseCommandOptionTest(metaclass=ABCMeta):
    @pytest.fixture(scope="function")
    @abstractmethod
    def cmd_option(self) -> BaseCommandOption:
        pass

    def test_help(self, cmd_option: BaseCommandOption):
        assert cmd_option.help() == self._expected_help_option()

    def _expected_help_option(self) -> str:
        return "--help"

    def test_version(self, cmd_option: BaseCommandOption):
        assert cmd_option.version() == self._expected_version_option()

    def _expected_version_option(self) -> str:
        return "--version"

    @pytest.mark.parametrize(
        ("address", "args", "expect"),
        [
            ([_Bind_Host_And_Port.value], ("address",), _Bind_Host_And_Port.value),
            (_Bind_Host_And_Port.value.split(":"), ("host", "port"), _Bind_Host_And_Port.value),
        ],
    )
    def test_bind(self, cmd_option: BaseCommandOption, address: List[str], args: Tuple[str], expect: str):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad

        assert cmd_option.bind(**bind_args) == self._expected_bind_option(expect)

    def _expected_bind_option(self, expect: str) -> str:
        return f"--bind {expect}"

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
        self, cmd_option: BaseCommandOption, address: List[str], args: Tuple[str], exc_type: Exception, err_msg: str
    ):
        bind_args = {}
        for arg, ad in zip(args, address):
            bind_args[arg] = ad
        with pytest.raises(exc_type) as exc_info:
            cmd_option.bind(**bind_args)

        assert str(exc_info.value) == err_msg

    def test_workers(self, cmd_option: BaseCommandOption):
        workers_amt = _Workers_Amount.value
        assert cmd_option.workers(w=workers_amt) == self._expected_workers_option(workers_amt)

    def _expected_workers_option(self, workers_amt: int) -> str:
        return f"--workers {workers_amt}"

    def test_log_level(self, cmd_option: BaseCommandOption):
        log_level = _Log_Level.value
        assert cmd_option.log_level(level=log_level) == self._expected_log_level_option(log_level)

    def _expected_log_level_option(self, log_level: str) -> str:
        return f"--log-level {log_level}"


class TestWSGICmdOption(BaseCommandOptionTest):
    @pytest.fixture(scope="function")
    def cmd_option(self) -> WSGICmdOption:
        return WSGICmdOption()


class TestASGICmdOption(BaseCommandOptionTest):
    @pytest.fixture(scope="function")
    def cmd_option(self) -> ASGICmdOption:
        return ASGICmdOption()

    def _expected_bind_option(self, expect: str) -> str:
        expect_info = expect.split(":")
        return f"--host {expect_info[0]} --port {expect_info[1]}"
