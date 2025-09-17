# FastAPI Server Setup

## Overview

The semantic search system now uses a FastAPI server instead of process spawning for better performance and reliability.

## Quick Start

### 1. Install Dependencies

```bash
cd Semantic-Search
pip install -r requirements.txt
```

### 2. Start the FastAPI Server

```bash
python start_server.py
```

Or manually:

```bash
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Verify Server is Running

- **Server URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Environment Variables

You can set the FastAPI server URL in your Next.js environment:

```bash
# In your .env.local file
FASTAPI_URL=http://localhost:8000
```

If not set, it defaults to `http://localhost:8000`.

## API Endpoints

- `POST /search` - Semantic search
- `POST /chatbot` - Chatbot queries
- `POST /process` - Document processing
- `GET /health` - Health check
- `GET /` - Root endpoint

## Integration with Next.js

The Next.js API route (`/api/semantic-search`) now makes HTTP requests to the FastAPI server instead of spawning Python processes. This provides:

- ✅ Better performance
- ✅ Connection pooling
- ✅ Proper error handling
- ✅ Health monitoring
- ✅ API documentation

## Troubleshooting

### Server Won't Start

1. Check if port 8000 is available:

   ```bash
   lsof -i :8000
   ```

2. Install missing dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

### Connection Issues

1. Verify the server is running:

   ```bash
   curl http://localhost:8000/health
   ```

2. Check the Next.js environment variable:
   ```bash
   echo $FASTAPI_URL
   ```

### Performance Issues

- The server runs with auto-reload in development
- For production, remove `--reload` flag
- Consider using a production ASGI server like Gunicorn

## Development vs Production

### Development

```bash
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
```

### Production

```bash
uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --workers 4
```

