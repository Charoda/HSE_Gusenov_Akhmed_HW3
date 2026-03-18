# URL Shortener API

A FastAPI-based service for shortening URLs with analytics, caching, and management features.

## Features

### Required Functions (5)
1. **Create/Delete/Update/Get Short Links**
   - `POST /links/shorten` - Create a short link
   - `GET /links/{short_code}` - Redirect to original URL
   - `DELETE /links/{short_code}` - Delete a link
   - `PUT /links/{short_code}` - Update link URL

2. **Link Statistics**
   - `GET /links/{short_code}/stats` - View link analytics

3. **Custom Aliases**
   - Support for custom short codes via `custom_alias` parameter

4. **Search by Original URL**
   - `GET /links/search?original_url={url}` - Find all links for a URL

5. **Link Expiration**
   - `expires_at` parameter for automatic deletion

### Additional Features (2+)
- **Cleanup Expired Links** - `POST /links/cleanup/expired`
- **Cleanup Unused Links** - `POST /links/cleanup/unused?days=90`
- **Redis Caching** - All link lookups are cached
- **Authentication** - User registration and JWT tokens
- **Access Control** - Update/Delete restricted to link owners

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **SQLAlchemy** - ORM
- **JWT** - Authentication
- **Docker** - Containerization

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Using Docker Compose (Recommended)

1. Clone and setup:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

2. Start all services:
```bash
docker-compose up -d
```

3. The API will be available at: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Configure DATABASE_URL and REDIS_URL in .env
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

### Authentication

#### Register a new user
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

#### Login
```http
POST /auth/login?username=john_doe&password=securepassword123
```

Returns: `{"access_token": "...", "token_type": "bearer"}`

Use the token in subsequent requests:
```http
Authorization: Bearer <your_token>
```

### Links

#### Create a short link
```http
POST /links/shorten
Content-Type: application/json

{
  "original_url": "https://very-long-url.com/with/many/segments",
  "custom_alias": "mylink",
  "expires_at": "2024-12-31T23:59:00"
}
```

Response:
```json
{
  "id": 1,
  "short_code": "mylink",
  "original_url": "https://very-long-url.com/with/many/segments",
  "custom_alias": "mylink",
  "clicks": 0,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Redirect (use the short link)
```http
GET /links/{short_code}
```
Returns a 307 redirect to the original URL.

#### Get link statistics
```http
GET /links/{short_code}/stats
```

Response:
```json
{
  "original_url": "https://very-long-url.com/with/many/segments",
  "short_code": "mylink",
  "created_at": "2024-01-01T00:00:00",
  "clicks": 42,
  "last_clicked_at": "2024-01-15T10:30:00",
  "is_active": true,
  "expires_at": null
}
```

#### Update a link
```http
PUT /links/{short_code}
Content-Type: application/json

{
  "original_url": "https://new-url.com"
}
```

#### Delete a link
```http
DELETE /links/{short_code}
```

#### Search by original URL
```http
GET /links/search?original_url=https://very-long-url.com/with/many/segments
```

#### Cleanup expired links (admin/owner only)
```http
POST /links/cleanup/expired
```

#### Cleanup unused links (admin/owner only)
```http
POST /links/cleanup/unused?days=90
```

## Database Schema

### Users
- `id` - Primary key
- `username` - Unique
- `email` - Unique
- `hashed_password` - BCrypt hashed
- `is_active` - Boolean flag
- `created_at` - Timestamp

### Links
- `id` - Primary key
- `short_code` - Unique short identifier
- `original_url` - Full URL
- `custom_alias` - Optional custom short code
- `user_id` - Foreign key to users (nullable for anonymous)
- `clicks` - Click counter
- `last_clicked_at` - Timestamp of last click
- `expires_at` - Optional expiration timestamp
- `is_active` - Boolean flag
- `created_at` - Timestamp

## Caching Strategy

- **Redis** is used to cache link lookups
- Cache key format: `link:{short_code}`
- TTL: 1 hour (3600 seconds)
- Cache is invalidated on:
  - Link creation
  - Link update
  - Link deletion
  - Link click (updates stats)

## Access Control

- **GET** endpoints are public (no authentication required)
- **POST/PUT/DELETE** endpoints require authentication for:
  - Links created by authenticated users
  - Anonymous links can be managed by anyone (no user_id)
- To restrict management to owners only, ensure you're authenticated

## Environment Variables

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=url_shortener
SECRET_KEY=your-secret-key-change-in-production
```

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── auth_router.py    # Authentication endpoints
│   │   └── links_router.py   # Link management endpoints
│   ├── services/
│   │   └── link_service.py   # Business logic for links
│   ├── utils/
│   │   ├── security.py       # Password & JWT utilities
│   │   └── redis_client.py   # Redis caching client
│   ├── __init__.py
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration
│   ├── database.py           # Database connection
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   └── initialization.py     # Startup initialization
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Testing the API

1. Start the service with Docker Compose
2. Open `http://localhost:8000/docs` for interactive Swagger UI
3. Register a user via `/auth/register`
4. Create a short link via `/links/shorten`
5. Access the short link via browser or `GET /links/{short_code}`
6. View stats via `/links/{short_code}/stats`

## Notes

- Short codes are 6 characters (letters and digits)
- Custom aliases must be unique
- Expired links are automatically deleted on access
- Click tracking is automatic on redirect
- Redis caching improves performance for frequently accessed links
- All timestamps are in UTC

## License

MIT