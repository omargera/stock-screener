# Stock Screener with Docker

A Python-based stock screener that identifies breakout patterns and volume spikes in stock data, containerized with Docker for easy deployment.

## 🚀 Features

- **Breakout Detection**: Identifies resistance breakouts and moving average breakouts
- **Volume Spike Detection**: Detects unusual volume activity (configurable threshold)
- **Technical Indicators**: Calculates moving averages, support/resistance levels, and volatility
- **Real-time Data**: Fetches live stock data using Yahoo Finance API
- **Docker Support**: Fully containerized for consistent deployment
- **Professional Logging**: Structured logging for monitoring and debugging
- **Customizable**: Configurable thresholds and screening parameters
- **Layered Architecture**: Clean separation of concerns for maintainability
- **Command-Line Interface**: Rich CLI with multiple operating modes

## 📋 Requirements

- Docker (for containerized deployment)
- OR Python 3.12+ (for local development)

## 🛠️ Quick Start with Docker

### 1. Clone and Build

```bash
# Make the Docker script executable
chmod +x docker_commands.sh

# Build and run the container
./docker_commands.sh
```

### 2. Manual Docker Commands

```bash
# Build the Docker image
docker build -t stock-screener:latest .

# Run the container
docker run --rm stock-screener:latest

# Run interactively (for debugging)
docker run --rm -it stock-screener:latest bash
```

## 🐍 Local Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Screener

```bash
# Basic screening
cd src && python main.py
# Or from root: PYTHONPATH=src python src/main.py

# Screen specific stocks
cd src && python main.py --symbols AAPL MSFT GOOGL

# Market analysis mode
cd src && python main.py --mode market-analysis

# Top opportunities
cd src && python main.py --mode top-opportunities --limit 5

# Health check
cd src && python main.py --health-check
```

## 📊 How It Works

### Breakout Detection

The screener identifies two types of breakouts:

1. **Resistance Breakout**: Price breaks above the 20-day resistance level
   - Requires volume confirmation (>1.2x average volume)
   - Configurable breakout threshold (default: 2%)

2. **Moving Average Breakout**: Price breaks above the 20-day SMA
   - Requires uptrend confirmation (SMA 20 > SMA 50)
   - Volume confirmation recommended

### Volume Spike Detection

- Compares current volume to 20-day average volume
- Default threshold: 2.0x (200% of average volume)
- Configurable via `volume_spike_threshold` parameter

### Technical Indicators

- **SMA 20/50**: Simple Moving Averages for trend analysis
- **Support/Resistance**: 20-day rolling min/max levels
- **Volume MA**: 20-day average volume for spike detection
- **Price Volatility**: 20-day standard deviation

## ⚙️ Configuration

### Command Line Options

```bash
# Basic parameters
python main.py --period 6mo --volume-threshold 3.0 --breakout-threshold 0.03

# Stock selection
python main.py --symbols AAPL MSFT GOOGL AMZN TSLA

# Operating modes
python main.py --mode market-analysis
python main.py --mode top-opportunities --limit 3
python main.py --mode signals-only

# Output options
python main.py --quiet           # Minimal output
python main.py --verbose         # Debug output
python main.py --log-file mylog.txt  # Log to file
```

### Available Parameters

- `--period`: Data timeframe (1mo, 3mo, 6mo, 1y, 2y, 5y)
- `--volume-threshold`: Volume spike multiplier (default: 2.0)
- `--breakout-threshold`: Breakout percentage threshold (default: 0.02)
- `--symbols`: Specific stocks to screen
- `--mode`: Operating mode (screen, market-analysis, top-opportunities, signals-only)
- `--limit`: Number of results in top-opportunities mode
- `--quiet`: Minimal output
- `--verbose`: Detailed debug output

## 📈 Sample Output

```
🔍 Starting Stock Screener...
Screening 15 stocks for breakouts and volume spikes...

================================================================================
 STOCK SCREENING RESULTS
================================================================================

🚨 STOCKS WITH SIGNALS (3 found):
--------------------------------------------------------------------------------

📈 TSLA
   Price: $248.50 (+2.15%)
   Volume: 89,234,567 (Avg: 45,123,890)
   🔥 BREAKOUT: Resistance Breakout (Strength: 3.25%)
   📊 VOLUME SPIKE: 2.0x average

📈 NVDA
   Price: $875.30 (+1.89%)
   Volume: 78,456,123 (Avg: 35,678,901)
   📊 VOLUME SPIKE: 2.2x average

📈 AMD
   Price: $142.75 (+0.95%)
   Volume: 45,789,012 (Avg: 23,456,789)
   🔥 BREAKOUT: MA Breakout (Strength: 1.85%)

📊 SUMMARY:
   Total stocks screened: 15
   Stocks with breakout signals: 2
   Stocks with volume spikes: 2
   Screening completed at: 2024-01-15 14:30:25
================================================================================
```

## 🔧 Troubleshooting

### Common Issues

1. **No data found for symbol**: Check if the stock symbol is valid and traded
2. **Network errors**: Ensure internet connection for Yahoo Finance API
3. **Docker build fails**: Check Docker installation and permissions

### Debug Mode

Run with verbose logging:

```python
# In stock_screener.py, change logging level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 📚 Dependencies

- **pandas**: Data manipulation and analysis
- **yfinance**: Yahoo Finance API for stock data
- **numpy**: Numerical computations
- **matplotlib**: Plotting (for future chart features)
- **seaborn**: Statistical visualization
- **requests**: HTTP requests
- **python-dateutil**: Date parsing utilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. It is not financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## 🏗️ Architecture

The application follows a clean layered architecture:

- **Presentation Layer** (`main.py`): CLI interface and user interaction
- **Service Layer** (`services/`): Business logic and orchestration
- **Model Layer** (`models/`): Data structures and domain entities
- **Gateway Layer** (`gateways/`): External API integration
- **Utility Layer** (`utils/`): Cross-cutting concerns (logging, display)

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

### Key Benefits
- **Maintainable**: Clear separation of concerns
- **Testable**: Each layer can be tested independently
- **Extensible**: Easy to add new features and data sources
- **Scalable**: Can be converted to microservices if needed

## 🔮 Future Enhancements

- [ ] Web dashboard with real-time updates
- [ ] Email/SMS alerts for detected signals
- [ ] More sophisticated technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Machine learning-based pattern recognition
- [ ] Historical backtesting capabilities
- [ ] Integration with trading APIs
- [ ] Custom screener strategies
- [ ] Performance metrics and analytics 