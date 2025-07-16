# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated CI/CD pipelines for the Stock Screener project.

## 🔄 Workflows Overview

### 1. **CI Pipeline** (`ci.yml`)
**Triggers**: Push/PR to main/master branches, manual dispatch

**Features**:
- ✅ **Multi-Python Testing**: Tests across Python 3.9, 3.10, 3.11, 3.12
- ✅ **Comprehensive Test Suite**: Unit tests with coverage reporting
- ✅ **Integration Testing**: End-to-end workflow validation
- ✅ **Performance Testing**: Performance benchmarks and health checks
- ✅ **Coverage Reporting**: Uploads to Codecov for tracking

**Jobs**:
- `test`: Main test suite with matrix strategy
- `test-performance`: Performance and health validation

### 2. **Docker Build & Test** (`docker.yml`)
**Triggers**: Push/PR to main/master, tags (v*), manual dispatch

**Features**:
- ✅ **Multi-Architecture Builds**: Docker Buildx for cross-platform support
- ✅ **Container Testing**: Health checks, basic functionality, market analysis
- ✅ **Security Scanning**: Trivy vulnerability scanning + Hadolint linting
- ✅ **Registry Publishing**: Pushes to GitHub Container Registry (GHCR)
- ✅ **Smart Caching**: GitHub Actions cache for faster builds

**Jobs**:
- `docker-build`: Build, test, and publish container images
- `docker-security`: Comprehensive security analysis

### 3. **Code Quality** (`code-quality.yml`)
**Triggers**: Push/PR to main/master branches, manual dispatch

**Features**:
- ✅ **Linting & Formatting**: Ruff, Black, isort validation
- ✅ **Type Checking**: MyPy static type analysis
- ✅ **Security Scanning**: Bandit, Safety dependency checks
- ✅ **Complexity Analysis**: Radon, Xenon code complexity metrics
- ✅ **Documentation**: Docstring coverage and style validation
- ✅ **Dependency Auditing**: pip-audit for vulnerability detection

**Jobs**:
- `linting`: Code style and formatting checks
- `type-checking`: Static type analysis
- `security-scan`: Security vulnerability detection
- `complexity-analysis`: Code complexity metrics
- `documentation`: Documentation quality checks
- `dependencies`: Dependency audit and analysis

## 🛠️ Configuration Files

### **pyproject.toml**
Centralized configuration for all tools:
- **Ruff**: Linting with pycodestyle, pyflakes, bugbear rules
- **Black**: Code formatting with 88-character line length
- **isort**: Import sorting compatible with Black
- **MyPy**: Type checking with reasonable strictness
- **Bandit**: Security scanning configuration
- **Coverage**: Test coverage reporting settings
- **pytest**: Test execution and coverage configuration

### **requirements.txt**
Updated with code quality tools:
```
# Core dependencies
pandas>=2.0.0
yfinance>=0.2.18
# ... existing dependencies

# Testing tools
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0

# Code quality tools
ruff>=0.1.0
black>=23.0.0
mypy>=1.5.0
isort>=5.12.0
bandit>=1.7.0
safety>=2.3.0
radon>=6.0.0
xenon>=0.9.0
pydocstyle>=6.3.0
interrogate>=1.5.0
pip-audit>=2.6.0
pipdeptree>=2.13.0
```

## 🚀 Workflow Execution

### **Automatic Triggers**
- **Every Push**: Runs CI and Code Quality checks
- **Every Pull Request**: Full validation including Docker builds
- **Version Tags**: Builds and publishes release containers
- **Manual**: All workflows can be triggered manually

### **Execution Matrix**
```yaml
CI Pipeline:
├── Python 3.9 → Unit + Integration Tests
├── Python 3.10 → Unit + Integration Tests  
├── Python 3.11 → Unit + Integration Tests
└── Python 3.12 → Unit + Integration Tests + Coverage

Docker Build:
├── Build & Cache → Test Health Check
├── Test Basic Functionality → Test Market Analysis
├── Security Scan → Publish (if not PR)
└── Hadolint Linting → Vulnerability Scan

Code Quality:
├── Ruff Linting → Black Formatting → isort
├── MyPy Type Checking
├── Bandit + Safety Security Scan
├── Radon + Xenon Complexity Analysis
├── Docstring Coverage + Style Check
└── Dependency Audit + Tree Analysis
```

## 📊 Reporting & Artifacts

### **Coverage Reports**
- **Codecov Integration**: Automatic coverage tracking
- **HTML Reports**: Generated in `htmlcov/` directory
- **Coverage Requirements**: Configured in pyproject.toml

### **Security Reports**
- **Trivy SARIF**: Uploaded to GitHub Security tab
- **Bandit JSON**: Security scan artifacts
- **Safety Reports**: Dependency vulnerability reports
- **pip-audit**: Comprehensive dependency auditing

### **Quality Metrics**
- **Complexity Analysis**: Radon cyclomatic complexity
- **Documentation Coverage**: Interrogate docstring analysis
- **Type Coverage**: MyPy type checking results
- **Dependency Tree**: pipdeptree visualization

## 🔒 Security Features

### **Container Security**
- **Trivy Scanning**: Comprehensive vulnerability detection
- **Hadolint**: Dockerfile best practices validation
- **Multi-stage Analysis**: Security at build and runtime

### **Code Security**
- **Bandit**: Python security issue detection
- **Safety**: Known vulnerability database checking
- **pip-audit**: OSV database vulnerability scanning

### **Registry Security**
- **GHCR Integration**: GitHub Container Registry
- **Automatic Tagging**: Semantic version + SHA tagging
- **Access Control**: GitHub token-based authentication

## 🎯 Quality Gates

### **Required Checks**
- ✅ All tests must pass across Python versions
- ✅ Code formatting must be consistent (Black)
- ✅ Import sorting must be proper (isort)
- ✅ Linting must pass (Ruff)
- ✅ Security scans must not find critical issues
- ✅ Docker builds must succeed and pass health checks

### **Advisory Checks** (continue-on-error: true)
- 📊 Type checking (MyPy) - reports issues but doesn't fail
- 📊 Complexity analysis - provides metrics for review
- 📊 Documentation coverage - tracks improvements needed
- 📊 Security scanning - reports for review

## 🔧 Local Development

### **Run Code Quality Checks Locally**
```bash
# Install tools
pip install -r requirements.txt

# Run formatting
python -m black src/ tests/
python -m isort src/ tests/

# Run linting
python -m ruff check src/ tests/

# Run type checking
python -m mypy src/

# Run security scan
python -m bandit -r src/

# Run tests with coverage
python run_tests.py --coverage
```

### **Test Docker Build Locally**
```bash
# Build image
docker build -t stock-screener:test .

# Test health check
docker run --rm stock-screener:test --health-check

# Test basic functionality
docker run --rm stock-screener:test --symbols AAPL --quiet
```

## 📈 Benefits

### **Development Quality**
- **Consistent Code Style**: Automated formatting and linting
- **Type Safety**: Static type checking for better reliability
- **Security Awareness**: Automated vulnerability detection
- **Performance Monitoring**: Complexity and performance metrics

### **Deployment Confidence**
- **Multi-Environment Testing**: Validates across Python versions
- **Container Validation**: Ensures Docker deployment works
- **Security Assurance**: Comprehensive security scanning
- **Automated Publishing**: Streamlined release process

### **Team Productivity**
- **Fast Feedback**: Quick validation on every change
- **Quality Gates**: Prevents problematic code from merging
- **Documentation**: Automated documentation quality checks
- **Dependency Management**: Proactive vulnerability detection 