# 🚀 Development Guide

This guide helps you quickly set up and run the Flask Location Manager.

## 📋 Prerequisites

- Python 3.10+ installed and in PATH
- Git (optional, for version control)

## 🏃‍♂️ Quick Start

### Simple Startup
```cmd
start.cmd
```

## 🔧 What the Script Does

1. **Check Python installation**
2. **Create virtual environment** (if it doesn't exist)
3. **Activate virtual environment**
4. **Install dependencies** from `requirements.txt`
5. **Set development environment variables**:
   - `FLASK_ENV=development`
   - `FLASK_DEBUG=True`
   - `DATABASE_URL=sqlite:///dev.db` (SQLite database)
   - `SECRET_KEY=dev-secret-key`
6. **Create database tables**
7. **Start Flask development server** on http://localhost:5000

## 🌐 Access Points

Once the server is running:

- **Main app**: http://localhost:5000 (redirects to login)
- **Login**: http://localhost:5000/login
- **Register**: http://localhost:5000/register
- **Health check**: http://localhost:5000/health
- **API endpoints**: http://localhost:5000/api/locations

## 📊 First Time Setup

1. Run `start.cmd` to start the application
2. Go to http://localhost:5000
3. **Quick Demo**: Use the demo account buttons on login page:
   - **Admin**: Full system access (create/manage locations, users)
   - **Client**: View-only access to locations and analytics
   - **Viewer**: View-only access to locations and analytics
   - Demo accounts are securely loaded from the database
4. Or click "Register" to create a new account
5. Start adding locations!

### Testing the API
```bash
# Health check
curl http://localhost:5000/health

# Get all locations
curl http://localhost:5000/api/locations
```

## 🗂️ Development Features

### Database
- **SQLite**: Simple file-based database (`dev.db`)
- **Auto-created**: Tables created automatically on first run
- **Reset**: Delete `dev.db` file to start fresh

### Environment
- **Auto-reload**: Server restarts on code changes
- **Debug mode**: Detailed error pages
- **User Authentication**: Register/login system

## 🛠️ Development Commands

### Manual Setup (if start.cmd doesn't work)
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Database operations
```cmd
# Reset database
del dev.db

# Create demo users
python create_demo_users.py
```

## 📁 Key Files

- `start.cmd` - Simple startup script
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `.env` - Environment variables
- `dev.db` - SQLite database (created automatically)
- `create_demo_users.py` - Demo user creation

## 🚨 Troubleshooting

### Python not found
- Install Python 3.10+ from python.org
- Add Python to your PATH environment variable

### Port already in use
- Stop any other web servers running on port 5000
- Or change port in app.py

### Database errors
- Delete `dev.db` file to reset database
- Restart the application

## 📝 Tips

1. **Keep the terminal open** - The development server runs in the foreground
2. **Use Ctrl+C** to stop the server
3. **Check logs** in the terminal for debugging
4. **Register first** - Create an account before using the app
5. **Code changes** are automatically reloaded (no restart needed)
