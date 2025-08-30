"""
Module for executing kubectl commands in the Kubernetes cluster.

This module provides functionality to run kubectl commands using subprocess.
Note: subprocess is used to allow execution of shell commands, but using shell=True
can pose security risks if input is not sanitized properly.
"""

import subprocess
from typing import Optional

def run_kubectl(cmd: str) -> str:
    """
    Execute kubectl command in the cluster and return output.

    Args:
        cmd (str): The kubectl command to execute as a string.

    Returns:
        str: The combined standard output and standard error from the command execution.

    Raises:
        None: Exceptions are caught and returned as error messages.
    """
    try:
        # shell=True allows execution of the command string in the shell environment
        # capture_output=True captures both stdout and stderr
        # text=True returns output as string instead of bytes
        # check=False prevents subprocess from raising CalledProcessError on non-zero exit codes
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return result.stdout + result.stderr
    except Exception as e:
        # Catch all exceptions and return the error message as a string
        return f"Error executing kubectl: {e}"