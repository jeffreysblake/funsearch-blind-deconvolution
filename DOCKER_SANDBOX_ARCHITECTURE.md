# Docker Sandbox Architecture

## Overview

This document describes the Docker-based sandboxing strategy for the FunSearch framework, enabling secure parallel execution of LLM-generated code.

## Design Decisions

### ✅ Chosen Approach: Docker Sibling Containers

**Architecture**: App runs on host (or in container), spawns sibling containers for sandboxing

```
Host Machine
├── LM Studio (port 1234) - GPU access
├── FunSearch App (host or container)
│   └── Docker SDK → spawns sandbox containers
├── Redis (container)
└── MLflow (container)

Sandbox Containers (ephemeral, parallel)
├── Eval Container 1 (isolated, no network, resource-limited)
├── Eval Container 2
├── ...
└── Eval Container N
```

### ❌ Rejected: App Container = Sandbox

**Why Not?**
- Security boundary violation (LLM code in same container as app)
- One malicious program could compromise entire app
- Can't enforce strict resource limits without affecting app

### ❌ Rejected: RestrictedPython

**Why Not?**
- Not secure against adversarial code
- Compile-time restrictions can be bypassed
- Example exploit:
  ```python
  ().__class__.__bases__[0].__subclasses__()[104].__init__.__globals__['sys'].modules['os'].system('ls')
  ```
- Only suitable for "friendly" code restriction

## Implementation Details

### 1. Docker Socket Access

The app needs access to the Docker daemon to spawn containers:

**If app runs on host:**
```python
import docker
client = docker.from_env()  # Uses /var/run/docker.sock
```

**If app runs in container:**
```yaml
# docker-compose.yml
services:
  funsearch-app:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    user: root  # Required for socket access
```

### 2. Sandbox Container Configuration

**Security Hardening:**
```python
container_config = {
    "image": "funsearch-sandbox:latest",  # Minimal Python image
    "network_disabled": True,              # No internet access
    "mem_limit": "256m",                   # Memory limit
    "memswap_limit": "256m",               # No swap
    "nano_cpus": 1_000_000_000,            # 1 CPU core
    "pids_limit": 50,                      # Process limit
    "read_only": True,                     # Read-only filesystem
    "security_opt": ["no-new-privileges"], # Can't escalate privileges
    "cap_drop": ["ALL"],                   # Drop all capabilities
    "tmpfs": {"/tmp": "size=10m"},         # Temp storage
}
```

**Timeout Enforcement:**
```python
try:
    container = client.containers.run(**config, detach=True)
    result = container.wait(timeout=30)  # 30-second max
    output = container.logs()
except docker.errors.ContainerError:
    # Container exited with error
    pass
except TimeoutError:
    container.kill()  # Force stop
finally:
    container.remove(force=True)  # Cleanup
```

### 3. Parallel Execution Pool

**Container Pool Pattern:**
```python
from concurrent.futures import ThreadPoolExecutor
import docker

class SandboxPool:
    def __init__(self, max_workers=8):
        self.client = docker.from_env()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def run_code(self, code: str, test_input: dict) -> dict:
        """Execute code in isolated container"""
        # Prepare code + test input
        script = f"""
import json
{code}

# Run test
input_data = {json.dumps(test_input)}
result = evaluate(input_data)
print(json.dumps({{"score": result}}))
"""

        # Spawn container
        container = self.client.containers.run(
            image="funsearch-sandbox:latest",
            command=["python", "-c", script],
            **SECURITY_CONFIG,
            detach=True,
            remove=True,
        )

        try:
            exit_code = container.wait(timeout=30)
            logs = container.logs().decode('utf-8')

            # Parse result
            result = json.loads(logs.strip().split('\n')[-1])
            return {"success": True, "score": result["score"]}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate_population(self, programs: list[str], test_cases: list[dict]):
        """Evaluate multiple programs in parallel"""
        tasks = [
            (prog, test)
            for prog in programs
            for test in test_cases
        ]

        futures = [
            self.executor.submit(self.run_code, prog, test)
            for prog, test in tasks
        ]

        return [f.result() for f in futures]
```

### 4. Custom Sandbox Image

**Dockerfile for Sandbox:**
```dockerfile
FROM python:3.11-slim

# Install only necessary dependencies
RUN pip install --no-cache-dir numpy scipy

# Create non-root user
RUN useradd -m -u 1000 sandbox
USER sandbox
WORKDIR /home/sandbox

# No shell (prevents interactive attacks)
CMD ["python", "-c", ""]
```

**Build:**
```bash
docker build -t funsearch-sandbox:latest -f Dockerfile.sandbox .
```

## Performance Optimization

### Container Reuse vs. Creation

**Option A: Create/Destroy (Recommended for Security)**
- Spawn new container per evaluation
- Destroy immediately after
- Slower (~500ms overhead) but safest
- No state leakage between runs

**Option B: Container Pool**
- Pre-create N containers
- Reuse for multiple evaluations
- Faster (~50ms overhead) but risk of state leakage
- Must restart containers periodically

