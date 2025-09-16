# QR Track Fittings System - Setup Guide

## 🚀 Quick Setup with Your MongoDB URL

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Access to your MongoDB instance

### Step 1: Run the Setup Script

```bash
# Navigate to the project directory
cd /Users/bharani/Rail_backend

# Run the setup script
python3 setup.py
```

This will:
- ✅ Create `.env` file with your MongoDB URL
- ✅ Install all required dependencies
- ✅ Create necessary directories
- ✅ Test database connection

### Step 2: Start the Application

```bash
# Start the FastAPI server
python3 run.py
```

### Step 3: Verify Installation

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Then edit `.env` and update the MongoDB URL:

```env
MONGODB_URL=mongodb://root:Bharani%4090323@62.72.59.3:27017/?authSource=admin
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt
```

### 3. Create Directories

```bash
mkdir -p uploads logs temp
```

### 4. Test Database Connection

```bash
python3 -c "from app.config.database import connect_to_mongo; import asyncio; asyncio.run(connect_to_mongo())"
```

### 5. Start the Application

```bash
python3 run.py
```

## 🐳 Docker Setup (Optional)

If you prefer using Docker:

```bash
# Build the Docker image
docker build -t qr-track-fittings .

# Run with Docker Compose
docker-compose up -d
```

## 📊 Database Configuration

Your MongoDB URL is configured as:
```
mongodb://root:Bharani%4090323@62.72.59.3:27017/?authSource=admin
```

The system will:
- Connect to your MongoDB instance
- Create the database: `qr_track_fittings`
- Set up all required collections and indexes
- Initialize with proper schema validation

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check if your MongoDB server is running
   - Verify the connection string
   - Ensure network access to the MongoDB server

2. **Python Dependencies Issues**
   - Make sure you're using Python 3.8+
   - Try: `pip3 install --upgrade pip`
   - Then: `pip3 install -r requirements.txt`

3. **Port Already in Use**
   - Change the port in `.env` file: `PORT=8001`
   - Or kill the process using port 8000

4. **Permission Issues**
   - Make sure you have write permissions in the project directory
   - Try: `chmod +x setup.py run.py`

### Check Logs

```bash
# View application logs
tail -f logs/app.log

# Check for errors
grep -i error logs/app.log
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python3 run_tests.py

# Run specific test categories
python3 run_tests.py auth
python3 run_tests.py users
python3 run_tests.py qr
```

## 📚 API Usage

### Authentication

1. **Register a user** (if not exists):
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "AdminPass123",
    "role": "admin"
  }'
```

2. **Login**:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123",
    "deviceInfo": {"type": "web"}
  }'
```

3. **Use the token** in subsequent requests:
```bash
curl -X GET "http://localhost:8000/api/users" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🚀 Production Deployment

For production deployment:

1. **Update security settings** in `.env`:
   - Change `SECRET_KEY` to a strong, random key
   - Set `DEBUG=false`
   - Configure proper CORS origins

2. **Use a reverse proxy** (nginx/Apache)

3. **Set up SSL/TLS** certificates

4. **Configure monitoring** and logging

5. **Set up backups** for MongoDB

## 📞 Support

If you encounter any issues:

1. Check the logs: `tail -f logs/app.log`
2. Verify MongoDB connection
3. Check the API documentation: http://localhost:8000/docs
4. Review the troubleshooting section above

## 🎯 Next Steps

Once the system is running:

1. **Explore the API** at http://localhost:8000/docs
2. **Create your first user** and login
3. **Set up zones, divisions, and stations**
4. **Create fitting categories and types**
5. **Start managing supply orders and QR codes**

The system is now ready to handle 10 crore Elastic Rail Clips, 5 crore liners, and 8.5 crore rail pads annually! 🚄
