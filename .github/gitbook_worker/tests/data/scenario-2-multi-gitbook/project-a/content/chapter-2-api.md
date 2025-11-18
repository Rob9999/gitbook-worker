# Kapitel 2: API Design

## 2.1 RESTful Endpoints

Unsere API folgt REST-Prinzipien:

- `GET /api/v1/users` - Liste aller User
- `POST /api/v1/users` - Neuen User erstellen
- `PUT /api/v1/users/{id}` - User aktualisieren
- `DELETE /api/v1/users/{id}` - User löschen

## 2.2 Request & Response

Beispiel Request Body:

```json
{
  "username": "test_user",
  "email": "test@example.com",
  "role": "admin"
}
```

## 2.3 Error Handling

Fehlerbehandlung mit HTTP Status Codes:

- **200 OK** ✅ - Erfolg
- **400 Bad Request** ⚠️ - Validierungsfehler
- **401 Unauthorized** 🔒 - Authentifizierung fehlgeschlagen
- **404 Not Found** ❌ - Ressource nicht gefunden
- **500 Internal Server Error** 💥 - Server-Fehler

## 2.4 Performance-Metriken

Durchschnittliche Response-Zeiten:

$$
\text{Latenz} = \frac{\sum_{i=1}^{n} t_i}{n} \approx 50\text{ms}
$$

Wo $t_i$ die individuelle Request-Zeit ist.
