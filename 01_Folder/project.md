def process_user(email):
if not database.user_exists(email):
database.add_user(email)
send_welcome_email(email)
else:
print(f"User {email} already exists, skipping")

```

**Real incident:** A major fintech sent 10,000 duplicate charge notifications because their webhook handler wasn't idempotent. Cost: $50K in support tickets.

### 4. **The Automation Reliability Pyramid**
```

         🎯 MONITORING & ALERTS
              (Know when it breaks)

         🔄 RETRY LOGIC & FALLBACKS
           (Handle expected failures)

       ✅ ERROR HANDLING
         (Catch exceptions gracefully)

     📝 LOGGING & OBSERVABILITY
       (Understand what happened)

🏗️ IDEMPOTENT DESIGN
(Safe to run multiple times)

```

**WHY:** Build from bottom to top. Logging before monitoring. Idempotency before retries.

---

## Tools Used (Stage 1)

- **Python 3.10+** (scripting)
- **Basic terminal/bash** (manual testing)
- **cron** (scheduling)
- **ngrok** (webhook testing - we'll use this soon)
- **VS Code** or any code editor

---

## Real-World Use Cases

1. **SaaS Operations:** Auto-cleanup of trial accounts after 14 days
2. **DevOps:** Daily health checks of production servers
3. **E-commerce:** Abandoned cart reminder automation
4. **Finance:** EOD transaction reconciliation
5. **Customer Support:** Auto-assign tickets based on keywords

---

## 🛠️ Project 1: System Health Monitor (Idempotent Design)

### Problem Statement
You manage 5 servers. Every hour, you need to:
- Check if each server is responding
- Log the status
- Only alert if a server is down for 2+ consecutive checks (avoid false alarms)

### Why This Project?
- **Teaches:** Idempotency, stateful automation, cron scheduling
- **Used by:** Every DevOps team (this is literally how Pingdom, UptimeRobot work)
- **Freelance value:** "$500/month monitoring setup" is a real gig

### Automation Flow
```

TRIGGER: Cron (every hour)
↓
CHECK: Ping each server (HTTP request)
↓
LOGIC: Compare with previous state
↓
ACTION:

- Log result
- If down 2+ times → Send alert
- Update state file

```

### Architecture
```

[Cron Scheduler]
↓
[health_monitor.py]
↓
[state.json] ← Stores last check results (idempotency key)
↓
[servers.txt] ← List of servers to monitor
↓
[alerts.log] ← Alert history
