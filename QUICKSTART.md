# Quick Start Guide

This guide provides step-by-step instructions to get the Pineapple Lead API up and running quickly.

## Prerequisites

- Python 3.8 or higher
- Git
- A text editor

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd pineapple-lead-api
```

## Step 2: Set Up the Environment

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the virtual environment

Windows:

```bash
.\venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

1. Copy the example environment file:

   ```bash
   cp app/.env.example app/.env
   ```

2. Edit the `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key
   API_BEARER_TOKEN=KEY=your_key SECRET=your_secret
   # ... other variables
   ```

## Step 4: Validate Environment Setup

Run the validation tool to check if everything is configured correctly:

```bash
python validate_env.py
```

This will check if all required environment variables are set and properly formatted.

## Step 5: Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see output similar to:
