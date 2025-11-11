# TPath Test Structure

This directory contains modular tests that match the structure of the TPath class files.

## Test Organization

The test structure mirrors the modular organization of the TPath source code:

```
test/
├── test_core.py        # Tests for _core.py (TPath class, pathlib compatibility)
├── test_age.py         # Tests for _age.py (Age calculations)
├── test_size.py        # Tests for _size.py (Size calculations and parsing)
├── test_time.py        # Tests for _time.py (Time properties)
├── test_integration.py # Integration tests (all modules working together)
├── run_all_tests.py    # Test runner for all modules
└── README.md           # This file
```

## Running Tests

### Run All Modular Tests

```bash
python test/run_all_tests.py
```

### Run Individual Test Modules

```bash
python test/test_core.py        # Core TPath functionality
python test/test_age.py         # Age calculation tests
python test/test_size.py        # Size calculation tests
python test/test_time.py        # Time property tests
python test/test_integration.py # Integration tests
```

## Test Categories

### Core Tests (`test_core.py`)

- TPath object creation and initialization
- Pathlib compatibility verification
- Convenience function testing
- Property access validation

### Age Tests (`test_age.py`)

- Age property calculations (seconds, minutes, hours, days, weeks, months, years)
- Custom base time functionality
- Time progression verification
- Different time types (ctime, mtime, atime)

### Size Tests (`test_size.py`)

- Size property calculations (bytes, KB/KiB, MB/MiB, etc.)
- Size string parsing (`Size.fromstr()`)
- Error handling for invalid size strings
- Edge cases (zero size, very large sizes)
- Size comparisons

### Time Tests (`test_time.py`)

- Time property functionality (ctime, mtime, atime)
- Timestamp and datetime access
- Custom base time with different time types
- Nonexistent file handling

### Integration Tests (`test_integration.py`)

- Complete workflow testing
- File operations with TPath features
- Pathlib compatibility in real scenarios
- Custom base time integration scenarios

## Test Design Principles

1. **Modular**: Each test file focuses on one specific module
2. **Independent**: Tests can run individually without dependencies
3. **Comprehensive**: Each module is thoroughly tested
4. **Clear**: Tests have descriptive names and clear assertions
5. **Clean**: Tests clean up after themselves (delete test files)

## Benefits of Modular Test Structure

- **Easier Debugging**: When a test fails, you know exactly which module has issues
- **Faster Development**: Run only the tests for the module you're working on
- **Better Organization**: Test structure matches code structure
- **Maintainable**: Easy to add new tests for specific functionality
- **Clear Coverage**: Easy to see what functionality is tested

## Test Output

Each test module provides clear output showing:

- ✅ Passed tests with descriptive messages
- ❌ Failed tests with error details
- Test data and results for verification
- Summary of all tests in the module

The main test runner (`run_all_tests.py`) provides:

- Progress for each test module
- Overall summary of passed/failed modules
- Clear indication of any issues
