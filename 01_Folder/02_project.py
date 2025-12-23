"""
System Health Monitor - Production Pattern
Level 2 (Partial)
Demonstrates: Idempotency, State Management, HTTP Method Support
"""

import json
import requests
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
SERVERS_FILE = "servers.json"
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
        if Path(STATE_FILE).exists():
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_servers(self) -> List[Dict]:
        """Load server configs (method + url + payload)"""
        if not Path(SERVERS_FILE).exists():
            example_servers = [
                {
                    "name": "Health Check API",
                    "url": "https://httpbin.org/status/200",
                    "method": "GET",
                },
                {
                    "name": "Create User API",
                    "url": "https://httpbin.org/post",
                    "method": "POST",
                    "payload": {"username": "test", "password": "123"},
                },
                {
                    "name": "Failing API",
                    "url": "https://httpbin.org/status/500",
                    "method": "GET",
                },
            ]
            with open(SERVERS_FILE, "w") as f:
                json.dump(example_servers, f, indent=2)
            logging.info(f"Created example {SERVERS_FILE}")
            return example_servers

        with open(SERVERS_FILE, "r") as f:
            return json.load(f)

    def check_server(self, server: Dict) -> bool:
        """Check API using HTTP method"""
        try:
            response = requests.request(
                method=server["method"],
                url=server["url"],
                json=server.get("payload"),
                timeout=5,
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logging.warning(f"Request failed for {server['url']}: {e}")
            return False

    def should_alert(self, key: str, is_down: bool) -> bool:
        if key not in self.state:
            self.state[key] = {
                "consecutive_failures": 0,
                "last_alert_sent": None,
                "last_status": "unknown",
            }

        if is_down:
            self.state[key]["consecutive_failures"] += 1
            failures = self.state[key]["consecutive_failures"]

            if failures >= ALERT_THRESHOLD and not self.state[key]["last_alert_sent"]:
                self.state[key]["last_alert_sent"] = datetime.now().isoformat()
                return True
        else:
            if self.state[key]["consecutive_failures"] > 0:
                logging.info(f"✅ API recovered: {key}")
            self.state[key]["consecutive_failures"] = 0
            self.state[key]["last_alert_sent"] = None

        return False

    def send_alert(self, message: str):
        logging.error(message)

        print("\n" + "=" * 60)
        print(message)
        print("=" * 60 + "\n")

    def run(self):
        logging.info("Starting health check run...")
        servers = self.load_servers()

        for server in servers:
            state_key = f"{server['method']}:{server['url']}"
            is_up = self.check_server(server)
            status = "UP" if is_up else "DOWN"

            logging.info(f"{status}: {server['name']} [{server['method']}]")

            if self.should_alert(state_key, not is_up):
                alert_msg = (
                    f"ALERT: {server['name']} "
                    f"({server['method']} {server['url']}) "
                    f"failed {ALERT_THRESHOLD}+ times"
                )
                self.send_alert(alert_msg)

            self.state[state_key]["last_status"] = status
            self.state[state_key]["last_check"] = datetime.now().isoformat()

        self.save_state()
        logging.info("Health check completed\n")


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.run()
