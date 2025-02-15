from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import configuration
from io import BytesIO

app = Flask(__name__)

# Load dataset
data_path = os.path.join(configuration.PROCESSED_DATA_DIR, "delta_results.csv")
df = pd.read_csv(data_path)

def get_unique_pcsids():
    """ Get unique PCSID values """
    return df['ID'].dropna().astype(str).unique()

@app.route('/')
def index():
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

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

