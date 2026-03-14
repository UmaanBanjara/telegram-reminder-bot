# ⏰ RemindMe Bot

> A personal Telegram reminder bot — set reminders, get notified on time, never forget anything again.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📌 Note

> This project is **not hosted on any public server**.
> You can run it **locally on your own machine** using Docker,
> or deploy it to any server of your choice.

---

## ✨ Features

- ⏰ Set reminders with a custom message and time
- 📋 View all your pending and sent reminders
- 🗑 Delete reminders you no longer need
- 🇳🇵 All times handled in **Nepal Time (NPT)**
- 🔔 Automatic Telegram notifications via background scheduler
- 🛡 Rate limiting per IP using Redis
- 🐳 Fully Dockerized — one command to run everything

---

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API backend — handles all reminder and user logic |
| **python-telegram-bot (PTB)** | Telegram bot — handles commands and sends notifications |
| **PostgreSQL** | Persistent database — stores users and reminders |
| **Redis** | Rate limiting — prevents API abuse (5 requests/minute per IP) |
| **SlowAPI** | Rate limiting middleware for FastAPI using Redis |
| **APScheduler** | Background job scheduler — checks and fires reminders every 30 seconds |
| **SQLAlchemy** | Async ORM — communicates with PostgreSQL |
| **Docker + Docker Compose** | Containerization — runs all services together |
| **python-dotenv** | Loads environment variables from `.env` file |

---

## 📁 Folder Structure
```
remind_me/
├── app/
│   ├── api/
│   │   └── app_routes.py         # FastAPI route handlers
│   ├── apscheduler/
│   │   └── apscheduler_config.py # Background reminder scheduler
│   ├── bot/
│   │   └── telegram_bot.py       # Telegram bot commands and handlers
│   ├── database/
│   │   ├── connection_config.py  # SQLAlchemy engine and session
│   │   └── create_tables.py      # Table creation script
│   ├── models/
│   │   └── app_models.py         # SQLAlchemy models (Users, Remainder)
│   ├── redis/
│   │   └── redis_config.py       # Redis client and rate limiter setup
│   └── utils/
│       └── app_validations.py    # Pydantic request validation models
├── main.py                       # FastAPI app entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed)
├── .dockerignore                 # Files to exclude from Docker build
├── .gitignore                    # Files to exclude from Git
├── Dockerfile.api                # Docker image for FastAPI
├── Dockerfile.bot                # Docker image for Telegram bot
├── docker-compose.yml            # Orchestrates all services
└── README.md
```

---

## 🐳 Docker Services
```
┌─────────────────────────────────────────────────┐
│                 docker-compose                  │
│                                                 │
│  ┌─────────────┐         ┌─────────────────┐   │
│  │  postgres   │         │      redis      │   │
│  │  port:5432  │         │   port: 6379    │   │
│  └──────┬──────┘         └────────┬────────┘   │
│         │                         │            │
│  ┌──────▼─────────────────────────▼────────┐   │
│  │              api (FastAPI)              │   │
│  │              port: 8000                 │   │
│  └──────────────────┬──────────────────────┘   │
│                     │                          │
│  ┌──────────────────▼──────────────────────┐   │
│  │         bot (Telegram + Scheduler)      │   │
│  │         runs in background              │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

| Service | Description | Port |
|---|---|---|
| `postgres` | PostgreSQL database | `5432` |
| `redis` | Redis for rate limiting | `6379` |
| `api` | FastAPI backend | `8000` |
| `bot` | Telegram bot + APScheduler | — |

---

## 🚀 Getting Started

### ✅ Prerequisites

Make sure you have these installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

---

### 1. Clone the repository
```bash
git clone https://github.com/UmaanBanjara/telegram-reminder-bot
cd app
```

---

### 2. Create your `.env` file

Create a file named `.env` in the root of the project:
```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=postgresql+asyncpg://remind_me_user:thankyou@postgres/remind_me
API_MACHINE=http://api:8000/api
REDIS_URL=redis://redis:6379/0
```

> ⚠️ Never commit your `.env` file to Git. It's already in `.gitignore`.

---

### 3. Build and run
```bash
docker-compose up --build
```

Run in background:
```bash
docker-compose up --build -d
```

---

### 4. Stop everything
```bash
docker-compose down
```

---

### 5. View logs
```bash
# All services
docker-compose logs -f

# Only the bot
docker-compose logs -f bot

# Only the API
docker-compose logs -f api
```

---

## 📖 Bot Commands

| Command | Description |
|---|---|
| `/start` | Register and open the main menu |
| `/remind <message> <YYYY-MM-DDTHH:MM:SS>` | Create a new reminder |
| `/list` | View all your reminders |
| `/delete <id>` | Delete a reminder by ID |
| `/help` | Show help and usage guide |
| `/about` | About this bot and the creator |

### Example
```
/remind Call John 2026-03-15T09:00:00
/remind Buy groceries 2026-03-20T18:30:00
```

> 🇳🇵 All times are in **Nepal Time (NPT)**

---

## 🏗 Architecture
```
┌─────────────┐     ┌──────────────────────┐
│  Telegram   │────▶│   Telegram Bot (PTB) │
│  User       │◀────│   telegram_bot.py    │
└─────────────┘     └──────────┬───────────┘
                               │ HTTP requests
                    ┌──────────▼───────────┐
                    │   FastAPI Backend    │
                    │   main.py            │
                    │   app_routes.py      │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
   ┌──────────▼──┐   ┌─────────▼──────┐  ┌──────▼───────────┐
   │ PostgreSQL  │   │     Redis      │  │   APScheduler    │
   │ Users &     │   │ Rate Limiting  │  │ Checks reminders │
   │ Reminders   │   │ 5 req/minute   │  │ every 30 seconds │
   └─────────────┘   └────────────────┘  └──────────────────┘
```

---

## ⚙️ How the Scheduler Works
```
Every 30 seconds
      ↓
Query DB for reminders where:
  is_sent = false AND scheduled_time <= now (UTC)
      ↓
Send Telegram message to user
      ↓
Mark reminder as is_sent = true
Mark sent_at = current UTC time
```

---

## 👨‍💻 Author

**Umaan Banjara**

- 📧 Email: umaanbanjara@gmail.com
- 🐙 GitHub: [github.com/UmaanBanjara](https://github.com/UmaanBanjara/)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify and distribute it.

---

> Built with ❤️ by Umaan Banjara