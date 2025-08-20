from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    send_from_directory,
    abort,
)
import pandas as pd
import os
import sys
from io import BytesIO

# Ensure project root on path (web_app may be executed directly)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from code.config.configuration import Config  # noqa: E402

app = Flask(__name__)

# --- Existing delta_results viewer (retained) -----------------------------
_delta_results_path = os.path.join(
    Config.DataPaths.PROCESSED_DATA_DIR, "delta_results.csv"
)
try:
    df = pd.read_csv(_delta_results_path)
except FileNotFoundError:
    df = pd.DataFrame()

# --- New pcs_database viewer ---------------------------------------------
_pcs_database_path = Config.DataPaths.DATABASE_CSV_FILE
try:
    pcs_df = pd.read_csv(_pcs_database_path)
except FileNotFoundError:
    pcs_df = pd.DataFrame()

def _safe_float(v):
    try:
        return float(v)
    except Exception:
        return None

def get_unique_pcsids():
    """Get unique PCSID values (delta_results)."""
    if df.empty:
        return []
    col = 'ID' if 'ID' in df.columns else 'PCS_ID'
    return df[col].dropna().astype(str).unique()

@app.route("/")
def index():
    """Landing page – link to delta viewer & database viewer."""
    return render_template("landing.html")


@app.route('/delta')
def delta_view():
    pcsids = get_unique_pcsids()
    return render_template('index.html', pcsids=pcsids, all_data=df.to_dict(orient='records'), filtered_data=None)
@app.route('/filter', methods=['POST'])
def filter_data():
    selected_pcsid = request.form.get('pcsid', '')
    search_pcsname = request.form.get('pcsname', '')

    filtered_data = df.copy()

    # Apply filtering by ID
    if selected_pcsid:
        filtered_data = filtered_data[filtered_data['ID'].astype(str) == str(selected_pcsid)]

    # Apply filtering by PCS Name
    if search_pcsname:
        filtered_data = filtered_data[filtered_data['PCS_name'].str.contains(search_pcsname, case=False, na=False)]

    # Reset index to avoid data misalignment
    filtered_data = filtered_data.reset_index(drop=True)

    return render_template('index.html', pcsids=get_unique_pcsids(), all_data=df.to_dict(orient='records'), filtered_data=filtered_data.to_dict(orient='records'))

# API endpoint to provide data for Chart.js
@app.route("/chart_data")
def chart_data():
    """Filter the data and return Delta_P_All values as JSON."""
    pcsid = request.args.get("pcsid")
    pcsname = request.args.get("pcsname")

    # Apply filtering based on selected PCSID and PCS Name
    filtered_df = df.copy()
    if pcsid:
        filtered_df = filtered_df[filtered_df["ID"] == pcsid]
    if pcsname:
        filtered_df = filtered_df[filtered_df["PCS_name"].str.contains(pcsname, case=False, na=False)]

    # Convert the filtered data to JSON format
    chart_data = {
        "labels": filtered_df["PCS_name"].tolist(),  # X-axis: PCS_Name
        "data": filtered_df["Delta_P_All"].tolist()  # Y-axis: Delta_P_All
    }
    return jsonify(chart_data)

@app.route('/download_csv', methods=['POST'])
def download_csv():
    """ Export filtered data as CSV file """
    selected_pcsid = request.form.get('pcsid', '')
    search_pcsname = request.form.get('pcsname', '')

    filtered_data = df.copy()

    # Apply filtering
    if selected_pcsid:
        filtered_data = filtered_data[filtered_data['ID'].astype(str) == str(selected_pcsid)]
    if search_pcsname:
        filtered_data = filtered_data[filtered_data['PCS_name'].str.contains(search_pcsname, case=False, na=False)]

    # Reset index
    filtered_data = filtered_data.reset_index(drop=True)

    # Convert DataFrame to CSV in memory
    csv_buffer = BytesIO()
    filtered_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(csv_buffer, mimetype="text/csv", as_attachment=True, download_name="filtered_data.csv")

# Serve images from "image" directory
@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "image"), filename)

# -------------------------------------------------------------------------
# New: PCS Database Browser (draft)
# -------------------------------------------------------------------------

@app.route('/db')
def db_index():
    if pcs_df.empty:
        return render_template('db_index.html', columns=[], sample=[], stats={})
    # Basic summary stats
    stats = {
        'n_rows': len(pcs_df),
        'n_devices': pcs_df['PCS_ID'].nunique() if 'PCS_ID' in pcs_df.columns else None,
        'categories': sorted(pcs_df['Category'].dropna().unique().tolist()) if 'Category' in pcs_df.columns else [],
    }
    sample = pcs_df.head(50).to_dict(orient='records')  # limit initial payload
    return render_template('db_index.html', columns=pcs_df.columns, sample=sample, stats=stats)


@app.route('/api/db')
def api_db():
    if pcs_df.empty:
        return jsonify({'data': [], 'total': 0})
    q = pcs_df.copy()
    # Filters
    pcs_id = request.args.get('pcs_id')
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search')

    if pcs_id and 'PCS_ID' in q.columns:
        q = q[q['PCS_ID'].astype(str) == str(pcs_id)]
    if category and 'Category' in q.columns:
        q = q[q['Category'].str.contains(category, case=False, na=False)]
    if level and 'PCS_Level' in q.columns:
        # allow numeric or friendly words (Low/Mid/High) approximate mapping
        lmap = {
            'low': 0.0,
            'mid': 0.5,
            'high': 1.0,
        }
        target = lmap.get(level.lower(), None)
        if target is not None:
            q = q[q['PCS_Level'].round(2) == target]
        else:
            try:
                f = float(level)
                q = q[q['PCS_Level'].round(2) == round(f, 2)]
            except Exception:
                pass
    if search:
        pattern = search.lower()
        subset_cols = [c for c in ['Brand', 'Model_Name', 'Category', 'Type', 'Physical_Effect'] if c in q.columns]
        if subset_cols:
            mask = False
            for c in subset_cols:
                mask = mask | q[c].astype(str).str.lower().str.contains(pattern)
            q = q[mask]

    # Pagination (simple)
    try:
        limit = int(request.args.get('limit', 200))
    except ValueError:
        limit = 200
    q = q.head(limit)
    return jsonify({'data': q.to_dict(orient='records'), 'total': len(q)})


@app.route('/device/<int:pcs_id>')
def device_detail(pcs_id: int):
    if pcs_df.empty or 'PCS_ID' not in pcs_df.columns:
        abort(404)
    sub = pcs_df[pcs_df['PCS_ID'] == pcs_id]
    if sub.empty:
        abort(404)
    # Group by level for simple chart
    chart = []
    if 'PCS_Level' in sub.columns and 'Delta_Teq_All' in sub.columns:
        g = sub.groupby('PCS_Level', dropna=True)['Delta_Teq_All'].mean().reset_index()
        g = g.sort_values('PCS_Level')
        chart = g.to_dict(orient='records')
    meta_cols = [c for c in ['Brand', 'Model_Name', 'Category', 'Type', 'Physical_Effect'] if c in sub.columns]
    meta = {c: sub[c].iloc[0] for c in meta_cols}
    return render_template('device.html', pcs_id=pcs_id, rows=sub.to_dict(orient='records'), columns=sub.columns, chart=chart, meta=meta)

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

