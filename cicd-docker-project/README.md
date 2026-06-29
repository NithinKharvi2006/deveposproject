# CI/CD Pipeline with GitHub Actions & Docker (No Cloud Needed)

A complete CI/CD pipeline for a small Flask REST API (a "Task Manager" service).
On every push to `main`, GitHub Actions automatically:

1. Installs dependencies and runs the **pytest** suite.
2. If tests pass, builds a **Docker image** and pushes it to **Docker Hub**.
3. The image can then be pulled and run on **Minikube** (or any local VM/Docker host).

---

## Project Structure

```
cicd-docker-project/
├── app/
│   ├── app.py                  # Flask REST API (Task Manager)
│   ├── requirements.txt        # Runtime dependencies
│   ├── requirements-dev.txt    # Test-only dependencies (pytest)
│   └── tests/
│       └── test_app.py         # pytest test suite (8 tests)
├── Dockerfile                  # Builds the app image
├── docker-compose.yml          # Local build + run
├── .github/workflows/ci-cd.yml # GitHub Actions CI/CD pipeline
├── k8s/
│   ├── deployment.yaml         # Minikube Deployment
│   └── service.yaml            # Minikube NodePort Service
├── .dockerignore
└── .gitignore
```

## The API

| Method | Endpoint        | Description           |
|--------|-----------------|------------------------|
| GET    | `/health`       | Health check           |
| GET    | `/tasks`        | List all tasks         |
| POST   | `/tasks`        | Create a task          |
| GET    | `/tasks/<id>`   | Get one task           |
| PUT    | `/tasks/<id>`   | Update a task          |
| DELETE | `/tasks/<id>`   | Delete a task          |

---

## 1. Run locally (no Docker)

```bash
cd app
pip install -r requirements.txt -r requirements-dev.txt
pytest tests -v          # run the test suite
python app.py            # starts on http://localhost:5000
```

## 2. Run with Docker

```bash
docker build -t task-manager-api:local .
docker run -p 5000:5000 task-manager-api:local
```

Or with Docker Compose:

```bash
docker compose up --build
```

Test it:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/tasks
```

---

## 3. Push this project to GitHub

```bash
git init
git add .
git commit -m "Initial commit: CI/CD pipeline with GitHub Actions & Docker"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 4. Configure GitHub Actions secrets (one-time setup)

The workflow needs to log in to Docker Hub to push the built image.
In your GitHub repo go to: **Settings → Secrets and variables → Actions → New repository secret**, and add:

| Secret name          | Value                                              |
|-----------------------|----------------------------------------------------|
| `DOCKERHUB_USERNAME`  | Your Docker Hub username                            |
| `DOCKERHUB_TOKEN`     | A Docker Hub **access token** (Account Settings → Security → New Access Token) — do not use your raw password |

Once these secrets exist, every push to `main` will:
- Run the test job (`test`)
- Build & push `task-manager-api:latest` and `task-manager-api:<commit-sha>` to Docker Hub (`build-and-push` job)

You can watch this happen under the **Actions** tab of your repo.

---

## 5. Deploy the built image with Minikube (local Kubernetes)

```bash
# Start Minikube
minikube start

# Edit k8s/deployment.yaml and replace <dockerhub-username> with your
# actual Docker Hub username so it points at the image GitHub Actions pushed.

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl get pods
kubectl get svc

# Open the app in the browser
minikube service task-manager-api-service
```

### Alternative: plain Docker on a local VM (no Kubernetes)

```bash
docker pull <your-dockerhub-username>/task-manager-api:latest
docker run -d -p 5000:5000 <your-dockerhub-username>/task-manager-api:latest
```

---

## How the pipeline works (for your interview / report)

1. **Trigger** – any `git push` to `main` (or a PR targeting `main`) triggers the workflow defined in `.github/workflows/ci-cd.yml`.
2. **Test job** – spins up an Ubuntu runner, installs dependencies, and runs the `pytest` suite (8 tests covering all CRUD endpoints + health check). If any test fails, the pipeline stops here — nothing broken ever gets built into an image.
3. **Build & push job** – runs only if `test` succeeded **and** the trigger was a push to `main`. It uses `docker/build-push-action` to build the image from the `Dockerfile` and pushes two tags to Docker Hub: `latest` and the commit SHA (so you always have an immutable, traceable version of every deployment).
4. **Deploy** – on the target machine (Minikube or a local VM), you simply pull the freshly built image and run it — no manual rebuilding required.

This demonstrates the core DevOps idea: **code change → automated test → automated build → automated, repeatable deployment**, entirely with free tools and no cloud cost.

## Suggested deliverables to capture for submission
- Screenshot of the green checkmarks on the **Actions** tab after a push to `main`.
- Screenshot of the pushed image on your Docker Hub repository page.
- Screenshot of `kubectl get pods` / `minikube service` output (or `docker ps` if you used the plain-Docker route).
- A short screen recording or screenshots of `curl`/Postman hitting the running API.
