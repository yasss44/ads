# Flask Location Manager

A simple Flask web application for managing geographical locations with user authentication.

## 🏗️ Architecture

- **Flask Application**: Python 3.10 with SQLite database
- **Authentication**: User registration/login system with role-based access
- **Frontend**: Bootstrap-based responsive interface
- **Database**: SQLite (simple, no complex setup required)

## 📋 Prerequisites

- Python 3.10+ installed and in PATH
- Git (optional, for version control)

## 🚀 Quick Start

1. **Start the application:**
   ```cmd
   start.cmd
   ```
   This will:
   - Create a virtual environment
   - Install dependencies
   - Set up the SQLite database
   - Start the development server

2. **Access application:**
   - Main app: http://localhost:5000
   - **Quick Demo**: Use the demo account buttons on login page
   - Or register a new user account

## 📁 Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start.cmd             # Simple startup script
├── .env                  # Environment variables
├── create_demo_users.py  # Demo user creation
├── templates/            # HTML templates
│   ├── index.html        # Main interface
│   ├── login.html        # Login page
│   └── dashboard.html    # User dashboard
├── static/               # CSS and JavaScript
│   ├── css/
│   └── js/
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration (SQLite for simplicity)
DATABASE_URL=sqlite:///dev.db

# CORS (allow all origins in development)
CORS_ORIGINS=*
```

## 🎆 Features

### 🔐 Authentication System
- User registration and login
- **Demo accounts** with secure one-click login (dynamically loaded from database)
- Password hashing with bcrypt
- **Role-based access control**:
  - **Admin**: Full system access (manage users, locations, campaigns, devices)
  - **Client**: Campaign management + view locations/devices
  - **Viewer**: Read-only access to all data
- Session management with activity logging

### 📍 Location Management
- **Enhanced location data**: Name, description, address, coordinates, status
- **Location status tracking**: Active, inactive, maintenance
- **Creator tracking**: Know who created each location
- **Device association**: Link devices to specific locations
- **Admin-only creation/editing** for data integrity

### 📢 Campaign Management
- **Complete campaign lifecycle**: Draft → Active → Paused → Completed
- **Budget tracking** with financial oversight
- **Client assignment**: Assign campaigns to specific clients
- **Target audience definition** for precise marketing
- **Date range management**: Start and end date planning
- **Admin creation, client visibility** based on assignments

### 🖥️ Device Management
- **Real-time device monitoring**: Online, offline, maintenance, error states
- **Device types**: Display, sensor, kiosk, camera, and more
- **Hardware tracking**: Serial numbers, firmware versions, IP addresses
- **Location assignment**: Associate devices with specific locations
- **Last seen timestamps** for connectivity monitoring
- **Status updates** with automatic timestamping

### 📊 Activity Logging & Audit Trail
- **Comprehensive user activity tracking**
- **IP address and user agent logging**
- **Action-specific details** for security and compliance
- **Admin-only access** to activity logs
- **Real-time activity feed** in dashboard

### User Interface
- Responsive Bootstrap design
- Interactive forms with validation
- Real-time notifications
- Dark theme support

## 🛠️ Development Commands

### Manual Setup (Alternative to start.cmd)
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

### Database Management
```cmd
# Create demo users (after starting app)
python create_demo_users.py

# Reset database (delete dev.db file)
del dev.db
python app.py  # Will recreate tables

# Access Python shell with app context
python -c "from app import app, db; app.app_context().push(); print('Database ready')"
```

## 🔍 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - User login
- `GET /logout` - User logout
- `GET /register` - Registration page
- `POST /register` - User registration

### Locations
- `GET /` - Main dashboard (requires login)
- `GET /api/locations` - List all locations (all authenticated users)
- `POST /api/locations` - Create new location (**admin only**)
- `GET /api/locations/{id}` - Get specific location (all authenticated users)
- `GET /health` - Application health check (public)

## 🛡️ Security Features

- **Password Hashing**: bcrypt for secure password storage
- **Session Management**: Flask sessions for user authentication
- **Role-based Access**: Different user roles (admin, client, viewer)
- **CSRF Protection**: Built-in Flask security features
- **Input Validation**: Form validation and sanitization

### Example API Usage
```bash
# Health check
curl http://localhost:5000/health

# Create location (requires login session)
curl -X POST http://localhost:5000/api/locations \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Location", "latitude": 40.7128, "longitude": -74.0060}'

# Get locations
curl http://localhost:5000/api/locations
```

## 😨 Troubleshooting

### Common Issues

**Python not found:**
- Install Python 3.10+ from https://python.org
- Add Python to your PATH environment variable

**Port already in use:**
- Stop any other web servers running on port 5000
- Or change the port in app.py: `app.run(host='0.0.0.0', port=5001)`

**Dependencies installation fails:**
- Check internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`

**Database errors:**
- Delete `dev.db` file to reset database
- Restart the application

## 📄 Technology Stack

**Backend:**
- Flask 2.3.3 (Python web framework)
- SQLAlchemy (Database ORM)
- Flask-CORS (Cross-origin support)
- Flask-Bcrypt (Password hashing)
- SQLite (Database)

**Frontend:**
- HTML5 + Bootstrap 5
- Font Awesome icons
- Vanilla JavaScript

**Development:**
- Python 3.10+
- Virtual environment (venv)

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the application logs in your terminal
