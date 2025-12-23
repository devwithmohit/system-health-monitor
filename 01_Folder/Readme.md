# System Health Monitor

A comprehensive system health monitoring solution with multiple implementation levels, demonstrating production-ready patterns including idempotency, state management, and real-time alerting capabilities.

## 📋 Description

This project provides a robust health monitoring system for web services and APIs. It includes four progressive implementations that showcase different levels of complexity and features, from basic health checks to advanced Slack integration with response time monitoring.

## 🚀 Technologies Used

- **Python 3.7+**
- **Requests** - HTTP client library
- **JSON** - Configuration and state management
- **Logging** - Comprehensive logging system
- **Slack Webhooks** - Real-time alerting
- **python-dotenv** - Environment variable management

## ✨ Features

### Core Features (All Levels)

- ✅ HTTP endpoint health checking
- ✅ Idempotent alert system (no duplicate alerts)
- ✅ Persistent state management
- ✅ Comprehensive logging
- ✅ Configurable alert thresholds

### Advanced Features (Level 2-4)

- 🌐 Multiple HTTP methods support (GET, POST, PUT)
- ⏱️ Response time monitoring with SLA thresholds
- 📊 Enhanced state tracking
- 🔔 Slack webhook integration for real-time alerts
- 🎨 Rich Slack message formatting with colors and fields

### Enterprise Features (Level 4)

- 🔧 Environment-based configuration
- 📈 Production-ready alert patterns
- 🎯 Smart alert recovery detection
- 📱 Professional Slack notifications with emojis

## 📁 Project Structure

```
01_Folder/
├── 01_project.py          # Level 1: Basic health monitoring
├── 02_project.py          # Level 2: HTTP methods + enhanced state
├── 03_project.py          # Level 3: Response time monitoring
├── 04_project.py          # Level 4: Slack integration (Production)
├── .env                   # Environment configuration
├── requirements.txt       # Python dependencies
├── servers.json          # Server configuration (auto-generated)
├── state.json            # Monitoring state (auto-generated)
└── health_monitor.log    # Application logs (auto-generated)
```

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd 01_Folder
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your Slack webhook URL and preferences
   ```

4. **Set up Slack webhook (for Level 4)**
   - Go to your Slack workspace
   - Create a new Incoming Webhook
   - Copy the webhook URL to your `.env` file

## 🎯 Usage

### Quick Start (Any Level)

```bash
# Run basic health monitor
python 01_project.py

# Run with HTTP methods support
python 02_project.py

# Run with response time monitoring
python 03_project.py

# Run production version with Slack alerts
python 04_project.py
```

### Configuration

#### Environment Variables (.env)

```bash
SERVERS_FILE="servers.json"
STATE_FILE="state.json"
LOG_FILE="health_monitor.log"
ALERT_THRESHOLD=2
MAX_RESPONSE_TIME=2.0
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
SLACK_USERNAME="Health Monitor"
SLACK_ICON_EMOJI=":warning:"
```

#### Server Configuration (servers.json)

```json
[
  {
    "name": "API Health Check",
    "url": "https://api.example.com/health",
    "method": "GET"
  },
  {
    "name": "User Service",
    "url": "https://api.example.com/users",
    "method": "POST",
    "payload": { "test": true }
  }
]
```

### Automated Monitoring

Set up as a cron job for continuous monitoring:

```bash
# Check every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/04_project.py
```

## 📊 Features by Implementation Level

| Feature                  | Level 1 | Level 2 | Level 3 | Level 4 |
| ------------------------ | ------- | ------- | ------- | ------- |
| Basic Health Checks      | ✅      | ✅      | ✅      | ✅      |
| State Management         | ✅      | ✅      | ✅      | ✅      |
| HTTP Methods             | ❌      | ✅      | ✅      | ✅      |
| Response Time Monitoring | ❌      | ❌      | ✅      | ✅      |
| Slack Integration        | ❌      | ❌      | ❌      | ✅      |
| Environment Config       | ❌      | ❌      | ❌      | ✅      |

## 🔍 Monitoring Output

The system provides detailed logging and state tracking:

```
2024-12-23 10:30:15 - INFO - UP: API Health Check [GET] 0.45s
2024-12-23 10:30:16 - INFO - SLOW: User Service [POST] 2.3s
2024-12-23 10:30:17 - ERROR - DOWN: Payment API [GET] 5.0s
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive logging
- Include error handling for all external calls
- Update documentation for new features
- Test with various HTTP endpoints

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Slack alerts not working:**

- Verify `SLACK_WEBHOOK_URL` in `.env`
- Test webhook URL manually
- Check Slack workspace permissions

**State file corruption:**

- Delete `state.json` - it will be recreated
- Check file permissions

**High response times:**

- Adjust `MAX_RESPONSE_TIME` in `.env`
- Check network connectivity
- Verify target server performance

## 🙏 Acknowledgments

- Built with production patterns for enterprise monitoring
- Inspired by industry-standard health check practices
- Designed for scalability and maintainability

---

**Ready to monitor your services like a pro? Start with Level 1 and progress through the implementations!** 🚀
