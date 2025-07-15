# Stock Screener Test Suite

Comprehensive test suite for the stock screener application, ensuring reliable signal detection and accurate entry point identification.

## 🧪 Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_technical_analysis_service.py
│   └── test_signal_detection_service.py
├── integration/                    # Integration tests for complete workflows
│   ├── test_complete_screening.py
│   └── test_signal_accuracy.py
├── utils/                         # Test utilities and fixtures
│   ├── test_data_generator.py
│   └── fixtures.py
└── data/                          # Generated test data scenarios
    ├── resistance_breakout.csv
    ├── ma_breakout.csv
    ├── volume_spike.csv
    ├── no_signal.csv
    └── false_breakout.csv
```

## 🚀 Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage
```

### Test Categories

```bash
# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration

# Fast tests (skip slow ones)
python run_tests.py --fast

# Verbose output
python run_tests.py --verbose
```

### Advanced Options

```bash
# Run specific test pattern
python run_tests.py -k "test_resistance_breakout"

# Run tests with markers
python run_tests.py -m "not slow"

# Parallel execution
python run_tests.py --parallel
```

## 📊 Test Coverage

The test suite covers:

### **Unit Tests**
- **Technical Analysis Service** (85+ test cases)
  - Moving average calculations (SMA, EMA)
  - Volume indicators (OBV, Volume MA)
  - Support/resistance levels
  - Volatility measures (ATR, Price volatility)
  - Data integrity and error handling

- **Signal Detection Service** (70+ test cases)
  - Resistance breakout detection
  - Moving average breakout detection
  - Volume spike identification
  - False breakout rejection
  - Signal strength calculations
  - Configuration impact testing

### **Integration Tests**
- **Complete Screening Workflow** (40+ test cases)
  - End-to-end screening process
  - Multiple stock analysis
  - Market condition assessment
  - Error handling and recovery
  - Performance validation

- **Signal Accuracy** (30+ test cases)
  - Entry point identification
  - Pattern recognition accuracy
  - Timing precision
  - Risk assessment
  - Market condition detection

## 🎯 Test Scenarios

### **Sample Data Scenarios**

1. **Resistance Breakout**: Clear resistance level with volume-confirmed breakout
2. **MA Breakout**: Moving average crossover with trend confirmation
3. **Volume Spike**: Unusual volume activity without price breakout
4. **No Signal**: Normal trading with no significant patterns
5. **False Breakout**: Brief price spike without proper confirmation

### **Signal Detection Tests**

#### ✅ **Should Detect Signals**
- Resistance breakout with 3x+ volume spike
- MA crossover in uptrend with volume confirmation
- Clear volume spikes (2x+ average volume)
- Multiple signal combinations

#### ❌ **Should NOT Detect Signals**
- False breakouts (low volume, closing below resistance)
- MA breakouts in downtrends
- Volume spikes below threshold
- Insufficient data scenarios

### **Entry Point Validation**

Tests verify the screener identifies optimal entry points by checking:

- **Signal Timing**: Detected at the right moment (not too early/late)
- **Volume Confirmation**: Adequate volume support for price movements
- **Trend Confirmation**: Proper trend context for breakouts
- **Risk Assessment**: Signal quality and reliability scoring
- **Pattern Recognition**: Accurate identification of chart patterns

## 🔧 Test Configuration

### **Fixture Configuration**
```python
# Standard configuration
ScreenerConfiguration(
    period="3mo",
    volume_spike_threshold=2.0,
    breakout_threshold=0.02
)

# Strict configuration for edge case testing
ScreenerConfiguration(
    period="3mo", 
    volume_spike_threshold=3.0,
    breakout_threshold=0.05
)
```

### **Mock Data Gateway**
- Maps test symbols to specific scenarios
- `TEST_RESISTANCE` → Resistance breakout data
- `TEST_MA` → Moving average breakout data
- `TEST_VOLUME` → Volume spike data
- `TEST_NONE` → No signal data
- `TEST_FALSE` → False breakout data

## 📈 Performance Testing

### **Performance Benchmarks**
- Technical indicator calculation: < 1 second for 1000 data points
- Signal detection: < 0.1 seconds per stock
- Complete screening: < 5 seconds for 20 stocks
- Memory usage: Reasonable for large datasets

