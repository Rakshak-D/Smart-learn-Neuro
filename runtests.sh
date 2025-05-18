#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run tests with coverage
run_tests() {
    echo -e "${BLUE}Running tests with coverage...${NC}"
    python -m pytest \
        --cov=ai \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-fail-under=80 \
        -v \
        "$@"
}

# Function to run specific test module
run_test_module() {
    echo -e "${BLUE}Running test module: $1${NC}"
    python -m pytest "$1" -v
}

# Function to run a specific test
run_specific_test() {
    echo -e "${BLUE}Running specific test: $1${NC}"
    python -m pytest "$1" -v -k "$2"
}

# Function to run tests with HTML report
generate_html_report() {
    echo -e "${BLUE}Generating HTML test report...${NC}"
    python -m pytest --html=test-report.html --self-contained-html "$@"
}

# Function to run tests in parallel
run_parallel_tests() {
    echo -e "${BLUE}Running tests in parallel...${NC}"
    python -m pytest -n auto "$@"
}

# Function to run tests with detailed debugging info
run_debug_tests() {
    echo -e "${BLUE}Running tests with debug output...${NC}"
    python -m pytest -v --log-level=DEBUG --pdb "$@"
}

# Function to show coverage report
show_coverage() {
    echo -e "${BLUE}Generating coverage report...${NC}"
    python -m coverage report -m
    python -m coverage html
    echo -e "${GREEN}Coverage report generated at htmlcov/index.html${NC}"
}

# Function to clean up
clean() {
    echo -e "${BLUE}Cleaning up...${NC}"
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -type d -name ".pytest_cache" -exec rm -r {} +
    rm -rf .coverage htmlcov/ .pytest_cache/ test-report.html
    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Main function
main() {
    case "$1" in
        module)
            shift
            run_test_module "$@"
            ;;
        test)
            shift
            if [ $# -lt 2 ]; then
                echo "Usage: $0 test <test_file.py> <test_function>"
                exit 1
            fi
            run_specific_test "$1" "$2"
            ;;
        html)
            shift
            generate_html_report "$@"
            ;;
        parallel)
            shift
            run_parallel_tests "$@"
            ;;
        debug)
            shift
            run_debug_tests "$@"
            ;;
        coverage)
            shift
            run_tests "$@"
            show_coverage
            ;;
        clean)
            clean
            ;;
        *)
            run_tests "$@"
            ;;
    esac
}

# Run the main function
main "$@"
