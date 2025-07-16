"""
Logging configuration utilities for the stock screener
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class LoggingConfig:
    """Configuration class for application logging"""

    @staticmethod
    def setup_logging(
        level: str = "INFO",
        log_to_file: bool = False,
        log_file_path: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        format_style: str = "detailed"
    ) -> None:
        """
        Set up application logging configuration

        Args:
            level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file (bool): Whether to log to file
            log_file_path (str, optional): Path to log file
            max_file_size (int): Maximum file size before rotation
            backup_count (int): Number of backup files to keep
            format_style (str): Format style (simple, detailed, json)
        """
        # Clear any existing handlers
        logging.getLogger().handlers.clear()

        # Set root logger level
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)

        # Create formatters
        formatter = LoggingConfig._get_formatter(format_style)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

        # File handler (if requested)
        if log_to_file:
            file_handler = LoggingConfig._setup_file_handler(
                log_file_path, max_file_size, backup_count, formatter
            )
            if file_handler:
                logging.getLogger().addHandler(file_handler)

        # Log initial message
        logger = logging.getLogger(__name__)
        logger.info(f"Logging configured - Level: {level}, File: {log_to_file}")

    @staticmethod
    def _get_formatter(style: str) -> logging.Formatter:
        """
        Get log formatter based on style

        Args:
            style (str): Format style

        Returns:
            logging.Formatter: Configured formatter
        """
        formats = {
            "simple": "%(levelname)s - %(message)s",
            "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "json": "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            "debug": "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(funcName)s() - %(message)s"
        }

        format_string = formats.get(style, formats["detailed"])
        return logging.Formatter(format_string)

    @staticmethod
    def _setup_file_handler(
        log_file_path: Optional[str],
        max_file_size: int,
        backup_count: int,
        formatter: logging.Formatter
    ) -> Optional[logging.Handler]:
        """
        Set up rotating file handler

        Args:
            log_file_path (str, optional): Path to log file
            max_file_size (int): Maximum file size before rotation
            backup_count (int): Number of backup files to keep
            formatter (logging.Formatter): Log formatter

        Returns:
            logging.Handler: File handler or None if failed
        """
        try:
            # Default log file path
            if log_file_path is None:
                logs_dir = "logs"
                os.makedirs(logs_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d")
                log_file_path = os.path.join(logs_dir, f"stock_screener_{timestamp}.log")

            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_file_size,
                backupCount=backup_count
            )
            file_handler.setFormatter(formatter)

            return file_handler

        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")
            return None

    @staticmethod
    def setup_development_logging() -> None:
        """Set up logging for development environment"""
        LoggingConfig.setup_logging(
            level="DEBUG",
            log_to_file=True,
            format_style="debug"
        )

    @staticmethod
    def setup_production_logging() -> None:
        """Set up logging for production environment"""
        LoggingConfig.setup_logging(
            level="INFO",
            log_to_file=True,
            format_style="detailed"
        )

    @staticmethod
    def setup_quiet_logging() -> None:
        """Set up minimal logging for quiet operation"""
        LoggingConfig.setup_logging(
            level="WARNING",
            log_to_file=False,
            format_style="simple"
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance with the given name

        Args:
            name (str): Logger name (usually __name__)

        Returns:
            logging.Logger: Logger instance
        """
        return logging.getLogger(name)


class PerformanceLogger:
    """Utility for logging performance metrics"""

    def __init__(self, logger_name: str = "performance"):
        self.logger = logging.getLogger(logger_name)

    def log_screening_performance(
        self,
        symbols_count: int,
        execution_time: float,
        successful_screens: int,
        failed_screens: int
    ) -> None:
        """
        Log screening performance metrics

        Args:
            symbols_count (int): Number of symbols processed
            execution_time (float): Total execution time in seconds
            successful_screens (int): Number of successful screens
            failed_screens (int): Number of failed screens
        """
        avg_time_per_symbol = execution_time / symbols_count if symbols_count > 0 else 0
        success_rate = (successful_screens / symbols_count * 100) if symbols_count > 0 else 0

        self.logger.info(
            f"Screening Performance: "
            f"Symbols={symbols_count}, "
            f"Time={execution_time:.2f}s, "
            f"Avg/Symbol={avg_time_per_symbol:.2f}s, "
            f"Success={successful_screens}, "
            f"Failed={failed_screens}, "
            f"Success Rate={success_rate:.1f}%"
        )

    def log_api_performance(self, symbol: str, fetch_time: float, data_points: int) -> None:
        """
        Log API fetch performance

        Args:
            symbol (str): Stock symbol
            fetch_time (float): Time taken to fetch data
            data_points (int): Number of data points received
        """
        self.logger.debug(
            f"API Performance: {symbol} - "
            f"Time={fetch_time:.2f}s, "
            f"DataPoints={data_points}"
        )


class AuditLogger:
    """Utility for audit logging"""

    def __init__(self, logger_name: str = "audit"):
        self.logger = logging.getLogger(logger_name)

    def log_screening_session(
        self,
        session_id: str,
        symbols: list,
        config: dict,
        results_summary: dict
    ) -> None:
        """
        Log a complete screening session for audit purposes

        Args:
            session_id (str): Unique session identifier
            symbols (list): List of symbols screened
            config (dict): Screening configuration used
            results_summary (dict): Summary of results
        """
        self.logger.info(
            f"Screening Session: ID={session_id}, "
            f"Symbols={len(symbols)}, "
            f"Config={config}, "
            f"Results={results_summary}"
        )

    def log_signal_detection(self, symbol: str, signals: dict) -> None:
        """
        Log signal detection for audit trail

        Args:
            symbol (str): Stock symbol
            signals (dict): Detected signals
        """
        if any(signals.values()):  # Only log if there are actual signals
            self.logger.info(f"Signals Detected: {symbol} - {signals}")


# Convenience function for quick setup
def setup_default_logging(environment: str = "production") -> None:
    """
    Set up default logging based on environment

    Args:
        environment (str): Environment type (development, production, quiet)
    """
    env_setups = {
        "development": LoggingConfig.setup_development_logging,
        "production": LoggingConfig.setup_production_logging,
        "quiet": LoggingConfig.setup_quiet_logging
    }

    setup_func = env_setups.get(environment, LoggingConfig.setup_production_logging)
    setup_func()


# Example usage and testing
if __name__ == "__main__":
    # Test logging configuration
    setup_default_logging("development")

    logger = LoggingConfig.get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Test performance logging
    perf_logger = PerformanceLogger()
    perf_logger.log_screening_performance(10, 25.5, 8, 2)

    # Test audit logging
    audit_logger = AuditLogger()
    audit_logger.log_signal_detection("AAPL", {"breakout": True, "volume_spike": False})
