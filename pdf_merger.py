from PyPDF2 import PdfMerger
import os
from flask import Flask, request as flask_request, send_file, jsonify
from werkzeug.utils import secure_filename
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def merge_pdfs(input_files, output_file):
    # Maak een PdfMerger object
    merger = PdfMerger()
    
    try:
        # Voeg alle PDF bestanden toe
        for pdf_file in input_files:
            if pdf_file.lower().endswith('.pdf'):
                merger.append(pdf_file)
        
        # Sla het samengevoegde bestand op
        merger.write(output_file)
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
        
    finally:
        # Sluit de merger
        merger.close()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    if 'files[]' not in flask_request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = flask_request.files.getlist('files[]')
    # Remove .pdf if user added it, then add it back
    output_filename = flask_request.form.get('output_filename', 'merged').rstrip('.pdf') + '.pdf'
    output_filename = secure_filename(output_filename)
    
    temp_files = []
    try:
        # Save uploaded files temporarily
        for file in files:
            if file.filename.lower().endswith('.pdf'):
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(temp_path)
                temp_files.append(temp_path)
        
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        if merge_pdfs(temp_files, output_path):
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        else:
            return jsonify({'error': 'Merge failed'}), 500
            
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 