**Benchmark:**
```python
# Test container creation overhead
import time
import docker

client = docker.from_env()

# Measure container creation
start = time.time()
for i in range(100):
    c = client.containers.run("python:3.11-slim", "echo 'test'", remove=True)
print(f"Avg creation time: {(time.time() - start) / 100 * 1000:.2f}ms")

# Result: ~400-600ms per container on typical hardware
```

**Optimization Strategy:**
1. **Pre-pull images** at startup (avoid download delays)
2. **Batch evaluations** when possible
3. **Cache test results** (same program + input = same output)
4. **Parallel execution** (8-16 workers for 8-core CPU)

### Resource Limits Tuning

```python
# Conservative limits for untrusted code
SANDBOX_LIMITS = {
    "mem_limit": "256m",      # Enough for most algorithms
    "nano_cpus": 1_000_000_000,  # 1 CPU (prevents resource hogging)
    "timeout": 30,            # 30 seconds max execution
}

# For compute-intensive problems (image processing, etc.)
HEAVY_LIMITS = {
    "mem_limit": "1g",
    "nano_cpus": 2_000_000_000,  # 2 CPUs
    "timeout": 120,
}
```

## Integration with FunSearch

### Evaluator Implementation

```python
# backend/core/docker_evaluator.py
from .evaluator import Evaluator
from .sandbox import SandboxPool

class DockerEvaluator(Evaluator):
    """Concrete evaluator using Docker sandboxing"""

    def __init__(self, max_workers: int = 8):
        self.sandbox = SandboxPool(max_workers=max_workers)

    def evaluate(self, program: str, test_inputs: list) -> float:
        """
        Evaluate a program on multiple test inputs.
        Returns average score across all tests.
        """
        results = self.sandbox.evaluate_population(
            programs=[program],
            test_cases=test_inputs
        )

        # Calculate fitness
        successful = [r["score"] for r in results if r["success"]]

        if not successful:
            return float('-inf')  # Failed all tests

        return sum(successful) / len(successful)
```

### Configuration

```yaml
# .funsearch/project.yaml
evaluator:
  type: "docker"
  max_workers: 8
  container_image: "funsearch-sandbox:latest"
  timeout: 30
  limits:
    memory: "256m"
    cpu_cores: 1
  security:
    network_disabled: true
    read_only: true
```

## Security Checklist

- [x] Network access disabled (`network_disabled=True`)
- [x] Resource limits enforced (CPU, memory, PIDs)
- [x] Read-only filesystem (`read_only=True`)
- [x] No privilege escalation (`no-new-privileges`)
- [x] Timeout enforcement (30s default)
- [x] Non-root user in container
- [x] Minimal base image (no shell, no unnecessary tools)
- [x] Auto-cleanup (`remove=True`)
- [ ] Seccomp profile (future: restrict syscalls)
- [ ] AppArmor/SELinux profile (future: mandatory access control)

## Deployment Considerations

### Development (Local)

```bash
# Run on host for fast iteration
python -m uvicorn app.main:app --reload

# Docker just for sandboxing
# LM Studio on host with GPU
```

### Production (Docker Compose)

```yaml
version: '3.8'
services:
  funsearch-app:
    build: .
    ports:
      - "7351:7351"  # FastAPI backend
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - SANDBOX_MAX_WORKERS=16
      - SANDBOX_IMAGE=funsearch-sandbox:latest
      - PORT=7351
```

### Scaling (Kubernetes - Future)

```yaml
# Use containerd or CRI-O for sandboxing
# gVisor (runsc) as container runtime for extra isolation
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: gvisor  # Extra layer of sandboxing
```

## Monitoring & Debugging

### Container Logs

```python
# Enable logging for debugging
container = client.containers.run(
    ...,
    detach=True,
    stdout=True,
    stderr=True,
)

stdout = container.logs(stdout=True, stderr=False)
stderr = container.logs(stdout=False, stderr=True)
```

### Metrics Collection

```python
# Track sandbox performance
import time

class InstrumentedSandbox(SandboxPool):
    def run_code(self, code: str, test_input: dict) -> dict:
        start = time.time()
        result = super().run_code(code, test_input)
        duration = time.time() - start

        # Log to MLflow
        mlflow.log_metric("sandbox_duration_ms", duration * 1000)
        mlflow.log_metric("sandbox_success", 1 if result["success"] else 0)

        return result
```

## Troubleshooting

### "Permission denied" on Docker socket

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Or run with sudo (not recommended)
```

### "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Verify
docker ps
```

### Containers not being cleaned up

**Solution:**
```bash
# Force remove all stopped containers
docker container prune -f

# In code, always use remove=True or cleanup in finally block
```

### Slow container creation

**Solution:**
```bash
# Pre-pull image
docker pull funsearch-sandbox:latest

# Use smaller base image
FROM python:3.11-alpine  # ~50MB vs ~140MB for slim
```

## References

- [Docker SDK for Python](https://docker-py.readthedocs.io/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [gVisor - Application Kernel for Containers](https://gvisor.dev/)
- [Seccomp Security Profiles](https://docs.docker.com/engine/security/seccomp/)

---

**Last Updated**: 2025-11-16
**Status**: Technical Specification
