# Kobidh - Container Deployment Automation Tool

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Qurtesy/kobidh)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-CloudFormation%20%7C%20ECS%20%7C%20ECR-orange.svg)](https://aws.amazon.com)

Kobidh is a powerful CLI tool for automating containerized application deployment on AWS, similar to Heroku but with full infrastructure control. It manages the complete lifecycle from infrastructure provisioning to container deployment using AWS services like ECS, ECR, and CloudFormation.

## 🚀 Features

- **One-Command Deployment**: Deploy applications with simple CLI commands
- **Infrastructure as Code**: Automated VPC, ECS, ECR, and IAM setup using CloudFormation
- **Container Management**: Build, push, and deploy Docker containers seamlessly
- **Auto-scaling**: Built-in auto-scaling based on CPU and memory metrics
- **Multi-Environment**: Support for development, staging, and production environments
- **Monitoring**: Integrated CloudWatch monitoring and logging

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Docker (for container operations)

### Install from Source

```bash
git clone https://github.com/Qurtesy/kobidh.git
cd kobidh
pip install -e .
```

### Verify Installation

```bash
kobidh --help
```

## 🛠️ Quick Start

### 1. Initial Setup

```bash
# Configure Kobidh with your AWS settings
kobidh setup
```

This will prompt you for:
- Application name
- AWS region
- AWS profile (optional)

### 2. Create Your First Application

```bash
# Create application infrastructure
kobidh apps create my-web-app

# Check application status
kobidh apps info my-web-app
```

### 3. Deploy a Service

```bash
# Create and deploy a service
kobidh service create my-web-app

# Push container to registry
kobidh container push my-web-app
```

## 📚 Documentation

### Commands Reference

#### Core Commands
- `kobidh setup` - Initial configuration
- `kobidh show` - Display current configuration

#### Application Management
- `kobidh apps create <name>` - Create new application infrastructure
- `kobidh apps info <name>` - Show application details
- `kobidh apps describe <name>` - Show CloudFormation stack details
- `kobidh apps delete <name>` - Delete application and all resources

#### Service Management
- `kobidh service create <name>` - Create ECS service
- `kobidh service delete <name>` - Delete ECS service

#### Container Operations
- `kobidh container push <name>` - Build and push container to ECR

## 🏗️ Architecture

Kobidh creates and manages the following AWS resources:

### Infrastructure Layer
- **VPC**: Isolated network with public and private subnets
- **Internet Gateway**: Internet access for public resources
- **Security Groups**: Network access control
- **IAM Roles**: Service permissions and access control

### Container Layer
- **ECR Repository**: Docker container registry
- **ECS Cluster**: Container orchestration platform
- **ECS Services**: Running container services with auto-scaling
- **Application Load Balancer**: Traffic distribution (optional)

### Monitoring Layer
- **CloudWatch Logs**: Centralized logging
- **CloudWatch Metrics**: Performance monitoring
- **CloudWatch Alarms**: Automated alerting (optional)

## ⚙️ Configuration

Kobidh stores configuration in `~/.kobidh/default.txt`:

```
app:my-web-app
region:us-east-1
```

### Environment Variables

- `AWS_DEFAULT_REGION` - Default AWS region
- `AWS_PROFILE` - AWS profile to use
- `KOBIDH_CONFIG` - Custom configuration file path

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Qurtesy/kobidh.git
cd kobidh

# Install dependencies
pip install -r _requirements/dev.txt

# Install in development mode
pip install -e .
```

### Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=kobidh
```

### Project Structure

```
kobidh/
├── kobidh/                 # Main package
│   ├── cli.py             # CLI interface
│   ├── core.py            # Core functionality
│   ├── resource/          # AWS resource management
│   └── utils/             # Utility functions
├── docs/                  # Documentation
├── tests/                 # Test files
└── _requirements/         # Dependency files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Troubleshooting

### Common Issues

**AWS Credentials Not Found**
```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

**CloudFormation Stack Creation Failed**
- Check AWS CloudFormation console for detailed error messages
- Ensure you have sufficient IAM permissions
- Verify your account limits for resources

**Container Push Failed**
- Ensure Docker is running
- Check ECR repository exists and you have push permissions
- Verify AWS CLI is configured correctly

### Getting Help

- Check the [documentation](docs/)
- Search [existing issues](https://github.com/Qurtesy/kobidh/issues)
- Create a [new issue](https://github.com/Qurtesy/kobidh/issues/new)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS for providing excellent cloud infrastructure services
- The Python community for amazing open-source tools
- All contributors who help improve this project

---

**Made with ❤️ by [Souvik Dey](https://github.com/dsouvik141)**
