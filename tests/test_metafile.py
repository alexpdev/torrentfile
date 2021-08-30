import os
import time
import pytest
from torrentfile import cli_parse
from tests.context import testfile, testdir


@pytest.fixture
def cliargs():
    args = ["--"]
    
    
def test_cli_args(testdir):
    args = ["-p","tests\\testdir"]
    assert cli_parse(args)