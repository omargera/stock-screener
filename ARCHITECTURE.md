# Stock Screener Architecture

## Overview

The Stock Screener has been refactored from a monolithic single-file application into a clean, maintainable layered architecture following software engineering best practices.

## Architecture Layers

### 1. Presentation Layer
- **File**: `main.py`
- **Purpose**: Entry point with command-line interface and user interaction
- **Responsibilities**:
  - Argument parsing and validation
  - Application configuration
  - User interface orchestration
  - Error handling and exit codes

### 2. Service Layer (Business Logic)
- **Directory**: `services/`
- **Purpose**: Core business logic and domain operations

#### Components:
- **`screener_service.py`**: Main orchestration service
  - Coordinates all screening operations
  - Manages configuration and dependencies
  - Provides high-level screening APIs
  
- **`technical_analysis_service.py`**: Technical indicator calculations
  - Moving averages (SMA, EMA)
  - Volume indicators (OBV, Volume MA)
  - Volatility measures (ATR, Price Volatility)
  - Support/Resistance levels
  
- **`signal_detection_service.py`**: Signal identification logic
  - Breakout pattern detection
  - Volume spike identification
  - Signal quality analysis

### 3. Model Layer (Data Structures)
- **Directory**: `models/`
- **Purpose**: Data representation and domain entities

#### Components:
- **`stock.py`**: Stock data models
  - `StockPrice`: Current price information
  - `TechnicalIndicators`: Calculated indicators
  - `StockData`: Complete stock data container
  
- **`signals.py`**: Signal models
  - `BreakoutSignal`: Breakout pattern information
  - `VolumeSignal`: Volume spike information
  - `CombinedSignals`: Container for all signals
  
- **`screening_result.py`**: Result models
  - `ScreeningResult`: Single stock result
  - `ScreeningResults`: Collection with analysis capabilities

### 4. Gateway Layer (External Data Access)
- **Directory**: `gateways/`
- **Purpose**: External API integration and data fetching

#### Components:
- **`stock_data_gateway.py`**: Data access abstraction
  - `StockDataGateway`: Abstract base class
  - `YahooFinanceGateway`: Yahoo Finance implementation
  - Data validation and quality checks
  - Connection testing capabilities

### 5. Utility Layer (Cross-cutting Concerns)
- **Directory**: `utils/`
- **Purpose**: Common utilities and infrastructure

#### Components:
- **`display.py`**: Result presentation and formatting
  - Formatted console output
  - Progress indicators
  - Error message display
  - Market analysis presentation
  
- **`logging_config.py`**: Logging infrastructure
  - Centralized logging configuration
  - Multiple output formats
  - Performance and audit logging
  - Environment-specific setups

## Design Principles

### 1. Separation of Concerns
Each layer has a single, well-defined responsibility:
- **Presentation**: User interface and input/output
- **Service**: Business logic and algorithms
- **Model**: Data representation
- **Gateway**: External integrations
- **Utility**: Cross-cutting concerns

### 2. Dependency Inversion
- High-level modules don't depend on low-level modules
- Services depend on abstractions (interfaces) not implementations
- Easy to mock and test individual components

### 3. Single Responsibility Principle
- Each class has one reason to change
- Services are focused on specific domains
- Models represent single concepts

### 4. Open/Closed Principle
- Easy to extend with new signal types
- New data sources can be added via gateway interface
- Display formats can be extended without changing core logic

## Key Improvements

### 1. Maintainability
- Clear separation makes code easier to understand
- Changes to one layer don't affect others
- Easier to locate and fix bugs

### 2. Testability
- Each component can be tested in isolation
- Dependency injection allows for mocking
- Clear interfaces make unit testing straightforward

### 3. Extensibility
- New signal types: Add to signal detection service
- New data sources: Implement gateway interface
- New indicators: Extend technical analysis service
- New output formats: Extend display service

### 4. Scalability
- Services can be optimized independently
- Caching can be added at gateway layer
- Parallel processing can be implemented in services

## Configuration Management

### ScreenerConfiguration Class
Centralizes all configuration parameters:
- Data period settings
- Signal thresholds
- Algorithm parameters
- Easy to extend and validate

## Error Handling Strategy

### Layered Error Handling
- **Gateway Layer**: Network and data errors
- **Service Layer**: Business logic errors
- **Presentation Layer**: User-friendly error messages
- **Logging**: Comprehensive error tracking

## Performance Considerations

### Efficient Data Flow
1. Data fetched once per stock (Gateway)
2. Indicators calculated once (Technical Analysis)
3. Signals detected efficiently (Signal Detection)
4. Results formatted for display (Display)

### Caching Opportunities
- Gateway layer can cache recent data
- Technical indicators can be cached
- Signal calculations can be optimized

## Future Enhancements

### Easy Extensions
1. **New Signal Types**: Add to signal detection service
2. **Machine Learning**: New service for ML-based signals
3. **Real-time Data**: WebSocket gateway implementation
4. **Web Interface**: New presentation layer
5. **Database Storage**: Persistence gateway
6. **Alert System**: Notification service

### Microservices Ready
The layered architecture can easily be converted to microservices:
- Each service becomes a separate service
- Gateways become API clients
- Models become shared contracts
- Communication via REST/gRPC

## Dependencies

### External Dependencies
- `pandas`: Data manipulation
- `yfinance`: Yahoo Finance API
- `numpy`: Numerical computations

### Internal Dependencies
- Services depend on models and gateways
- Main depends on services and utilities
- Clear dependency graph prevents cycles

## Testing Strategy

### Unit Testing
- Each service can be tested independently
- Models can be tested for data integrity
- Gateways can be mocked for testing

### Integration Testing
- Test service interactions
- Test data flow between layers
- Test complete screening scenarios

### System Testing
- End-to-end screening tests
- Performance benchmarking
- Error scenario testing

## Deployment

### Docker Support
- Multi-stage builds possible
- Each layer can be optimized separately
- Easy to create different deployment configs

### Environment Flexibility
- Configuration-driven behavior
- Easy to switch between dev/prod
- Logging levels per environment

This architecture provides a solid foundation for a production-ready stock screening application that can grow and evolve with changing requirements. 