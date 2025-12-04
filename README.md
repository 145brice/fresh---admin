# Fresh - Admin Dashboard

Admin dashboard for viewing contractor leads from multiple cities.

## Features

- 📊 View leads from 12+ cities
- 🔐 Password-protected admin access
- 📈 Real-time statistics
- 🗂️ Organized by date and city
- 📋 Sortable tables

## Quick Start

### Local Development

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the admin dashboard
python3 app.py
```

Dashboard will be available at: http://localhost:8083/admin?secret=admin123

### Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/145brice/fresh---admin)

1. Click the deploy button above
2. Set environment variables:
   - `ADMIN_SECRET` - Your admin password
   - `LEADS_PATH` - Path to leads directory (default: `leads`)
3. Add your CSV files to the `leads/` directory

**Note:** For Vercel deployment, you'll need to either:
- Commit your CSV files to the `leads/` directory
- Configure API integration to fetch data from your backend
- Use a cloud storage solution (S3, etc.)

## Configuration

Environment variables:
- `ADMIN_SECRET` - Admin password (default: `admin123`)
- `LEADS_PATH` - Path to leads CSV files (default: `../contractor-leads-backend/leads`)
- `PORT` - Server port (default: `8083`)

Edit `app.py` to configure:
- `CITIES` - List of cities to display

## Default Credentials

- **Admin Secret:** `admin123` (change via `ADMIN_SECRET` environment variable)
- **Port:** 8083

## Data Format

Reads CSV files from structure:
```
leads/{city}/{date}/{date}_{city}.csv
```

Example:
```
leads/
  austin/
    2025-12-04/
      2025-12-04_austin.csv
  chicago/
    2025-12-04/
      2025-12-04_chicago.csv
```

Each CSV should have columns:
- `permit_number` - Permit ID
- `address` - Full address
- `type` - Permit type (residential, commercial, etc.)
- `value` - Permit value/cost
- `state` - State abbreviation (optional)

## Production Deployment

For production use on Vercel or other serverless platforms:

1. **Add sample data** to `leads/` directory and commit to repo
2. **Or configure API integration** to fetch from your backend API
3. **Or use cloud storage** (S3, Google Cloud Storage, etc.)

The current implementation reads from local file system, which works for:
- Local development
- VPS/dedicated server deployment
- Docker containers with mounted volumes

For serverless platforms like Vercel, you'll need one of the alternatives above.
