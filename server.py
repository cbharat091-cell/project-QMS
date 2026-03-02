from flask import Flask, request, jsonify, send_from_directory
from pathlib import Path
import tempfile
import os
import io
from ai_qms_reviewer import review_document, ai_review_document, gemini_review_document

# Optional PDF extraction - try both libraries for robustness
PDF_AVAILABLE = False
PDF_LIBRARY = None

try:
    import pdfplumber
    PDF_AVAILABLE = True
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_AVAILABLE = True
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        pass

# Optionally load .env for local development without committing secrets
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv not installed or .env not present — continue silently
    pass

app = Flask(__name__, static_folder='')


@app.route('/review', methods=['POST'])
def review():
    data = request.get_json() or {}
    name = data.get('name', 'uploaded_document.txt')
    content = data.get('content', '')
    provider = data.get('provider', None)

    # Write content to a temp file and call review functions which expect a Path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tf:
        tf.write(content)
        tmp_path = Path(tf.name)

    try:
        # If provider requested and server has credentials, try AI provider
        if provider == 'gemini' and os.environ.get('GEMINI_API_KEY'):
            result = gemini_review_document(tmp_path)
        elif provider == 'openai' and os.environ.get('OPENAI_API_KEY'):
            result = ai_review_document(tmp_path)
        else:
            # Default: keyword-based local review
            result = review_document(tmp_path)

        return jsonify(result)
    except Exception as e:
        return jsonify({
            'document': name,
            'status': 'Error',
            'error': str(e)
        }), 500
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


@app.route('/upload', methods=['POST'])
def upload_file():
    """Accept file uploads (multipart/form-data). Extract text from PDFs server-side."""
    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no file selected'}), 400

    filename = f.filename or 'uploaded'
    suffix = Path(filename).suffix.lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tf:
        f.save(tf.name)
        tmp_path = Path(tf.name)

    try:
        content = ''
        size = tmp_path.stat().st_size
        
        if suffix == '.pdf':
            if not PDF_AVAILABLE:
                return jsonify({
                    'error': 'PDF extraction not available on server',
                    'message': 'Install pdfplumber or PyPDF2 for PDF support'
                }), 500
            
            try:
                # Try pdfplumber first (better extraction)
                if PDF_LIBRARY == 'pdfplumber':
                    import pdfplumber
                    with pdfplumber.open(str(tmp_path)) as pdf:
                        pages = []
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                pages.append(text)
                        content = '\n'.join(pages)
                # Fall back to PyPDF2
                elif PDF_LIBRARY == 'PyPDF2':
                    import PyPDF2
                    with open(str(tmp_path), 'rb') as pdf_file:
                        reader = PyPDF2.PdfReader(pdf_file)
                        pages = []
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                pages.append(text)
                        content = '\n'.join(pages)
                
                if not content or content.strip() == '':
                    content = '[PDF uploaded but text extraction returned empty - document may be scanned/image-based]'
                    
            except Exception as e:
                return jsonify({
                    'error': f'PDF extraction failed: {str(e)}',
                    'message': 'The PDF file may be corrupted or in an unsupported format'
                }), 400
        else:
            # Read text file (TXT, MD, etc)
            try:
                content = tmp_path.read_text(encoding='utf-8', errors='replace')
            except Exception as e:
                return jsonify({
                    'error': f'Failed to read file: {str(e)}'
                }), 400

        return jsonify({
            'name': filename,
            'content': content,
            'size': size,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Upload failed: {str(e)}'
        }), 500
    finally:
        try:
            tmp_path.unlink()
        except Exception:
            pass


@app.route('/status', methods=['GET'])
def status():
    """Return which AI provider keys are available on the server."""
    providers = {
        'openai': bool(os.environ.get('OPENAI_API_KEY')),
        'gemini': bool(os.environ.get('GEMINI_API_KEY')),
    }
    return jsonify({'providers': providers})


@app.route('/', methods=['GET'])
def root_index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>', methods=['GET'])
def serve_file(filename):
    # Serve static files (CSS/JS/html) from repo root
    return send_from_directory('.', filename)


if __name__ == '__main__':
    # Bind to 0.0.0.0 so it can be reached from the forwarded Codespaces port
    app.run(host='0.0.0.0', port=8080)
