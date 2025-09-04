# LBM Arena - Render.com Deployment Guide

This guide will help you deploy LBM Arena to Render.com with both backend API and frontend.

## Prerequisites

1. **Render.com account** - Sign up at [render.com](https://render.com)
2. **GitHub repository** - Your code should be pushed to GitHub
3. **Supabase account** - For the PostgreSQL database
4. **API Keys** - OpenAI and/or Anthropic API keys (optional but recommended)

## Database Behavior

**🔒 Safe Production Deployment**: 

- **Tables**: Created if they don't exist (safe operation)
- **Data**: No test data added in production - database starts empty
- **User Data**: All data comes from actual user interactions via the frontend
- **Existing Data**: Never touched or overwritten during deployments

### Database Scripts:

- `scripts/init_db_safe.py` - Production safe (only creates tables, no data)
- `dev/scripts/setup_complete_db.py` - Development only (⚠️ drops all data!)
- `dev/scripts/recreate_db.py` - Development only (⚠️ drops all tables!)

**✅ Production Ready**: Your production database will start completely empty and only be populated through real user interactions.

### 1. Prepare Your Database (Supabase)

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Go to **Settings** → **Database** 
3. Copy your **Connection String** (it looks like: `postgresql://postgres:[password]@[host]:5432/[db-name]`)
4. Keep this handy - you'll need it for the Render environment variables

### 2. Deploy to Render

1. **Fork/Clone this repository** to your GitHub account
2. **Connect to Render:**
   - Go to [render.com](https://render.com) and sign in
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub account and select this repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables:**
   During deployment, Render will ask you to set these environment variables:
   
   **Required:**
   - `DATABASE_URL` - Your Supabase PostgreSQL connection string
   
   **Optional (but recommended):**
   - `OPENAI_API_KEY` - Your OpenAI API key for GPT models
   - `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude models

4. **Deploy:**
   - Click **"Apply"** to start the deployment
   - Render will create:
     - **Backend API** service (`lbm-arena-backend`)
     - **Frontend** static site (`lbm-arena-frontend`) 
     - **Redis** service for caching

### 3. Access Your Application

After deployment (5-10 minutes):

- **Backend API**: `https://lbm-arena-backend.onrender.com`
- **Frontend**: `https://lbm-arena-frontend.onrender.com`
- **API Docs**: `https://lbm-arena-backend.onrender.com/docs`

### 4. Test Your Deployment

1. Visit your frontend URL
2. Click **"Run All Tests"** button
3. All tests should show **PASS**:
   - Health: PASS
   - Players: PASS 
   - Games: PASS
   - Chess: PASS

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | ✅ | `postgresql://postgres:password@host:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key for GPT models | ❌ | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude models | ❌ | `sk-ant-...` |

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Static)      │───▶│   (Python)      │───▶│   (Supabase)    │
│   Render        │    │   Render        │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   (Render)      │
                       └─────────────────┘
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Verify your `DATABASE_URL` is correct
   - Check Supabase project is running
   - Ensure IP allowlist includes Render IPs (or set to allow all)

2. **API Key Errors**
   - API keys are optional for basic functionality
   - Check environment variables are set correctly
   - Verify keys are valid and have sufficient credits

3. **Build Failures**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

### Getting Help:

- Check Render service logs in the dashboard
- Visit the backend `/health` endpoint to verify it's running
- Test individual API endpoints using the `/docs` interface

## Local Development

To run locally after deployment:

```bash
# Clone the repo
git clone <your-repo-url>
cd lbm-arena

# Set up environment
cp .env.example .env
# Edit .env with your database URL and API keys

# Run locally
./dev/dev.sh
```

## Cost Estimate

Render.com pricing (as of 2024):
- **Backend Web Service**: $7/month (starter plan)
- **Frontend Static Site**: Free
- **Redis Service**: $7/month (starter plan)
- **Total**: ~$14/month

Plus Supabase database costs (has generous free tier).

---

**🎉 Your LBM Arena is now deployed and ready for AI model battles!**
