# Product Reviews API
A FastAPI-based service for managing product reviews.

## Local Development Setup
### Option 1: Manual Setup
1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Database configuration
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_DB="product_reviews"

# S3 configuration
export S3_ENDPOINT="http://ceph:8080"
export S3_ACCESS_KEY="your-access-key"
export S3_SECRET_KEY="your-secret-key"
export S3_BUCKET="product-reviews"
```

4. Set up the database:
```bash
# Create the database
createdb product_reviews

# Initialize Alembic
alembic init alembic

# Create and apply migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Option 2: Docker Setup

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Initialize the database:
```bash
# Connect to the app container
docker-compose exec app bash

# Inside the container, run migrations
alembic upgrade head
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

- `GET /` - Welcome message
- `GET /reviews` - Get all reviews
- `GET /reviews/{review_id}` - Get a specific review
- `POST /reviews` - Create a new review (with photos)
- `GET /reviews/product/{product_id}` - Get reviews for a specific product
- `PATCH /reviews/{review_id}/status` - Update review status
- `PATCH /photos/{photo_id}/status` - Update photo status

## Review Status

Reviews can have one of the following statuses:
- `pending` - Review is awaiting moderation
- `approved` - Review has been approved
- `rejected` - Review has been rejected

## Photo Status

Photos can have one of the following statuses:
- `pending` - Photo is awaiting moderation
- `approved` - Photo has been approved
- `rejected` - Photo has been rejected

## Example Review Creation

```bash
curl -X POST "http://localhost:8000/reviews" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "product_id=1" \
  -F "user_id=1" \
  -F "rating=5" \
  -F "comment=Great product!" \
  -F "photos=@photo1.jpg" \
  -F "photos=@photo2.jpg"
```

## Example Photo Status Update

```bash
curl -X PATCH "http://localhost:8000/photos/1/status" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"status": "approved"}'
```

## Environment Variables

### Database Configuration
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port
- `POSTGRES_DB` - PostgreSQL database name

### S3 Configuration
- `S3_ENDPOINT` - Ceph S3 endpoint URL
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key
- `S3_BUCKET` - S3 bucket name for storing review photos

## Docker Configuration

The application is containerized using Docker and Docker Compose. The setup includes:

1. FastAPI Application Container
   - Based on Python 3.11
   - Exposes port 8000
   - Mounts the application code as a volume for development

2. PostgreSQL Container
   - Based on PostgreSQL 15
   - Exposes port 5432
   - Persists data using a named volume

3. Ceph S3 Container
   - Based on Ceph Daemon
   - Exposes port 8080
   - Persists data using a named volume
   - Pre-configured with demo credentials

To start the entire stack:
```bash
docker-compose up --build
```

To stop the stack:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f
```