### **Scalability Tests**
- Large dataset handling (1000+ days)
- Multiple stock screening (20+ stocks)
- Concurrent processing validation
- Memory efficiency verification

## 🛡️ Error Handling Tests

### **Edge Cases Covered**
- Empty/insufficient data
- Malformed data structures
- Network/API failures
- Invalid configuration parameters
- Zero volume scenarios
- Extreme price movements

### **Graceful Degradation**
- Failed data fetching
- Calculation errors
- Service unavailability
- Invalid input handling

## 📋 Test Validation Criteria

### **Signal Accuracy Requirements**
- **Resistance Breakouts**: Must have volume confirmation (>1.2x average)
- **MA Breakouts**: Require uptrend confirmation (SMA 20 > SMA 50)
- **Volume Spikes**: Must exceed configurable threshold (default 2x)
- **False Positives**: Maximum 5% false positive rate acceptable
- **Signal Timing**: Must detect within 1 trading day of actual breakout

### **Performance Requirements**
- **Response Time**: Technical analysis < 1s, Signal detection < 0.1s
- **Memory Usage**: Reasonable memory footprint for dataset sizes
- **Scalability**: Linear performance scaling with data size
- **Reliability**: 99%+ success rate for valid data

## 🔍 Debugging Tests

### **Test Data Inspection**
```bash
# Generate and inspect test data
cd tests/utils
python test_data_generator.py

# View generated scenarios
ls tests/data/*.csv
```

### **Individual Test Debugging**
```bash
# Run specific test with verbose output
python run_tests.py -k "test_resistance_breakout" --verbose

# Run with debugging breakpoints
python -m pytest tests/unit/test_signal_detection_service.py::TestSignalDetectionService::test_resistance_breakout_detection -v -s
```

### **Test Data Builder**
```python
# Create custom test scenarios
data = (data_builder("TEST", 100.0)
        .with_basic_data(60)
        .with_resistance_at(110.0, 30, 55)
        .with_breakout_on_day(56, 112.0, 3.0)
        .build())
```

## 🎯 Assertion Helpers

### **Signal Validation**
```python
# Test signal detection
assert_signal_detected(result, "breakout")
assert_signal_detected(result, "volume") 
assert_signal_detected(result, "any")

# Test no signals
assert_no_signals(result)

# Test signal strength
assert_signal_strength(result, min_strength=0.02)
assert_volume_ratio(result, min_ratio=2.0)
```

## 🔄 Continuous Integration

### **CI Pipeline Tests**
```bash
# Quick validation (for PR checks)
python run_tests.py --fast --unit

# Full validation (for releases)
python run_tests.py --coverage --verbose

# Performance validation
python run_tests.py -k "performance" --verbose
```

### **Test Reporting**
- Coverage reports: `htmlcov/index.html`
- JUnit XML: For CI integration
- Performance metrics: Execution time tracking
- Signal accuracy: False positive/negative rates

## 🛠️ Adding New Tests

### **Test Development Guidelines**

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Use Fixtures**: Leverage existing test utilities
4. **Clear Assertions**: Use descriptive assertion messages
5. **Performance Awareness**: Mark slow tests appropriately

### **Example Test Structure**
```python
def test_new_signal_detection(self, data_builder):
    """Test description"""
    # Arrange
    data = data_builder("TEST", 100.0).with_custom_pattern().build()
    
    # Act
    signals = self.service.detect_all_signals(data)
    
    # Assert
    assert signals.breakout.signal, "Should detect breakout"
    assert signals.breakout.strength > 0.02, "Strength should be significant"
```

## 📚 Resources

- **pytest Documentation**: https://docs.pytest.org/
- **Test Coverage**: Coverage.py documentation
- **Mock Objects**: unittest.mock documentation
- **Performance Testing**: pytest-benchmark plugin

## 🤝 Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Maintain coverage** above 85%
3. **Add integration tests** for new workflows
4. **Update test documentation**
5. **Validate signal accuracy** with real market scenarios

---

For questions about testing, see the main project documentation or create an issue in the repository. 