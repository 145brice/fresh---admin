# Leads Data Directory

For local development, place your CSV files here in the structure:
```
leads/{city}/{date}/{date}_{city}.csv
```

For production deployment on Vercel:
- This directory won't have access to your local leads
- You need to either:
  1. Commit sample CSV files to this directory
  2. Configure API integration to fetch leads from your backend
  3. Use a database or cloud storage solution

Example structure:
```
leads/
  austin/
    2025-12-04/
      2025-12-04_austin.csv
```

