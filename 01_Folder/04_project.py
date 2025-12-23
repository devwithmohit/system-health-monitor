"""
System Health Monitor - Production Pattern with Slack Integration
Level 3 (Advanced)

Features:
- HTTP Method Support (GET/POST/PUT)
- Response Time Monitoring
- Stateful Idempotent Alerts
- Slack Incoming Webhook Alerts (REAL Slack channel)
"""

import json
import os
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
# ================= CONFIGURATION =================

SERVERS_FILE = os.environ.get("SERVERS_FILE", "servers.json")
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
LOG_FILE = os.environ.get("LOG_FILE", "health_monitor.log")

ALERT_THRESHOLD = int(os.environ.get("ALERT_THRESHOLD", "2"))
MAX_RESPONSE_TIME = float(os.environ.get("MAX_RESPONSE_TIME", "2.0"))

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
SLACK_USERNAME = os.environ.get("SLACK_USERNAME", "Health Monitor")
SLACK_ICON_EMOJI = os.environ.get("SLACK_ICON_EMOJI", ":warning:")

if not SLACK_WEBHOOK_URL:
    raise ValueError("SLACK_WEBHOOK_URL environment variable is required")

# ================= LOGGING =================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# ================= SLACK ALERT HANDLER =================


class SlackAlertHandler:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        logging.info("Slack webhook initialized")

    def send_alert(self, message: str, status: str, server: Dict = None):
        color_map = {
            "DOWN": "#FF0000",
            "SLOW": "#FFA500",
            "RECOVERED": "#36A64F",
        }

        fields = [
            {"title": "Status", "value": status, "short": True},
            {
                "title": "Time",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "short": True,
            },
        ]

        if server:
            fields.extend(
                [
                    {"title": "Server", "value": server["name"], "short": True},
                    {"title": "Method", "value": server["method"], "short": True},
                    {"title": "URL", "value": server["url"], "short": False},
                    {
                        "title": "Response Time",
                        "value": f"{server.get('response_time', 'N/A')}s",
                        "short": True,
                    },
                ]
            )

        payload = {
            "username": SLACK_USERNAME,
            "icon_emoji": SLACK_ICON_EMOJI,
            "attachments": [
                {
                    "color": color_map.get(status, "#FF0000"),
                    "title": f"🚨 System Health Alert: {status}",
                    "text": message,
                    "fields": fields,
                    "footer": "System Health Monitor",
                    "ts": int(time.time()),
                }
            ],
        }

        try:
            res = requests.post(self.webhook_url, json=payload, timeout=5)
            res.raise_for_status()
            logging.info(" Slack alert sent")
        except Exception as e:
            logging.error(f" Slack alert failed: {e}")


# ================= HEALTH MONITOR =================


class HealthMonitor:
    def __init__(self):
        self.state = self.load_state()
        self.slack = SlackAlertHandler(SLACK_WEBHOOK_URL)

    def load_state(self) -> Dict:
        if Path(STATE_FILE).exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.warning("Corrupted state file, resetting")
        return {}

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_servers(self) -> List[Dict]:
        if not Path(SERVERS_FILE).exists():
            example = [
                {
                    "name": "Healthy API",
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
            logging.info("📁 Created example servers.json")
            return example

        with open(SERVERS_FILE) as f:
            return json.load(f)

    def check_server(self, server: Dict):
        start = time.time()
        try:
            res = requests.request(
                method=server["method"],
                url=server["url"],
                timeout=5,
            )
            response_time = round(time.time() - start, 2)
            return res.status_code == 200, response_time
        except Exception:
            response_time = round(time.time() - start, 2)
            return False, response_time

    def should_alert(self, key: str, is_down: bool):
        state = self.state.setdefault(
            key,
            {
                "failures": 0,
                "alerted": False,
            },
        )

        if is_down:
            state["failures"] += 1
            if state["failures"] >= ALERT_THRESHOLD and not state["alerted"]:
                state["alerted"] = True
                return True
        else:
            if state["failures"] > 0:
                state["failures"] = 0
                state["alerted"] = False
                return "RECOVERED"
        return False

    def run(self):
        logging.info(" Starting health check")
        servers = self.load_servers()

        for server in servers:
            key = f"{server['method']}:{server['url']}"
            is_up, response_time = self.check_server(server)
            server["response_time"] = response_time

            if not is_up:
                status = "DOWN"
            elif response_time > MAX_RESPONSE_TIME:
                status = "SLOW"
            else:
                status = "UP"

            logging.info(
                f"{status}: {server['name']} | {response_time}s | {server['url']}"
            )

            alert = self.should_alert(key, status == "DOWN")

            if alert is True:
                self.slack.send_alert(
                    f"{server['name']} is DOWN for {ALERT_THRESHOLD}+ checks",
                    "DOWN",
                    server,
                )

            elif alert == "RECOVERED":
                self.slack.send_alert(
                    f"{server['name']} has RECOVERED",
                    "RECOVERED",
                    server,
                )

            elif status == "SLOW":
                self.slack.send_alert(
                    f"{server['name']} response time exceeded SLA",
                    "SLOW",
                    server,
                )

        self.save_state()
        logging.info("Health check completed\n")


# ================= ENTRY POINT =================

if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.run()
