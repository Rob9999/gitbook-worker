#!/bin/bash
# Bash Wrapper für Docker-basierte Tests und Workflows
# Usage: ./run-in-docker.sh [test|test-slow|orchestrator|shell|build-only] [--profile PROFILE] [--no-build]

set -e

COMMAND=""
PROFILE="local"
NO_BUILD=0

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        test|test-slow|orchestrator|shell|build-only)
            COMMAND="$1"
            shift
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --no-build)
            NO_BUILD=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [test|test-slow|orchestrator|shell|build-only] [--profile PROFILE] [--no-build]"
            exit 1
            ;;
    esac
done

if [ -z "$COMMAND" ]; then
    echo "Error: Command required"
    echo "Usage: $0 [test|test-slow|orchestrator|shell|build-only] [--profile PROFILE] [--no-build]"
    exit 1
fi

DOCKERFILE=".github/gitbook_worker/tools/docker/Dockerfile"
IMAGE_TAG="erda-workflow-tools"
CONTEXT="."

# Check Docker daemon
echo "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if image exists or needs to be built
if ! docker image inspect "$IMAGE_TAG" &> /dev/null; then
    if [ $NO_BUILD -eq 1 ]; then
        echo "Error: Image '$IMAGE_TAG' not found and --no-build is set"
        exit 1
    fi
    echo "Building Docker image '$IMAGE_TAG'..."
    docker build -f "$DOCKERFILE" -t "$IMAGE_TAG" "$CONTEXT"
else
    echo "Using existing Docker image '$IMAGE_TAG'"
fi

if [ "$COMMAND" = "build-only" ]; then
    echo "Build complete!"
    exit 0
fi

# Create external log directory for Docker
WORKDIR=$(pwd)
DOCKER_LOG_DIR="${WORKDIR}/.docker-logs"
mkdir -p "$DOCKER_LOG_DIR"
echo "Created external log directory: $DOCKER_LOG_DIR"

# Run the desired command
echo "Running command in Docker container..."
echo "Logs will be available in: $DOCKER_LOG_DIR"

case $COMMAND in
    test)
        docker run --rm \
            -v "${WORKDIR}:/workspace" \
            -v "${DOCKER_LOG_DIR}:/docker-logs" \
            -w /workspace \
            -e PYTHONPATH=/workspace \
            -e DOCKER_LOG_DIR=/docker-logs \
            "$IMAGE_TAG" \
            bash -c "cd /workspace && python3 -m pytest .github/gitbook_worker/tests -v --tb=short"
        ;;
    test-slow)
        docker run --rm \
            -v "${WORKDIR}:/workspace" \
            -v "${DOCKER_LOG_DIR}:/docker-logs" \
            -w /workspace \
            -e PYTHONPATH=/workspace \
            -e DOCKER_LOG_DIR=/docker-logs \
            "$IMAGE_TAG" \
            bash -c "cd /workspace && python3 -m pytest .github/gitbook_worker/tests -v -m slow --tb=short"
        ;;
    orchestrator)
        docker run --rm \
            -v "${WORKDIR}:/workspace" \
            -v "${DOCKER_LOG_DIR}:/docker-logs" \
            -w /workspace \
            -e PYTHONPATH=/workspace \
            -e DOCKER_LOG_DIR=/docker-logs \
            "$IMAGE_TAG" \
            bash -c "cd /workspace && python3 -m tools.workflow_orchestrator --root /workspace --manifest publish.yml --profile $PROFILE"
        ;;
    shell)
        docker run --rm -it \
            -v "${WORKDIR}:/workspace" \
            -v "${DOCKER_LOG_DIR}:/docker-logs" \
            -w /workspace \
            -e PYTHONPATH=/workspace \
            -e DOCKER_LOG_DIR=/docker-logs \
            "$IMAGE_TAG" \
            bash
        ;;
esac

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\nCommand completed successfully!"
else
    echo -e "\nCommand failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE
