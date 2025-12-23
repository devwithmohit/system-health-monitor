"""
System Health Monitor - Production Pattern
Level 2 (Extended)
Demonstrates: Idempotency, State Management, HTTP Method Support,
Response Time Monitoring
"""

import json
import requests
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration
SERVERS_FILE = "servers.json"
STATE_FILE = "state.json"
LOG_FILE = "health_monitor.log"
ALERT_THRESHOLD = 2  # consecutive failures
MAX_RESPONSE_TIME = 2.0  # seconds (SLA)

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
        if not Path(SERVERS_FILE).exists():
            example = [
                {
                    "name": "Health API",
                    "url": "https://httpbin.org/status/200",
                    "method": "GET",
                },
                {
                    "name": "Slow API",
                    "url": "https://httpbin.org/delay/3",
                    "method": "GET",
                },
                {
                    "name": "Failing API",
                    "url": "https://httpbin.org/status/500",
                    "method": "GET",
                },
            ]
            with open(SERVERS_FILE, "w") as f:
                json.dump(example, f, indent=2)
            logging.info(f"Created example {SERVERS_FILE}")
            return example

        with open(SERVERS_FILE, "r") as f:
            return json.load(f)

    def check_server(self, server: Dict):
        """Returns (is_up, response_time)"""
        start = time.time()
        try:
            response = requests.request(
                method=server["method"],
                url=server["url"],
                json=server.get("payload"),
                timeout=5,
            )
            response_time = round(time.time() - start, 2)
            return response.status_code == 200, response_time
        except requests.RequestException as e:
            response_time = round(time.time() - start, 2)
            logging.warning(f"Request failed for {server['url']}: {e}")
            return False, response_time

    def should_alert(self, key: str, is_down: bool) -> bool:
        if key not in self.state:
            self.state[key] = {
                "consecutive_failures": 0,
                "last_alert_sent": None,
                "last_status": "unknown",
                "last_response_time": None,
            }

        if is_down:
            self.state[key]["consecutive_failures"] += 1

            if (
                self.state[key]["consecutive_failures"] >= ALERT_THRESHOLD
                and not self.state[key]["last_alert_sent"]
            ):
                self.state[key]["last_alert_sent"] = datetime.now().isoformat()
                return True
        else:
            if self.state[key]["consecutive_failures"] > 0:
                logging.info(f"✅ Recovered: {key}")
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
            key = f"{server['method']}:{server['url']}"

            is_up, response_time = self.check_server(server)

            if not is_up:
                status = "DOWN"
            elif response_time > MAX_RESPONSE_TIME:
                status = "SLOW"
            else:
                status = "UP"

            logging.info(
                f"{status}: {server['name']} [{server['method']}] {response_time}s"
            )

            if self.should_alert(key, status == "DOWN"):
                alert_msg = (
                    f"ALERT: {server['name']} is DOWN | Failures: {ALERT_THRESHOLD}+"
                )
                self.send_alert(alert_msg)

            # Update state
            self.state[key]["last_status"] = status
            self.state[key]["last_response_time"] = response_time
            self.state[key]["last_check"] = datetime.now().isoformat()

        self.save_state()
        logging.info("Health check completed\n")


if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.run()
