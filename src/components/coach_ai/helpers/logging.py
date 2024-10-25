# Import standard library modules
import sys
import traceback
from enum import Enum
from typing import Optional

# Import third-party library modules
from fastapi import status
from loguru import logger

# Updated Log format string with Instance Name and Priority first
LOG_FORMAT_STRING = "\nInstance: <magenta>{extra[instance_name]}</magenta> | Priority: <red>{extra[priority]}</red> | Level: <level>{level}</level> | Timestamp: <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | Message: <level>{message}</level>"


class Priority(Enum):
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4"
    P5 = "p5"


# Default extra fields with metadata
LOG_EXTRA_METADATA = {
    "source": "coachai-api",
    "user": "",
    "ip": "",
    "method": "",
    "url": "",
    "instance_name": "",
    "priority": Priority.P5.value,
    "custom_metadata": {},
}


def log_to_monitor(record: dict, status_code: Optional[int] = status.HTTP_200_OK):
    level = record["level"].name
    source = record["extra"].get("source")
    method = record["extra"].get("method")
    path = record["extra"].get("path")
    custom_metadata = record["extra"].get("custom_metadata", {})

    format_string = LOG_FORMAT_STRING

    if level == "ERROR":
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if method and path:
        format_string += f" | Path: {method} {path}"

    if status_code:
        format_string += f" | Status Code: {status_code}"

    if record["extra"]["source"]:
        format_string += f" | Source: {source} "

    if record["extra"]["user"]:
        format_string += f" | User: {record['extra']['user']} "

    if record["extra"]["ip"]:
        format_string += f" | IP Address: {record['extra']['ip']} "

    # Add custom metadata (if any)
    if custom_metadata:
        format_string += f" | Metadata: {custom_metadata}"

    # Handle exception stack trace if it exists
    if record["exception"] is not None:
        record["extra"]["stack"] = traceback.format_stack(record["exception"])
        format_string += f"{record['extra']['stack']} \n"

    return format_string


def setup_logger():
    # Remove any existing logger handlers
    logger.remove()

    # Add custom logger with formatter
    logger.add(
        sys.stdout,
        format=log_to_monitor,
        colorize=True,
        backtrace=True,
        diagnose=True,
        catch=True,
    )

    # Configure logger to bind default metadata
    logger.configure(extra=LOG_EXTRA_METADATA)

    return logger


# Initialize the logger
log = setup_logger()


# Use bind internally to inject extra fields without requiring the user to use it
def log_with_context(
    level: str,
    message: str,
    instance_name: str = "api-log",
    priority: Priority = Priority.P5.value,
    custom_metadata: Optional[dict] = None,
):
    if custom_metadata is None:
        custom_metadata = {}

    # Use bind to attach context before logging the message
    log.bind(
        instance_name=instance_name, priority=priority, custom_metadata=custom_metadata
    ).log(level, message)


# Override logger methods (debug, info, warning, error, critical) to accept additional parameters
def override_logging_methods():
    # Override log.debug
    def custom_debug(
        message: str,
        instance_name: str = "api-log",
        priority: Priority = Priority.P5.value,
        custom_metadata: Optional[dict] = None,
    ):
        log_with_context("DEBUG", message, instance_name, priority, custom_metadata)

    # Override log.info
    def custom_info(
        message: str,
        instance_name: str = "api-log",
        priority: Priority = Priority.P5.value,
        custom_metadata: Optional[dict] = None,
    ):
        log_with_context("INFO", message, instance_name, priority, custom_metadata)

    # Override log.warning
    def custom_warning(
        message: str,
        instance_name: str = "api-log",
        priority: Priority = Priority.P4.value,
        custom_metadata: Optional[dict] = None,
    ):
        log_with_context("WARNING", message, instance_name, priority, custom_metadata)

    # Override log.error
    def custom_error(
        message: str,
        instance_name: str = "api-log",
        priority: Priority = Priority.P4.value,
        custom_metadata: Optional[dict] = None,
    ):
        log_with_context("ERROR", message, instance_name, priority, custom_metadata)

    # Override log.critical
    def custom_critical(
        message: str,
        instance_name: str = "api-log",
        priority: Priority = Priority.P1.value,
        custom_metadata: Optional[dict] = None,
    ):
        log_with_context("CRITICAL", message, instance_name, priority, custom_metadata)

    # Replace original methods with custom ones
    log.debug = custom_debug
    log.info = custom_info
    log.warning = custom_warning
    log.error = custom_error
    log.critical = custom_critical


# Apply the overrides to all log methods
override_logging_methods()
