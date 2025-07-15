#!/usr/bin/env python3
"""
Test runner for the stock screener project
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(command, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(command)}")
    print()
    
    # Set up environment with src in PYTHONPATH
    env = os.environ.copy()
    current_pythonpath = env.get('PYTHONPATH', '')
    src_path = str(Path.cwd() / 'src')
    if current_pythonpath:
        env['PYTHONPATH'] = f"{src_path}:{current_pythonpath}"
    else:
        env['PYTHONPATH'] = src_path
    
    try:
        result = subprocess.run(command, check=True, capture_output=False, env=env)
        print(f"\n✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"\n❌ {description} - FAILED (command not found)")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for the stock screener project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --fast             # Skip slow tests
  python run_tests.py --verbose          # Verbose output
        """
    )
    
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run tests with coverage report'
    )
    
    parser.add_argument(
        '--fast', '-f',
        action='store_true',
        help='Skip slow tests'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--markers', '-m',
        help='Run tests with specific markers (e.g., -m "not slow")'
    )
    
    parser.add_argument(
        '--pattern', '-k',
        help='Run tests matching pattern'
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test paths
    if args.unit:
        cmd.append('tests/unit')
    elif args.integration:
        cmd.append('tests/integration')
    else:
        cmd.append('tests/')
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(['--cov=src/models', '--cov=src/services', '--cov=src/gateways', '--cov=src/utils'])
        cmd.extend(['--cov-report=term-missing', '--cov-report=html:htmlcov'])
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    else:
        cmd.append('--tb=short')
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(['-n', 'auto'])
    
    # Add markers
    if args.fast:
        cmd.extend(['-m', 'not slow'])
    elif args.markers:
        cmd.extend(['-m', args.markers])
    
    # Add pattern matching
    if args.pattern:
        cmd.extend(['-k', args.pattern])
    
    # Additional options
    cmd.extend([
        '--strict-markers',
        '--strict-config',
        '--color=yes'
    ])
    
    print("🔍 Stock Screener Test Suite")
    print("="*60)
    
    # Check if pytest is available
    try:
        subprocess.run(['python', '-m', 'pytest', '--version'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pytest not found. Please install test dependencies:")
        print("   pip install -r requirements.txt")
        return 1
    
    # Run tests
    success = run_command(cmd, "Running Tests")
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("   - Terminal: See output above")
            print("   - HTML: Open htmlcov/index.html in browser")
        
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


def run_quick_tests():
    """Run a quick subset of tests for CI/development"""
    cmd = [
        'python', '-m', 'pytest',
        'tests/unit',
        '-v',
        '--tb=short',
        '-x',  # Stop on first failure
        '--color=yes'
    ]
    
    return run_command(cmd, "Quick Test Suite")


def run_full_test_suite():
    """Run the complete test suite with coverage"""
    commands = [
        # Unit tests with coverage
        ([
            'python', '-m', 'pytest',
            'tests/unit',
            '--cov=src/models',
            '--cov=src/services', 
            '--cov=src/gateways',
            '--cov=src/utils',
            '--cov-report=term-missing',
            '-v'
        ], "Unit Tests with Coverage"),
        
        # Integration tests
        ([
            'python', '-m', 'pytest',
            'tests/integration',
            '-v',
            '--tb=short'
        ], "Integration Tests"),
        
        # Signal accuracy tests
        ([
            'python', '-m', 'pytest',
            'tests/integration/test_signal_accuracy.py',
            '-v',
            '--tb=long'
        ], "Signal Accuracy Tests")
    ]
    
    all_passed = True
    for cmd, description in commands:
        success = run_command(cmd, description)
        if not success:
            all_passed = False
    
    return all_passed


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 