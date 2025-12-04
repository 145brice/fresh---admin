# Fresh - Admin Dashboard

Admin dashboard for viewing contractor leads from multiple cities.

## Features

- 📊 View leads from 12+ cities
- 🔐 Password-protected admin access
- 📈 Real-time statistics
- 🗂️ Organized by date and city
- 📋 Sortable tables

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the admin dashboard
python3 admin.py
```

Dashboard will be available at: http://localhost:8083/admin?secret=admin123

## Configuration

Edit `admin.py` to configure:
- `ADMIN_SECRET` - Admin password (default: admin123)
- `CITIES` - List of cities to display
- `LEADS_PATH` - Path to leads CSV files

## Default Credentials

- **Admin Secret:** `admin123`
- **Port:** 8083

## Data Format

Reads CSV files from structure:
```
../contractor-leads-backend/leads/{city}/{date}/{date}_{city}.csv
```

Each CSV should have columns:
- `permit_number`
- `address`
- `type`
- `value`
- `state` (optional)
