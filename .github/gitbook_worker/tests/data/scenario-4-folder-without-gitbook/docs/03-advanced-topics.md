# Advanced Topics

## Performance Optimization

### Database Indexing

Optimale Index-Strategien für verschiedene Abfragen:

| Query Type | Index | Performance Gain |
|------------|-------|------------------|
| Exact Match | B-Tree | 100x - 1000x |
| Range Query | B-Tree | 10x - 100x |
| Full-Text | GIN/GiST | 50x - 500x |
| Geospatial | GiST | 100x - 10000x |

**Beispiel:**

```sql
-- B-Tree Index für schnelle Lookups
CREATE INDEX idx_users_email ON users(email);

-- GIN Index für Volltextsuche
CREATE INDEX idx_posts_content ON posts USING gin(to_tsvector('german', content));

-- Composite Index für Multi-Column Queries
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

### Caching Strategy

Multi-Layer Caching für optimale Performance:

```
┌─────────────┐
│   Browser   │  (Service Worker, 24h)
└──────┬──────┘
       ↓
┌─────────────┐
│     CDN     │  (CloudFront, 1h)
└──────┬──────┘
       ↓
┌─────────────┐
│    Redis    │  (In-Memory, 5min)
└──────┬──────┘
       ↓
┌─────────────┐
│  Database   │  (PostgreSQL)
└─────────────┘
```

**Cache-Hit-Ratio Formel:**

$$
\text{Hit Ratio} = \frac{\text{Cache Hits}}{\text{Total Requests}} \times 100\%
$$

Ziel: > 95% für optimale Performance

### Load Balancing

Anfragen werden auf mehrere Server verteilt:

| Algorithmus | Use Case | Fairness |
|-------------|----------|----------|
| Round Robin | Gleichmäßige Last | ⭐⭐⭐⭐⭐ |
| Least Connections | Ungleiche Requests | ⭐⭐⭐⭐ |
| IP Hash | Session Affinity | ⭐⭐⭐ |
| Weighted | Heterogene Server | ⭐⭐⭐⭐ |

## Security Best Practices

### Input Validation

**Immer validieren:**

```python
import re
from typing import Optional

def validate_email(email: str) -> Optional[str]:
    """Validate email address with Unicode support."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email.lower()
    return None

# Test mit internationalen Domains
emails = [
    'user@example.com',
    'admin@例え.jp',  # Internationalized Domain Names
    'test@münchen.de'
]
```

### SQL Injection Prevention

**❌ Unsicher:**

```python
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

**✅ Sicher:**

```python
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (user_input,))
```

### XSS Protection

Output-Encoding für verschiedene Kontexte:

| Context | Encoding | Beispiel |
|---------|----------|----------|
| HTML Body | HTML Entity | `&lt;script&gt;` |
| HTML Attribute | Attribute | `&quot;onclick=...&quot;` |
| JavaScript | Unicode | `\u003cscript\u003e` |
| URL | Percent | `%3Cscript%3E` |

## Microservices Architecture

Verteilte System-Architektur:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   API        │────▶│   Auth       │────▶│   Users      │
│   Gateway    │     │   Service    │     │   Service    │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├────────────▶ ┌──────────────┐     ┌──────────────┐
       │              │   Product    │────▶│   Inventory  │
       │              │   Service    │     │   Service    │
       │              └──────────────┘     └──────────────┘
       │
       └────────────▶ ┌──────────────┐     ┌──────────────┐
                      │   Order      │────▶│   Payment    │
                      │   Service    │     │   Service    │
                      └──────────────┘     └──────────────┘
```

### Service Communication

**Synchronous (REST):**

```javascript
// TypeScript Example
async function getUserProfile(userId: string): Promise<User> {
    const response = await fetch(`https://users-service/api/users/${userId}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch user: ${response.status}`);
    }
    return response.json();
}
```

**Asynchronous (Message Queue):**

```python
import pika
import json

def publish_order_created(order_id: str, user_id: str):
    """發送訂單創建事件到消息隊列 (Sende Bestellung an Message Queue)"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    
    message = {
        'event': 'order.created',
        'order_id': order_id,
        'user_id': user_id,
        'timestamp': '2024-01-15T10:30:00Z'
    }
    
    channel.basic_publish(
        exchange='orders',
        routing_key='order.created',
        body=json.dumps(message)
    )
    
    connection.close()
