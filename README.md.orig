# 🚀 coin prelisting analyst app - Backend

A production-ready backend system that assists cryptocurrency exchanges in selecting new coins for listing based on market data, developer activity, and sentiment analysis.

---

## 📌 Features

✅ Periodic data fetching from:
- CoinGecko (market data)
- GitHub (developer activity)
- Twitter (community sentiment)
- Reddit (community discussions)

✅ Scoring algorithm with adjustable weights  
✅ Role-Based Access Control (RBAC) for Analysts & Managers  
✅ Slack notifications for pending coin suggestions  
✅ Soft delete functionality for data integrity  
✅ Celery for scheduled background jobs  
✅ API endpoints for managing users, coins, metrics, and suggestions  
✅ Fully tested with Pytest and integrated with FastAPI  

---

## 🛠️ Tech Stack

| Component       | Technology        |
|----------------|------------------|
| Backend        | FastAPI           |
| Database       | PostgreSQL        |
| ORM            | SQLAlchemy / SQLModel |
| Task Queue     | Celery + Redis    |
| Authentication | JWT + OAuth2      |
| Caching        | Redis             |
| Deployment     | Docker            |

---

## 🏗️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/zmomz/coin_prelisting_analyst.git
cd coin_prelisting_analyst/backend
```

### 2️⃣ Create & Configure `.env` File

Copy the `.env.example` file and update the required credentials:

```bash
cp .env.example .env
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Database Migrations

```bash
<<<<<<< HEAD
python alembic.y upgrade head
=======
python alembic.py upgrade head
>>>>>>> b5a58ff526cfbc7d1eef69bb7c330e94c35fa3f7
```

### 5️⃣ Start the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6️⃣ Start Celery Workers

```bash
celery -A app.celery_app worker --loglevel=info
celery -A app.celery_app beat --loglevel=info
```

---

## 📡 API Documentation

Once the server is running, you can access the API documentation:

- **Swagger UI** → [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Redoc UI** → [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## 🧪 Running Tests

To run the full test suite, execute:

```bash
pytest
```

For test coverage:

```bash
pytest --cov=app
```

---

## 🐳 Docker Deployment

Build and run the project using Docker:

```bash
docker-compose up --build
```

---

## 👥 User Roles

| Role             | Permissions |
|-----------------|------------|
| **Analyst**     | View coins, analyze data, submit suggestions, comment on coins |
| **Manager**     | All Analyst permissions + approve/reject suggestions, adjust scoring algorithm, manage users |

---
<<<<<<< HEAD

backend/ 
├── app/  # Main FastAPI app directory
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── tasks/
│   ├── utils/
│   ├── __init__.py
│   ├── main.py
│   ├── celery-app.py
├── tests/
├── migrations/
├── venv/
├── .env
├── docker-compose.yml
└── dockerfile
=======
>>>>>>> b5a58ff526cfbc7d1eef69bb7c330e94c35fa3f7
