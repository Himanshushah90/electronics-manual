# Electronics Manual

A web application for electronics documentation with admin panel.

## Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/electronics-manual.git
cd electronics-manual
```

2. Set up the backend
```bash
cd backend/admin
pip install -r requirements.txt
python run.py
```

3. Set up the frontend
```bash
cd frontend
pip install -r requirements.txt
python run.py
```

4. Create .env files:

Frontend (.env):
```
MONGO_URI=your_mongodb_uri
```

Backend (.env):
```
MONGO_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

## Usage
- Frontend runs on: http://localhost:5001
- Admin login: http://localhost:5002/auth/login

## Features
- Document Management
- Category Organization
- Markdown Support
- Admin Panel