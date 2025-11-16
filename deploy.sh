#!/bin/bash
# Deployment script for FunSearch

set -e

echo "🚀 FunSearch Deployment Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env with your configuration before proceeding${NC}"
    echo ""
    read -p "Continue with default configuration? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Exiting. Please configure .env and run again."
        exit 1
    fi
fi

# Parse command
COMMAND=${1:-"up"}

case $COMMAND in
    "build")
        echo "🔨 Building all containers..."
        docker-compose build
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;

    "up")
        echo "🚀 Starting all services..."
        docker-compose up -d
        echo ""
        echo -e "${GREEN}✓ All services started${NC}"
        echo ""
        echo "📊 Service URLs:"
        echo "  • Frontend:  http://localhost:7350"
        echo "  • Backend:   http://localhost:7351"
        echo "  • API Docs:  http://localhost:7351/docs"
        echo "  • MLflow:    http://localhost:7352"
        echo "  • Flower:    http://localhost:5555"
        echo ""
        echo "📋 Logs: docker-compose logs -f"
        echo "🛑 Stop: ./deploy.sh down"
        ;;

    "down")
        echo "🛑 Stopping all services..."
        docker-compose down
        echo -e "${GREEN}✓ All services stopped${NC}"
        ;;

    "restart")
        echo "🔄 Restarting all services..."
        docker-compose restart
        echo -e "${GREEN}✓ All services restarted${NC}"
        ;;

    "logs")
        SERVICE=${2:-""}
        if [ -z "$SERVICE" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f $SERVICE
        fi
        ;;

    "status")
        echo "📊 Service Status:"
        docker-compose ps
        ;;

    "clean")
        echo "🧹 Cleaning up..."
        read -p "This will remove all containers, volumes, and data. Continue? (y/n): " CONFIRM
        if [ "$CONFIRM" = "y" ]; then
            docker-compose down -v
            echo -e "${GREEN}✓ Cleanup complete${NC}"
        else
            echo "Cancelled"
        fi
        ;;

    "migrate")
        echo "🗄️  Running database migrations..."
        docker-compose exec backend alembic upgrade head
        echo -e "${GREEN}✓ Migrations complete${NC}"
        ;;

    "shell")
        SERVICE=${2:-"backend"}
        echo "🐚 Opening shell in $SERVICE..."
        docker-compose exec $SERVICE /bin/bash
        ;;

    "test")
        echo "🧪 Running tests..."
        docker-compose exec backend pytest
        ;;

    "init-sandbox")
        echo "🏗️  Building sandbox image..."
        docker build -f Dockerfile.sandbox -t funsearch-sandbox:latest .
        echo -e "${GREEN}✓ Sandbox image built${NC}"
        ;;

    "scale-workers")
        WORKERS=${2:-2}
        echo "⚖️  Scaling workers to $WORKERS..."
        docker-compose up -d --scale worker=$WORKERS
        echo -e "${GREEN}✓ Workers scaled to $WORKERS${NC}"
        ;;

    "backup")
        BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        echo "💾 Creating backup to $BACKUP_DIR..."

        # Backup database
        docker-compose exec -T postgres pg_dump -U funsearch funsearch > $BACKUP_DIR/database.sql

        # Backup MLflow artifacts
        docker cp funsearch-mlflow:/mlflow/artifacts $BACKUP_DIR/mlflow_artifacts

        echo -e "${GREEN}✓ Backup complete: $BACKUP_DIR${NC}"
        ;;

    "restore")
        BACKUP_PATH=${2}
        if [ -z "$BACKUP_PATH" ]; then
            echo -e "${RED}Error: Please specify backup path${NC}"
            echo "Usage: ./deploy.sh restore /path/to/backup"
            exit 1
        fi

        echo "♻️  Restoring from $BACKUP_PATH..."

        # Restore database
        if [ -f "$BACKUP_PATH/database.sql" ]; then
            docker-compose exec -T postgres psql -U funsearch funsearch < $BACKUP_PATH/database.sql
            echo -e "${GREEN}✓ Database restored${NC}"
        fi

        # Restore MLflow artifacts
        if [ -d "$BACKUP_PATH/mlflow_artifacts" ]; then
            docker cp $BACKUP_PATH/mlflow_artifacts funsearch-mlflow:/mlflow/
            echo -e "${GREEN}✓ MLflow artifacts restored${NC}"
        fi

        echo -e "${GREEN}✓ Restore complete${NC}"
        ;;

    "help")
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build          - Build all Docker images"
        echo "  up             - Start all services (default)"
        echo "  down           - Stop all services"
        echo "  restart        - Restart all services"
        echo "  logs [service] - View logs (optionally for specific service)"
        echo "  status         - Show service status"
        echo "  clean          - Remove all containers and volumes"
        echo "  migrate        - Run database migrations"
        echo "  shell [service]- Open shell in service (default: backend)"
        echo "  test           - Run tests"
        echo "  init-sandbox   - Build sandbox Docker image"
        echo "  scale-workers N- Scale worker count to N"
        echo "  backup         - Create backup of database and MLflow"
        echo "  restore PATH   - Restore from backup"
        echo "  help           - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh build"
        echo "  ./deploy.sh up"
        echo "  ./deploy.sh logs backend"
        echo "  ./deploy.sh scale-workers 4"
        echo "  ./deploy.sh backup"
        ;;

    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run './deploy.sh help' for usage information"
        exit 1
        ;;
esac
