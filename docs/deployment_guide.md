# RescueMind AI – Deployment Guide

Complete instructions for deploying on Streamlit Cloud, Docker, and Google Cloud Run.

---

## Prerequisites

- Python 3.11+
- Git
- (Optional) Google API key for Gemini — system runs in demo mode without it
- (Optional) Docker for containerized deployment
- (Optional) Google Cloud SDK for Cloud Run

---

## Option 1: Local Development (Fastest — 2 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/rescuemind-ai.git
cd rescuemind-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys (or leave as-is for demo mode)

# 5. Initialize database
python -c "from database.schema import initialize_database; initialize_database()"

# 6. Run the application
streamlit run app.py
```

Open http://localhost:8501 in your browser.

**Demo mode** (no API keys required): Set `DEMO_MODE=true` in `.env` — all agents use intelligent rule-based fallbacks and seeded data. The system is fully functional for demonstration.

---

## Option 2: Streamlit Cloud (Recommended for Kaggle Demo)

The easiest zero-infrastructure deployment.

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial RescueMind AI commit"
git remote add origin https://github.com/YOUR_USERNAME/rescuemind-ai.git
git push -u origin main
```

### Step 2: Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repository
4. Set **Main file path**: `app.py`
5. Click **Advanced settings** → **Secrets**

### Step 3: Add Secrets

In the Streamlit Cloud secrets editor, paste:

```toml
GOOGLE_API_KEY = "your_gemini_api_key"
OPENWEATHER_API_KEY = "your_openweather_key"
DEMO_MODE = "false"
SECRET_KEY = "your-random-secret-key-here"
LOG_LEVEL = "INFO"
```

For pure demo without API keys:
```toml
DEMO_MODE = "true"
SECRET_KEY = "demo-secret-key"
```

### Step 4: Deploy

Click **Deploy**. Your app will be live at:
`https://your-username-rescuemind-ai-app-XXXX.streamlit.app`

**Estimated deployment time:** 3–5 minutes

---

## Option 3: Docker (Self-hosted)

### Build and Run

```bash
# Build the image
docker build -t rescuemind-ai:latest .

# Run with environment variables
docker run -d \
  --name rescuemind \
  -p 8501:8501 \
  -e GOOGLE_API_KEY=your_key \
  -e DEMO_MODE=false \
  -e SECRET_KEY=your_secret \
  -v rescuemind_db:/app/database \
  -v rescuemind_logs:/app/logs \
  rescuemind-ai:latest

# View logs
docker logs -f rescuemind

# Health check
curl http://localhost:8501/_stcore/health
```

### Docker Compose (Recommended)

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Remove volumes (fresh start)
docker-compose down -v
```

Access at http://localhost:8501

---

## Option 4: Google Cloud Run

### Step 1: Set Up Google Cloud

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Store Secrets in Secret Manager

```bash
# Create secrets (more secure than env vars in Cloud Run)
echo -n "your_gemini_api_key" | \
  gcloud secrets create GOOGLE_API_KEY --data-file=-

echo -n "your_secret_key" | \
  gcloud secrets create SECRET_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 3: Build and Push Container

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rescuemind-ai:latest .

# Or use Docker directly
docker build -t gcr.io/YOUR_PROJECT_ID/rescuemind-ai:latest .
docker push gcr.io/YOUR_PROJECT_ID/rescuemind-ai:latest
```

### Step 4: Deploy to Cloud Run

```bash
# Update cloudrun.yaml with your project ID first
sed -i 's/PROJECT_ID/YOUR_PROJECT_ID/g' cloudrun.yaml

# Deploy
gcloud run services replace cloudrun.yaml \
  --region=asia-south1    # Mumbai region for India

# Get service URL
gcloud run services describe rescuemind-ai \
  --region=asia-south1 \
  --format="value(status.url)"
```

### Step 5: Make Public (Optional)

```bash
gcloud run services add-iam-policy-binding rescuemind-ai \
  --region=asia-south1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

**Estimated deployment time:** 8–12 minutes  
**Cost:** ~$0 for low traffic (Cloud Run free tier: 2M requests/month)

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v --tb=short

# Run specific test class
pytest tests/test_rescuemind.py::TestSecurity -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run only fast tests (exclude integration)
pytest tests/ -v -m "not slow"

# Run security tests only
pytest tests/test_rescuemind.py::TestSecurity -v
```

**Expected output:** 60+ tests, all passing in demo mode.

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | No* | — | Gemini API key (*required for live LLM) |
| `OPENWEATHER_API_KEY` | No | — | Weather data API |
| `GOOGLE_MAPS_API_KEY` | No | — | Maps and routing |
| `DEMO_MODE` | No | `true` | Use rule-based fallbacks |
| `SECRET_KEY` | Yes | dev-key | Session security |
| `DATABASE_URL` | No | SQLite | Database connection |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |
| `RATE_LIMIT_REQUESTS` | No | `60` | Requests per minute |
| `MAX_INPUT_LENGTH` | No | `2000` | Max query character length |
| `GEMINI_MODEL` | No | `gemini-1.5-pro` | Primary model |
| `GEMINI_FLASH_MODEL` | No | `gemini-1.5-flash` | Fast model for alerts |

---

## Getting API Keys

### Google Gemini (Free tier available)
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API key** → **Create API key**
3. Copy and add to `.env` as `GOOGLE_API_KEY`
4. Free tier: 60 requests/minute, 1500 requests/day

### OpenWeatherMap (Free tier: 60 calls/minute)
1. Register at [openweathermap.org](https://openweathermap.org/api)
2. Go to **API keys** tab → copy default key
3. Add to `.env` as `OPENWEATHER_API_KEY`

### ReliefWeb (Free, no key needed)
The ReliefWeb API at `https://api.reliefweb.int/v1/` is public — no key required.

---

## Troubleshooting

**App won't start:**
```bash
# Check Python version (needs 3.11+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for import errors
python -c "import streamlit; import google.generativeai"
```

**Database errors:**
```bash
# Reinitialize database
python -c "from database.schema import initialize_database; initialize_database(force_reset=True)"
```

**Gemini API errors:**
```bash
# Test API key
python -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-1.5-flash')
print(model.generate_content('Say hello').text)
"
```

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Docker build fails:**
```bash
# Clear build cache
docker builder prune
docker build --no-cache -t rescuemind-ai:latest .
```

---

## Performance Optimization

For production deployments serving many concurrent users:

1. **Enable Streamlit caching** — `@st.cache_data` on DB queries (already implemented for `init_database`)
2. **Connection pooling** — Replace SQLite with PostgreSQL for high concurrency
3. **Redis rate limiting** — Replace in-memory rate limiter with Redis for multi-instance deployments
4. **CDN** — Serve static assets via CloudFlare or AWS CloudFront
5. **Gemini Flash** — Use `gemini-1.5-flash` for high-volume alert generation (3x faster, lower cost)

---

## Support

- NDMA Emergency: 1079
- National Emergency: 112
- Technical issues: Open a GitHub issue
