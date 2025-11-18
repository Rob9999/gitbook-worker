# API Reference

## REST Endpoints

### Users API

#### GET /api/users

Alle Benutzer abrufen.

**Response:**

```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  ],
  "total": 1
}
```

#### POST /api/users

Neuen Benutzer erstellen.

**Request Body:**

```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secureP@ssw0rd",
  "role": "user"
}
```

**Response:**

```json
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Products API

#### GET /api/products

Liste aller Produkte mit Paginierung.

**Query Parameters:**

| Parameter | Typ | Beschreibung | Default |
|-----------|-----|--------------|---------|
| page | integer | Seitennummer | 1 |
| limit | integer | Einträge pro Seite | 10 |
| sort | string | Sortierfeld | name |
| order | string | asc oder desc | asc |

**Response:**

```json
{
  "products": [
    {
      "id": 1,
      "name": "Product A",
      "price": 29.99,
      "stock": 100
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 150,
    "pages": 15
  }
}
```

## Error Codes

| Code | Status | Beschreibung |
|------|--------|--------------|
| 200 | OK | Erfolg ✅ |
| 201 | Created | Erstellt ✅ |
| 400 | Bad Request | Ungültige Eingabe ❌ |
| 401 | Unauthorized | Nicht authentifiziert 🔒 |
| 403 | Forbidden | Keine Berechtigung 🚫 |
| 404 | Not Found | Nicht gefunden ❓ |
| 500 | Internal Error | Server-Fehler 💥 |

## Rate Limiting

API-Anfragen sind limitiert:

$$
\text{Limit} = \begin{cases}
1000 \text{ req/h} & \text{Free Tier} \\
10000 \text{ req/h} & \text{Pro Tier} \\
\infty & \text{Enterprise}
\end{cases}
$$

## Authentication

Bearer Token in Authorization Header:

```http
GET /api/users HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
```

## WebSocket Events

Echtzeit-Kommunikation über WebSocket:

```javascript
const ws = new WebSocket('wss://api.example.com/ws');

ws.on('message', (data) => {
    console.log('Received:', data);
});

// Sende Nachricht
ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['orders', 'notifications']
}));
```

### Verfügbare Events

| Event | Direction | Beschreibung |
|-------|-----------|--------------|
| subscribe | Client → Server | Kanal abonnieren |
| unsubscribe | Client → Server | Kanal abbestellen |
| message | Server → Client | Neue Nachricht |
| error | Server → Client | Fehler aufgetreten |
| ping | Bidirectional | Keep-Alive |

## Internationalisierung

Die API unterstützt mehrere Sprachen über `Accept-Language` Header:

```http
Accept-Language: de-DE, en-US, ja-JP, zh-CN
```

Beispiel-Antworten:

- **Deutsch**: "Benutzer erfolgreich erstellt"
- **English**: "User created successfully"
- **日本語**: "ユーザーが正常に作成されました"
- **中文**: "用户创建成功"