```

## Monitoring & Observability

### Key Metrics

Die "Golden Signals" für Service Health:

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| **Latency** | Response Time | p95 > 500ms |
| **Traffic** | Requests/Second | > 10000 rps |
| **Errors** | Error Rate | > 1% |
| **Saturation** | Resource Usage | CPU > 80% |

### Distributed Tracing

Trace-ID durch alle Services:

```
Request: GET /api/orders/123
├─ api-gateway (5ms)
│  └─ auth-service (10ms)
│     └─ users-service (15ms)
├─ orders-service (20ms)
│  ├─ database (50ms)
│  └─ cache (2ms)
└─ payment-service (100ms)
   └─ external-api (200ms)

Total: 402ms (Waterfall)
```

### Alerting Rules

Prometheus Alert-Beispiele:

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
```

## Internationalization (i18n)

Mehrsprachige Unterstützung in der Anwendung:

### Sprachkonfiguration

```typescript
const translations = {
    de: {
        welcome: 'Willkommen',
        goodbye: 'Auf Wiedersehen'
    },
    en: {
        welcome: 'Welcome',
        goodbye: 'Goodbye'
    },
    ja: {
        welcome: 'ようこそ',
        goodbye: 'さようなら'
    },
    zh: {
        welcome: '欢迎',
        goodbye: '再见'
    },
    ko: {
        welcome: '환영합니다',
        goodbye: '안녕히 가세요'
    }
};
```

### Datum & Zeit-Formatierung

| Locale | Format | Beispiel |
|--------|--------|----------|
| de-DE | DD.MM.YYYY HH:mm | 15.01.2024 14:30 |
| en-US | MM/DD/YYYY h:mm AM/PM | 01/15/2024 2:30 PM |
| ja-JP | YYYY年MM月DD日 HH:mm | 2024年01月15日 14:30 |
| zh-CN | YYYY-MM-DD HH:mm | 2024-01-15 14:30 |

### Währungsformatierung

```javascript
const formatCurrency = (amount, locale, currency) => {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(amount);
};

// Beispiele:
formatCurrency(1234.56, 'de-DE', 'EUR');  // 1.234,56 €
formatCurrency(1234.56, 'en-US', 'USD');  // $1,234.56
formatCurrency(1234.56, 'ja-JP', 'JPY');  // ¥1,235
```

## Deployment Strategies

### Blue-Green Deployment

Null-Downtime Releases:

```
Current (Blue):  [v1.0] ──▶ 100% Traffic
New (Green):     [v2.0] ──▶   0% Traffic

          ↓ Switch

Old (Blue):      [v1.0] ──▶   0% Traffic
Current (Green): [v2.0] ──▶ 100% Traffic
```

### Canary Releases

Graduelles Rollout:

| Phase | v1.0 Traffic | v2.0 Traffic | Duration |
|-------|--------------|--------------|----------|
| 1 | 95% | 5% | 1 hour |
| 2 | 80% | 20% | 2 hours |
| 3 | 50% | 50% | 4 hours |
| 4 | 0% | 100% | Final |

**Monitoring-Metriken während Canary:**

$$
\text{Success} = \frac{\text{Errors}_{v2.0}}{\text{Errors}_{v1.0}} < 1.2
$$

Falls die Fehlerrate von v2.0 mehr als 20% über v1.0 liegt → Rollback!

---

## Zusammenfassung

Diese fortgeschrittenen Themen decken ab:

- ✅ Performance-Optimierung (DB, Caching, Load Balancing)
- ✅ Security Best Practices (Validation, SQL Injection, XSS)
- ✅ Microservices-Architektur (Sync/Async Communication)
- ✅ Monitoring & Observability (Golden Signals, Tracing)
- ✅ Internationalisierung (8+ Sprachen)
- ✅ Deployment-Strategien (Blue-Green, Canary)
- ✅ Komplexe Tabellen & Diagramme
- ✅ Code mit Unicode-Kommentaren
- ✅ Mathematische Formeln
