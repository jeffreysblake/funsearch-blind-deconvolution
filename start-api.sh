#!/bin/bash
# Start FastAPI backend server

echo "🚀 Starting FunSearch API on port 7351..."
echo ""
echo "Available at:"
echo "  - API:    http://localhost:7351"
echo "  - Docs:   http://localhost:7351/docs"
echo "  - Health: http://localhost:7351/health"
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 7351 --reload
