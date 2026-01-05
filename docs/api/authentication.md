# Authentication API

Authentication endpoints for user registration, login, and token management.

---

## Register

Create a new user account.

**Endpoint**: `POST /api/v1/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response** (201):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 604800
  }
}
```

**Errors**:
- `400`: Email already registered

---

## Login

Authenticate with email and password.

**Endpoint**: `POST /api/v1/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 604800
  }
}
```

**Errors**:
- `401`: Incorrect email or password
- `403`: User account is inactive

---

## Get Current User

Get information about the authenticated user.

**Endpoint**: `GET /api/v1/auth/me`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Errors**:
- `401`: Unauthorized (invalid/missing token)

---

## Refresh Token

Refresh the access token.

**Endpoint**: `POST /api/v1/auth/refresh`

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Errors**:
- `401`: Unauthorized (invalid/missing token)

---

## Endpoint Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/auth/register` | No | Register new user |
| POST | `/auth/login` | No | Login with credentials |
| GET | `/auth/me` | Yes | Get current user |
| POST | `/auth/refresh` | Yes | Refresh token |

---

## Token Usage

Include token in `Authorization` header for all authenticated requests:

```
Authorization: Bearer <access_token>
```

**Token Expiration**: 7 days (604,800 seconds)

---

## Next Steps

- **[Workspaces API](workspaces.md)** - Workspace management
- **[Documents API](documents.md)** - Document operations

