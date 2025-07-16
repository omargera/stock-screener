#!/usr/bin/env python3
"""
Stock Screener - Main Entry Point
Detects breakout patterns and volume spikes in stock data
"""

import argparse
import sys
import time

from gateways.stock_data_gateway import YahooFinanceGateway
from services.screener_service import ScreenerConfiguration, StockScreenerService
from utils.display import ResultsDisplayService

# Import custom modules
from utils.logging_config import LoggingConfig, setup_default_logging

# Set up logging
logger = LoggingConfig.get_logger(__name__)


def get_default_symbols() -> list[str]:
    """Get the default list of symbols to screen"""
    return [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA',
        'NVDA', 'META', 'NFLX', 'AMD', 'CRM',
        'BABA', 'UBER', 'SHOP', 'SQ', 'PYPL'
    ]


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Stock Screener - Detect breakouts and volume spikes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Screen default stocks
  python main.py --symbols AAPL MSFT GOOGL         # Screen specific stocks
  python main.py --period 6mo --volume-threshold 3 # Custom parameters
  python main.py --mode market-analysis             # Market analysis mode
  python main.py --mode top-opportunities --limit 3 # Top 3 opportunities
  python main.py --quiet                           # Quiet mode
  python main.py --health-check                    # System health check
        """
    )

    # Stock selection
    parser.add_argument(
        '--symbols', '-s',
        nargs='+',
        help='Stock symbols to screen (default: popular tech stocks)'
    )

    # Screening parameters
    parser.add_argument(
        '--period', '-p',
        default='3mo',
        choices=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
        help='Time period for analysis (default: 3mo)'
    )

    parser.add_argument(
        '--volume-threshold', '-v',
        type=float,
        default=2.0,
        help='Volume spike threshold multiplier (default: 2.0)'
    )

    parser.add_argument(
        '--breakout-threshold', '-b',
        type=float,
        default=0.02,
        help='Breakout threshold percentage (default: 0.02 = 2%%)'
    )

    # Operating modes
    parser.add_argument(
        '--mode', '-m',
        choices=['screen', 'market-analysis', 'top-opportunities', 'signals-only'],
        default='screen',
        help='Operating mode (default: screen)'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=5,
        help='Limit results in top-opportunities mode (default: 5)'
    )

    # Output options
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - minimal output'
    )

    parser.add_argument(
        '--verbose', '--debug',
        action='store_true',
        help='Verbose debug output'
    )

    # System options
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Run system health check and exit'
    )

    parser.add_argument(
        '--log-file',
        help='Log to specified file'
    )

    return parser.parse_args()


def setup_logging_from_args(args):
    """Set up logging based on command line arguments"""
    if args.quiet:
        setup_default_logging("quiet")
    elif args.verbose:
        setup_default_logging("development")
    else:
        setup_default_logging("production")

    # Override with file logging if specified
    if args.log_file:
        LoggingConfig.setup_logging(
            level="DEBUG" if args.verbose else "INFO",
            log_to_file=True,
            log_file_path=args.log_file
        )


def run_health_check(screener_service: StockScreenerService, display: ResultsDisplayService) -> int:
    """
    Run system health check

    Args:
        screener_service: Screener service instance
        display: Display service instance

    Returns:
        int: Exit code (0 for healthy, 1 for issues)
    """
    logger.info("Running system health check...")

    health_status = screener_service.test_system_health()
    display.display_system_health(health_status)

    if health_status.get('overall') == 'healthy':
        logger.info("System health check passed")
        return 0
    else:
        logger.warning("System health check found issues")
        return 1


def run_screening(
    screener_service: StockScreenerService,
    display: ResultsDisplayService,
    symbols: list[str],
    mode: str,
    limit: int
) -> int:
    """
    Run stock screening based on mode

    Args:
        screener_service: Screener service instance
        display: Display service instance
        symbols: List of symbols to screen
        mode: Operating mode
        limit: Limit for results

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        start_time = time.time()

        if mode == 'screen':
            # Standard screening mode
            results = screener_service.screen_multiple_stocks(symbols)
            display.display_screening_results(results)

        elif mode == 'signals-only':
            # Only show stocks with signals
            results = screener_service.get_stocks_with_signals(symbols)
            if results.signal_count > 0:
                display.display_screening_results(results)
            else:
                display.display_error_message("No signals detected in current screening.", "INFO")

        elif mode == 'market-analysis':
            # Market condition analysis
            analysis = screener_service.analyze_market_conditions(symbols)
            display.display_market_analysis(analysis)

        elif mode == 'top-opportunities':
            # Top opportunities mode
            opportunities = screener_service.get_top_opportunities(symbols, limit)
            display.display_top_opportunities(opportunities, limit)

        execution_time = time.time() - start_time
        logger.info(f"Screening completed in {execution_time:.2f} seconds")

        return 0

    except Exception as e:
        logger.error(f"Error during screening: {str(e)}")
        display.display_error_message(f"Screening failed: {str(e)}")
        return 1


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()

    # Set up logging
    setup_logging_from_args(args)

    # Initialize services
    display = ResultsDisplayService()

    # Show welcome message unless in quiet mode
    if not args.quiet:
        display.display_welcome_message()

    try:
        # Create configuration
        config = ScreenerConfiguration(
            period=args.period,
            volume_spike_threshold=args.volume_threshold,
            breakout_threshold=args.breakout_threshold
        )

        # Initialize screener service
        data_gateway = YahooFinanceGateway()
        screener_service = StockScreenerService(config, data_gateway)

        # Health check mode
        if args.health_check:
            return run_health_check(screener_service, display)

        # Get symbols to screen
        symbols = args.symbols if args.symbols else get_default_symbols()

        if not args.quiet:
            print(f"Screening {len(symbols)} stocks for breakouts and volume spikes...")
            logger.info(f"Starting screening with config: {vars(config)}")

        # Run screening
        exit_code = run_screening(screener_service, display, symbols, args.mode, args.limit)

        return exit_code

    except KeyboardInterrupt:
        logger.info("Screening interrupted by user")
        display.display_error_message("Screening interrupted by user", "WARNING")
        return 130  # Standard exit code for Ctrl+C

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        display.display_error_message(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
