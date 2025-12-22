"""
System Health Monitor - Production Pattern
Demonstrates: Idempotency, State Management, Error Handling
"""

import json
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
SERVERS_FILE = "servers.txt"
STATE_FILE = "state.json"
LOG_FILE = "health_monitor.log"
ALERT_THRESHOLD = 2  # Alert after 2 consecutive failures

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)


class HealthMonitor:
    def __init__(self):
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """Load previous check results (idempotency key)"""
        if Path(STATE_FILE).exists():
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_state(self):
        """Persist state for next run"""
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_servers(self) -> List[str]:
        """Load server list from config file"""
        if not Path(SERVERS_FILE).exists():
            # Create example file
            example_servers = [
                "https://httpbin.org/status/200",
                "https://httpbin.org/status/500",
                "https://example.com",
            ]
            with open(SERVERS_FILE, "w") as f:
                f.write("\n".join(example_servers))
            logging.info(f"Created example {SERVERS_FILE}")
            return example_servers

        with open(SERVERS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def check_server(self, url: str) -> bool:
        """Check if server responds (with timeout)"""
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except requests.RequestException as e:
            logging.warning(f"Server check failed for {url}: {e}")
            return False

    def should_alert(self, url: str, is_down: bool) -> bool:
        """
        Idempotent alert logic:
        - Only alert if down for ALERT_THRESHOLD consecutive checks
        - Don't re-alert if already alerted
        """
        if url not in self.state:
            self.state[url] = {
                "consecutive_failures": 0,
                "last_alert_sent": None,
                "last_status": "unknown",
            }

        if is_down:
            self.state[url]["consecutive_failures"] += 1
            failures = self.state[url]["consecutive_failures"]

            # Alert if threshold reached AND we haven't alerted yet
            if failures >= ALERT_THRESHOLD and not self.state[url]["last_alert_sent"]:
                self.state[url]["last_alert_sent"] = datetime.now().isoformat()
                return True
        else:
            # Server recovered - reset counters
            if self.state[url]["consecutive_failures"] > 0:
                logging.info(f"✅ Server recovered: {url}")
            self.state[url]["consecutive_failures"] = 0
            self.state[url]["last_alert_sent"] = None

        return False

    def send_alert(self, url: str):
        """Send alert (email, Slack, PagerDuty, etc.)"""
        message = f"🚨 ALERT: Server {url} has been down for {ALERT_THRESHOLD}+ checks"
        logging.error(message)

        # In production, integrate with:
        # - Email: smtplib
        # - Slack: requests.post(webhook_url)
        # - PagerDuty: pypd library
        # - Telegram: python-telegram-bot

        print(f"\n{'=' * 60}")
        print(message)
        print(f"{'=' * 60}\n")

    def run(self):
        """Main monitoring loop"""
        logging.info("Starting health check run...")
        servers = self.load_servers()

        for url in servers:
            is_up = self.check_server(url)
            status = "UP" if is_up else "DOWN"

            logging.info(f"{status}: {url}")

            # Check if we should alert
            if self.should_alert(url, not is_up):
                self.send_alert(url)

            # Update state
            self.state[url]["last_status"] = status
            self.state[url]["last_check"] = datetime.now().isoformat()

        # Save state for next run (idempotency)
        self.save_state()
        logging.info("Health check completed\n")


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.run()
