#!/usr/bin/env python3
"""
Fresh Admin Dashboard
Displays contractor leads from multiple cities
"""

from flask import Flask, render_template_string, request, make_response, redirect
import pandas as pd
import os
import datetime

app = Flask(__name__)

# Configuration
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'admin123')
CITIES = ['nashville', 'chattanooga', 'austin', 'sanantonio', 'houston', 'charlotte',
          'phoenix', 'dallas', 'raleigh', 'philadelphia', 'seattle', 'chicago']
# Path to leads data - can be configured via environment variable
LEADS_PATH = os.getenv('LEADS_PATH', '../contractor-leads-backend/leads')

# Admin Login Template
ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Contractor Leads</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 30px; }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            font-size: 16px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn:hover { opacity: 0.9; }
        .error {
            background: #fee;
            color: #c33;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>Admin Login</h1>
        <p>View all scraped data across all cities</p>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/admin/login">
            <input type="password" name="secret" placeholder="Admin Secret" required autofocus>
            <button type="submit" class="btn">Access Admin Dashboard</button>
        </form>
    </div>
</body>
</html>
'''

# Admin Dashboard Template (copy from backend.py lines 505-890)
ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Fresh Contractor Leads</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #f8fafc;
            color: #1e293b;
        }
        .header {
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { margin: 0; }
        .logout-btn {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 14px;
        }
        .logout-btn:hover { background: rgba(255,255,255,0.3); }

        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number { font-size: 32px; font-weight: 800; color: #dc2626; }
        .stat-label { color: #64748b; margin-top: 5px; }

        .section {
            background: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .section-header {
            background: #f1f5f9;
            padding: 15px 20px;
            border-bottom: 1px solid #e2e8f0;
            font-weight: 600;
            color: #374151;
        }

        .city-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .city-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }
        .city-header {
            background: #f8fafc;
            padding: 12px 15px;
            font-weight: 600;
            color: #374151;
            border-bottom: 1px solid #e2e8f0;
        }
        .city-stats {
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
        }

        .leads-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        .leads-table th {
            background: #f8fafc;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e2e8f0;
            cursor: pointer;
            user-select: none;
        }
        .leads-table th:hover { background: #e2e8f0; }
        .leads-table th.sort-asc::after {
            content: ' ▲';
            font-size: 12px;
            color: #dc2626;
        }
        .leads-table th.sort-desc::after {
            content: ' ▼';
            font-size: 12px;
            color: #dc2626;
        }
        .leads-table td {
            padding: 8px 10px;
            border-bottom: 1px solid #f1f5f9;
        }
        .leads-table tr:hover { background: #f8fafc; }

        .permit-number { font-weight: 600; color: #dc2626; }
        .address { color: #374151; }
        .permit-type {
            background: #fee2e2;
            color: #991b1b;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 600;
        }
        .value { font-weight: 700; color: #059669; }

        .no-data {
            text-align: center;
            padding: 40px;
            color: #64748b;
        }

        @media (max-width: 768px) {
            .header { flex-direction: column; gap: 10px; text-align: center; }
            .stats { grid-template-columns: 1fr; }
            .city-grid { grid-template-columns: 1fr; }
            .leads-table { font-size: 12px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 Fresh Admin Dashboard - All Contractor Leads</h1>
        <a href="/admin?logout=1" class="logout-btn">Logout</a>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ cities|length }}</div>
                <div class="stat-label">Total Cities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_leads }}</div>
                <div class="stat-label">Total Leads Scraped</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ all_leads|length }}</div>
                <div class="stat-label">Days of Data</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">
                    {% set active_cities = 0 %}
                    {% for city, data in cities_data.items() %}
                        {% if data.leads %}
                            {% set active_cities = active_cities + 1 %}
                        {% endif %}
                    {% endfor %}
                    {{ active_cities }}
                </div>
                <div class="stat-label">Active Cities</div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">📊 City Overview</div>
            <div class="city-grid">
                {% for city, data in cities_data.items() %}
                <div class="city-card">
                    <div class="city-header">{{ city.title() }}</div>
                    <div class="city-stats">
                        <span>{{ data.leads|length }} leads</span>
                        <span>{{ data.files|length }} files</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        {% if all_leads %}
        <div class="section">
            <div class="section-header">📋 All Leads by Date</div>
            {% for date, cities in all_leads.items() %}
            <div style="margin-bottom: 30px;">
                <h3 style="padding: 15px 20px; background: #f8fafc; margin: 0; border-bottom: 1px solid #e2e8f0;">{{ date }}</h3>

                {% for city, leads in cities.items() %}
                <div style="border-left: 4px solid #dc2626; background: #fef2f2; margin: 10px 20px;">
                    <div style="padding: 10px 15px; font-weight: 600; color: #dc2626;">{{ city.title() }} ({{ leads|length }} leads)</div>

                    <table class="leads-table">
                        <thead>
                            <tr>
                                <th>City</th>
                                <th>State</th>
                                <th>Permit #</th>
                                <th>Address</th>
                                <th>Type</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for lead in leads[:100] %}
                            <tr>
                                <td><span class="city-name">{{ city.title() }}</span></td>
                                <td><span class="state-name">{{ lead.get('state', 'N/A') }}</span></td>
                                <td><span class="permit-number">{{ lead.permit_number }}</span></td>
                                <td><span class="address">{{ lead.address }}</span></td>
                                <td><span class="permit-type">{{ lead.type }}</span></td>
                                <td><span class="value">{{ lead.value }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>
        {% else %}
            <div class="no-data">
                <h3>No leads data found</h3>
                <p>Check the leads path configuration.</p>
            </div>
        {% endif %}
    </div>

    <script>
        // Table sorting functionality
        document.addEventListener('DOMContentLoaded', function() {
            function sortTable(table, column, asc = true) {
                const dirModifier = asc ? 1 : -1;
                const tBody = table.tBodies[0];
                const rows = Array.from(tBody.querySelectorAll("tr"));

                // Sort each row
                const sortedRows = rows.sort((a, b) => {
                    const aColText = a.querySelector(`td:nth-child(${column + 1})`).textContent.trim();
                    const bColText = b.querySelector(`td:nth-child(${column + 1})`).textContent.trim();

                    // Try to parse as number for value column (index 5)
                    if (column === 5) {
                        const aVal = parseFloat(aColText.replace(/[$,]/g, '')) || 0;
                        const bVal = parseFloat(bColText.replace(/[$,]/g, '')) || 0;
                        return aVal > bVal ? dirModifier : aVal < bVal ? -dirModifier : 0;
                    }

                    // String comparison for other columns
                    return aColText > bColText ? dirModifier : aColText < bColText ? -dirModifier : 0;
                });

                // Remove all existing TRs from tbody
                while (tBody.firstChild) {
                    tBody.removeChild(tBody.firstChild);
                }

                // Re-add the newly sorted rows
                tBody.append(...sortedRows);

                // Update sort indicators
                table.querySelectorAll("th").forEach(th => th.classList.remove("sort-asc", "sort-desc"));
                table.querySelector(`th:nth-child(${column + 1})`).classList.toggle("sort-asc", asc);
                table.querySelector(`th:nth-child(${column + 1})`).classList.toggle("sort-desc", !asc);
            }

            // Add click handlers to all table headers
            document.querySelectorAll(".leads-table th").forEach(headerCell => {
                headerCell.addEventListener("click", () => {
                    const tableElement = headerCell.parentElement.parentElement.parentElement;
                    const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
                    const currentIsAscending = headerCell.classList.contains("sort-asc");

                    sortTable(tableElement, headerIndex, !currentIsAscending);
                });
            });
        });
    </script>
</body>
</html>
'''

@app.route('/admin')
def admin_dashboard():
    # Handle logout
    if request.args.get('logout'):
        response = make_response(redirect('/admin'))
        response.delete_cookie('admin_secret')
        return response

    # Check admin authentication
    admin_secret = request.cookies.get('admin_secret') or request.args.get('secret')
    if admin_secret != ADMIN_SECRET:
        return render_template_string(ADMIN_LOGIN_TEMPLATE)

    # Get all CSV files from all cities
    all_leads = {}
    total_leads = 0
    cities_data = {}

    for city in CITIES:
        city_path = os.path.join(LEADS_PATH, city)
        if os.path.exists(city_path):
            # Look for all date directories
            date_dirs = [d for d in os.listdir(city_path)
                        if os.path.isdir(os.path.join(city_path, d)) and d.startswith('2025-')]
            csv_files = []
            for date_dir in sorted(date_dirs, reverse=True):
                dir_path = os.path.join(city_path, date_dir)
                dir_files = [os.path.join(date_dir, f) for f in os.listdir(dir_path) if f.endswith('.csv')]
                csv_files.extend(dir_files)
            cities_data[city] = {'files': csv_files, 'leads': []}

            for csv_file in sorted(csv_files, reverse=True):  # Most recent first
                file_path = os.path.join(city_path, csv_file)
                try:
                    df = pd.read_csv(file_path)
                    leads = df.to_dict('records')
                    cities_data[city]['leads'].extend(leads)
                    total_leads += len(leads)

                    # Group by date
                    date = csv_file.split('/')[0]  # Extract date from directory name
                    if date not in all_leads:
                        all_leads[date] = {}
                    all_leads[date][city] = leads

                except Exception as e:
                    print(f'Error reading {file_path}: {e}')

    return render_template_string(ADMIN_DASHBOARD_TEMPLATE,
                                cities_data=cities_data,
                                all_leads=all_leads,
                                total_leads=total_leads,
                                cities=CITIES)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    secret = request.form.get('secret')
    if secret == ADMIN_SECRET:
        response = make_response(redirect('/admin'))
        response.set_cookie('admin_secret', ADMIN_SECRET, max_age=24*3600)  # 24 hours
        return response
    return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Invalid admin secret")

@app.route('/')
def index():
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8083))
    print(f'🚀 Fresh Admin Dashboard starting on port {port}...')
    print(f'📂 Reading leads from: {os.path.abspath(LEADS_PATH)}')
    print(f'🔐 Admin URL: http://localhost:{port}/admin?secret={ADMIN_SECRET}')
    app.run(host='0.0.0.0', port=port, debug=True)
