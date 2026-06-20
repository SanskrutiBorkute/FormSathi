import os
import json
import re
import uuid
import base64
import sqlite3
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import db
import cv_pipeline
import ocr_engine
import models
import ai_provider

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'formsaathi_dev_secret_key_9988')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
db.init_db()

import error_handler
error_handler.register_error_handlers(app)

# AI Provider Initialization
AI_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('OPENAI_API_KEY')
provider = ai_provider.LLMAIProvider(
    provider_type='gemini' if os.environ.get('GEMINI_API_KEY') else 'local',
    api_key=AI_KEY
)

# -------------------------------------------------------------
# JWT AUTH MIDDLEWARE
# -------------------------------------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
            
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({'message': 'Token is invalid or expired!'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

def log_activity(user_id, action, details=""):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)",
        (user_id, action, details)
    )
    # Check if commit is needed (SQLite needs commit, PostgreSQL is autocommit in our db.py setup)
    if hasattr(conn, 'commit'):
        conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Invalid input data.'}), 400
        
    name = data.get('name')
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    password_hash = generate_password_hash(password)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'message': 'User with this email already exists.'}), 400
        
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        if hasattr(conn, 'commit'):
            conn.commit()
        
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = cursor.fetchone()[0]
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        log_activity(user_id, "USER_REGISTER", f"Registered account for {email}")
        
        return jsonify({
            'token': token,
            'user': {'id': user_id, 'name': name, 'email': email}
        }), 201
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password.'}), 400
        
    email = data.get('email').strip().lower()
    password = data.get('password')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    user_row = cursor.fetchone()
    conn.close()
    
    if not user_row:
        return jsonify({'message': 'Invalid email or password.'}), 401
        
    if not check_password_hash(user_row['password_hash'], password):
        return jsonify({'message': 'Invalid email or password.'}), 401
        
    # Generate token
    token = jwt.encode({
        'user_id': user_row['id'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    log_activity(user_row['id'], "USER_LOGIN", f"Logged in from account {email}")
    
    return jsonify({
        'token': token,
        'user': {'id': user_row['id'], 'name': user_row['name'], 'email': user_row['email']}
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (current_user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'message': 'User not found.'}), 404
        
    return jsonify({
        'user': {'id': row['id'], 'name': row['name'], 'email': row['email']}
    }), 200

# -------------------------------------------------------------
# FORM UPLOAD & ANALYSIS ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/forms/upload', methods=['POST'])
@token_required
def upload_form(current_user_id):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in request.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file.'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'message': 'File extension not supported.'}), 400
        
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Check image quality if it's an image
        if not file_path.lower().endswith('.pdf'):
            import cv2
            img = cv2.imread(file_path)
            if img is None or img.size == 0:
                raise error_handler.EmptyImageError("Image is empty. Please upload a valid form image.")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            if variance < 45.0:
                raise error_handler.BlurryImageError("Image quality is too low. Please upload a clearer image.")

        lang = request.args.get('lang', 'en')
        # Run OCR and structure detection pipeline
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_pdf_pages')
        fields, full_text, extra_data = ocr_engine.run_ocr_pipeline(file_path, temp_dir, lang=lang)

        # 1. OCR Failure Check
        if not fields:
            raise error_handler.OCRFailureError("No fields could be detected from this form. Please check image formatting.")
        
        # ML Form Classification
        form_type, class_conf = models.classify_form_text(full_text)
        
        # 2. Unsupported Form Check
        supported_categories = {
            "Healthcare Forms",
            "Education Forms",
            "Government Forms",
            "Banking Forms",
            "Employment Forms"
        }
        if form_type not in supported_categories:
            raise error_handler.UnsupportedFormError("This form format is currently unsupported. FormSathi supports Healthcare, Education, Government, Banking, and Employment forms.")
        
        # Document checklist requirement prediction
        docs_needed = models.predict_documents(form_type, fields, full_text)
        
        # Difficulty Scoring
        diff_score = models.calculate_difficulty_score(fields, docs_needed)
        
        # AI Form Summary
        summary = provider.summarize_form(form_type, fields, language='en')
        summary['classification_confidence'] = class_conf
        summary['classification_reason'] = models.get_classification_reason(full_text, form_type)
        summary['ocr_accuracy'] = extra_data.get('ocr_accuracy', 0.95)
        summary['field_detection_confidence'] = extra_data.get('field_detection', 0.90)
        summary['field_mapping_confidence'] = extra_data.get('field_mapping', 0.88)
        summary['sections'] = extra_data.get('sections', [])
        summary['extracted_documents'] = extra_data.get('extracted_documents', [])
        summary_json = json.dumps(summary)
        
        # Save Form to DB
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO forms (user_id, filename, file_path, form_type, difficulty_score, summary_json) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user_id, file.filename, file_path, form_type, diff_score, summary_json)
        )
        cursor.execute("SELECT last_insert_rowid() as id" if isinstance(conn, sqlite3.Connection) else "SELECT currval(pg_get_serial_sequence('forms','id')) as id")
        form_id = cursor.fetchone()[0]
        
        # Save Fields to DB
        import validation_engine
        fields_data = []
        for f in fields:
            expanded_lbl = f.get('expanded_label', f['label'])
            val_res = validation_engine.validate_field_value(f['detected_type'], expanded_lbl, f['current_value'])
            status = 'todo'
            err_msg = ""
            if f['current_value']:
                status = 'done' if val_res['is_valid'] else 'error'
                if not val_res['is_valid']:
                    err_msg = " · ".join(val_res['messages'])
            elif f['is_required']:
                status = 'error'
                err_msg = "This field is required and cannot be empty."
                
            fields_data.append((
                form_id,
                f['label'],
                expanded_lbl,
                f['detected_type'],
                f['current_value'],
                1 if f['is_required'] else 0,
                f['confidence_score'],
                status,
                err_msg if err_msg else None,
                f.get('ocr_confidence', f['confidence_score']),
                f.get('field_detection_confidence', 0.90),
                f.get('section_title', 'General'),
                f.get('nearby_ocr_text', ''),
                f['current_value'],
                val_res['score'],
                json.dumps(val_res)
            ))
            
        cursor.executemany("""
            INSERT INTO fields (form_id, label, expanded_label, detected_type, current_value, is_required, confidence_score, status, error_message, ocr_confidence, field_detection_confidence, section_title, nearby_ocr_text, original_ocr_value, validation_score, validation_json) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fields_data)
        
        if hasattr(conn, 'commit'):
            conn.commit()
            
        log_activity(current_user_id, "FORM_UPLOADED", f"Uploaded form {file.filename} (ID: {form_id}, Type: {form_type})")
        
        return jsonify({
            'form_id': form_id,
            'form_type': form_type,
            'difficulty_score': diff_score
        }), 201
        
    except error_handler.FormSathiError as e:
        raise e
    except Exception as e:
        import logging
        logging.exception(f"Analysis failed: {str(e)}")
        return jsonify({'message': 'An unexpected error occurred during form processing. Please try again.'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/api/forms/camera-capture', methods=['POST'])
@token_required
def camera_capture(current_user_id):
    data = request.get_json()
    if not data or not data.get('image_data'):
        return jsonify({'message': 'Missing image data.'}), 400
        
    image_data_b64 = data.get('image_data')
    if "," in image_data_b64:
        image_data_b64 = image_data_b64.split(",")[1]
        
    raw_filename = f"capture_{uuid.uuid4()}.png"
    raw_path = os.path.join(app.config['UPLOAD_FOLDER'], raw_filename)
    
    # Save base64 to image file
    with open(raw_path, "wb") as fh:
        fh.write(base64.b64decode(image_data_b64))
        
    try:
        import cv2
        img = cv2.imread(raw_path)
        if img is None or img.size == 0:
            raise error_handler.EmptyImageError("Image is empty. Please upload a valid form image.")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 45.0:
            raise error_handler.BlurryImageError("Image quality is too low. Please upload a clearer image.")

        processed_filename = f"processed_{uuid.uuid4()}.png"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        
        lang = request.args.get('lang', 'en')
        # Run CV Preprocessing (Crop, Perspective warp, Threshold)
        cv_pipeline.preprocess_document(raw_path, processed_path)
        
        # Run OCR on processed document
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_pdf_pages')
        fields, full_text, extra_data = ocr_engine.run_ocr_pipeline(processed_path, temp_dir, lang=lang)

        # 1. OCR Failure Check
        if not fields:
            raise error_handler.OCRFailureError("No fields could be detected from this form. Please check image formatting.")
            
        # Form Classification
        form_type, class_conf = models.classify_form_text(full_text)
        
        # 2. Unsupported Form Check
        supported_categories = {
            "Healthcare Forms",
            "Education Forms",
            "Government Forms",
            "Banking Forms",
            "Employment Forms"
        }
        if form_type not in supported_categories:
            raise error_handler.UnsupportedFormError("This form format is currently unsupported. FormSathi supports Healthcare, Education, Government, Banking, and Employment forms.")
        
        # Documents checklist
        docs_needed = models.predict_documents(form_type, fields, full_text)
        
        # Difficulty rating
        diff_score = models.calculate_difficulty_score(fields, docs_needed)
        
        # Summary
        summary = provider.summarize_form(form_type, fields, language='en')
        summary['classification_confidence'] = class_conf
        summary['classification_reason'] = models.get_classification_reason(full_text, form_type)
        summary['ocr_accuracy'] = extra_data.get('ocr_accuracy', 0.95)
        summary['field_detection_confidence'] = extra_data.get('field_detection', 0.90)
        summary['field_mapping_confidence'] = extra_data.get('field_mapping', 0.88)
        summary['sections'] = extra_data.get('sections', [])
        summary['extracted_documents'] = extra_data.get('extracted_documents', [])
        summary_json = json.dumps(summary)
        
        # Save Form
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO forms (user_id, filename, file_path, form_type, difficulty_score, summary_json) VALUES (?, ?, ?, ?, ?, ?)",
            (current_user_id, "Camera Capture.png", processed_path, form_type, diff_score, summary_json)
        )
        cursor.execute("SELECT last_insert_rowid() as id" if isinstance(conn, sqlite3.Connection) else "SELECT currval(pg_get_serial_sequence('forms','id')) as id")
        form_id = cursor.fetchone()[0]
        
        # Save Fields
        import validation_engine
        fields_data = []
        for f in fields:
            expanded_lbl = f.get('expanded_label', f['label'])
            val_res = validation_engine.validate_field_value(f['detected_type'], expanded_lbl, f['current_value'])
            status = 'todo'
            err_msg = ""
            if f['current_value']:
                status = 'done' if val_res['is_valid'] else 'error'
                if not val_res['is_valid']:
                    err_msg = " · ".join(val_res['messages'])
            elif f['is_required']:
                status = 'error'
                err_msg = "This field is required and cannot be empty."
                
            fields_data.append((
                form_id,
                f['label'],
                expanded_lbl,
                f['detected_type'],
                f['current_value'],
                1 if f['is_required'] else 0,
                f['confidence_score'],
                status,
                err_msg if err_msg else None,
                f.get('ocr_confidence', f['confidence_score']),
                f.get('field_detection_confidence', 0.90),
                f.get('section_title', 'General'),
                f.get('nearby_ocr_text', ''),
                f['current_value'],
                val_res['score'],
                json.dumps(val_res)
            ))
            
        cursor.executemany("""
            INSERT INTO fields (form_id, label, expanded_label, detected_type, current_value, is_required, confidence_score, status, error_message, ocr_confidence, field_detection_confidence, section_title, nearby_ocr_text, original_ocr_value, validation_score, validation_json) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fields_data)
        
        if hasattr(conn, 'commit'):
            conn.commit()
            
        log_activity(current_user_id, "CAMERA_CAPTURE", f"Captured form via camera (ID: {form_id}, Type: {form_type})")
        
        return jsonify({
            'form_id': form_id,
            'form_type': form_type,
            'difficulty_score': diff_score
        }), 201
        
    except error_handler.FormSathiError as e:
        raise e
    except Exception as e:
        import logging
        logging.exception(f"Camera capture analysis failed: {str(e)}")
        return jsonify({'message': 'An unexpected error occurred during camera form processing. Please try again.'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# -------------------------------------------------------------
# DETAILS & UPDATING ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/forms/<int:form_id>', methods=['GET'])
@token_required
def get_form_details(current_user_id, form_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Verify owner
    cursor.execute("SELECT id, filename, form_type, difficulty_score, summary_json, created_at FROM forms WHERE id = ? AND user_id = ?", (form_id, current_user_id))
    form_row = cursor.fetchone()
    if not form_row:
        conn.close()
        return jsonify({'message': 'Form not found or access denied.'}), 404
        
    # Get fields
    cursor.execute("SELECT id, label, expanded_label, detected_type, current_value, is_required, confidence_score, status, error_message, ocr_confidence, field_detection_confidence, original_ocr_value, validation_score, validation_json, section_title FROM fields WHERE form_id = ?", (form_id,))
    fields_rows = cursor.fetchall()
    conn.close()
    
    fields_list = []
    for fr in fields_rows:
        fields_list.append({
            'id': fr['id'],
            'label': fr['expanded_label'] if fr['expanded_label'] else fr['label'],
            'original_label': fr['label'],
            'expanded_label': fr['expanded_label'] if fr['expanded_label'] else fr['label'],
            'detected_type': fr['detected_type'],
            'current_value': fr['current_value'],
            'is_required': bool(fr['is_required']),
            'confidence_score': fr['confidence_score'],
            'ocr_confidence': fr['ocr_confidence'] if fr['ocr_confidence'] is not None else fr['confidence_score'],
            'field_detection_confidence': fr['field_detection_confidence'] if fr['field_detection_confidence'] is not None else 0.90,
            'status': fr['status'],
            'error_message': fr['error_message'],
            'original_ocr_value': fr['original_ocr_value'],
            'validation_score': fr['validation_score'],
            'validation_json': fr['validation_json'],
            'section_title': fr['section_title'] or 'General'
        })
        
    form_type = form_row['form_type']
    summary = json.loads(form_row['summary_json']) if form_row['summary_json'] else {}
    docs_needed = models.predict_documents(form_type, fields_list, form_row['summary_json'])
    
    # Combine predicted and extracted documents
    extracted_docs = summary.get('extracted_documents', [])
    combined_docs = list(docs_needed)
    seen_doc_names = {d['name'].lower() for d in combined_docs}
    for doc in extracted_docs:
        doc_name = doc.get('name')
        if doc_name and doc_name.lower() not in seen_doc_names:
            combined_docs.append(doc)
            seen_doc_names.add(doc_name.lower())
    
    return jsonify({
        'id': form_row['id'],
        'filename': form_row['filename'],
        'form_type': form_type,
        'difficulty_score': form_row['difficulty_score'],
        'summary': summary,
        'created_at': form_row['created_at'],
        'fields': fields_list,
        'predicted_documents': combined_docs
    }), 200

@app.route('/api/forms/field/<int:field_id>', methods=['PUT'])
@token_required
def update_field_value(current_user_id, field_id):
    data = request.get_json()
    value = data.get('value', '').strip()
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get field properties and verify ownership of form
    cursor.execute("""
        SELECT f.id, f.detected_type, f.label, f.expanded_label, f.form_id, f.is_required, fo.user_id 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE f.id = ?
    """, (field_id,))
    field_row = cursor.fetchone()
    
    if not field_row or field_row['user_id'] != current_user_id:
        conn.close()
        return jsonify({'message': 'Field not found or access denied.'}), 404
        
    detected_type = field_row['detected_type']
    is_required = bool(field_row['is_required'])
    label = field_row['expanded_label'] if field_row['expanded_label'] else field_row['label']
    
    # Run format validation using validation_engine
    import validation_engine
    val_res = validation_engine.validate_field_value(detected_type, label, value)
    
    status = 'done'
    err_msg = ""
    if not value:
        if is_required:
            status = 'error'
            err_msg = "This field is required and cannot be empty."
        else:
            status = 'todo'
    elif not val_res['is_valid']:
        status = 'error'
        err_msg = " · ".join(val_res['messages'])
        
    # Update field record
    cursor.execute("""
        UPDATE fields 
        SET current_value = ?, status = ?, error_message = ?, validation_score = ?, validation_json = ? 
        WHERE id = ?
    """, (value if value else None, status, err_msg if err_msg else None, val_res['score'], json.dumps(val_res), field_id))
    
    if hasattr(conn, 'commit'):
        conn.commit()
        
    log_activity(current_user_id, "FIELD_UPDATED", f"Updated field {field_id} (value: {value}, status: {status})")
    conn.close()
    
    return jsonify({
        'field_id': field_id,
        'current_value': value,
        'status': status,
        'error_message': err_msg,
        'validation_score': val_res['score'],
        'validation': val_res
    }), 200

@app.route('/api/forms/field/<int:field_id>/explain', methods=['GET'])
@token_required
def get_field_explanation(current_user_id, field_id):
    lang = request.args.get('lang', 'en')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.detected_type, f.label, f.expanded_label, f.section_title, f.nearby_ocr_text, f.explanation_json, fo.form_type, fo.user_id 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE f.id = ?
    """, (field_id,))
    field_row = cursor.fetchone()
    conn.close()
    
    if not field_row or field_row['user_id'] != current_user_id:
        return jsonify({'message': 'Field not found or access denied.'}), 404
        
    label_to_use = field_row['expanded_label'] if field_row['expanded_label'] else field_row['label']
        
    # Log Guidance Request
    log_activity(current_user_id, "GUIDANCE_REQUESTED", f"Requested explanation for field {field_id} ({label_to_use}) in language {lang}")
        
    explanation = None
    cached_explanations = {}
    if field_row['explanation_json']:
        try:
            cached_explanations = json.loads(field_row['explanation_json'])
            if lang in cached_explanations:
                explanation = cached_explanations[lang]
        except Exception as cache_err:
            print(f"Warning: Failed to parse cached explanation JSON: {cache_err}")
            
    if not explanation:
        explanation = provider.explain_field(
            field_row['detected_type'],
            label_to_use,
            language=lang,
            nearby_text=field_row['nearby_ocr_text'] or '',
            form_category=field_row['form_type'] or '',
            section_title=field_row['section_title'] or 'General'
        )
        
        # Save to DB cache
        cached_explanations[lang] = explanation
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE fields SET explanation_json = ? WHERE id = ?", (json.dumps(cached_explanations), field_id))
            if hasattr(conn, 'commit'):
                conn.commit()
            conn.close()
        except Exception as save_cache_err:
            print(f"Warning: Failed to save explanation to cache: {save_cache_err}")
            
        # Future-Proof: Log unknown fields (where confidence score is < 70%)
        conf_str = explanation.get('confidence_score', '0%').replace('%', '')
        try:
            conf_val = float(conf_str)
        except ValueError:
            conf_val = 0.0
            
        if conf_val < 70.0:
            try:
                log_path = os.path.join(os.path.dirname(__file__), 'unknown_fields.log')
                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"{datetime.utcnow().isoformat()} - Label: '{field_row['label']}' | Category: '{field_row['form_type']}' | Section: '{field_row['section_title']}'\n")
            except Exception as log_err:
                print(f"Warning: Failed to log unknown field: {log_err}")
                
    return jsonify({
        'field_id': field_id,
        'language': lang,
        'explanation': explanation
    }), 200

# -------------------------------------------------------------
# CHAT ASSISTANT & LANGUAGE SWITCH API
# -------------------------------------------------------------
@app.route('/api/forms/<int:form_id>/chat', methods=['POST'])
@token_required
def chat_with_form(current_user_id, form_id):
    data = request.get_json()
    query = data.get('query', '').strip()
    lang = data.get('lang', 'en')
    
    if not query:
        return jsonify({'message': 'Query cannot be empty.'}), 400
        
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, form_type, summary_json FROM forms WHERE id = ? AND user_id = ?", (form_id, current_user_id))
    form_row = cursor.fetchone()
    
    if not form_row:
        conn.close()
        return jsonify({'message': 'Form not found or access denied.'}), 404
        
    cursor.execute("SELECT label, detected_type, current_value, is_required FROM fields WHERE form_id = ?", (form_id,))
    fields_rows = cursor.fetchall()
    conn.close()
    
    fields_list = []
    for fr in fields_rows:
        fields_list.append({
            'label': fr['label'],
            'detected_type': fr['detected_type'],
            'current_value': fr['current_value'],
            'is_required': bool(fr['is_required'])
        })
        
    # Build complete form context for the AI
    form_type = form_row['form_type']
    summary = json.loads(form_row['summary_json']) if form_row['summary_json'] else {}
    predicted_docs = models.predict_documents(form_type, fields_list, form_row['summary_json'])
    
    form_context = {
        'form_type': form_type,
        'summary': summary,
        'fields': fields_list,
        'predicted_documents': predicted_docs
    }
    
    # Fetch answer from AI
    answer = provider.answer_assistant_query(query, form_context, language=lang)
    
    return jsonify({
        'query': query,
        'language': lang,
        'response': answer
    }), 200

# -------------------------------------------------------------
# ANALYTICS DASHBOARD API
# -------------------------------------------------------------
@app.route('/api/analytics', methods=['GET'])
@token_required
def get_analytics(current_user_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Total forms analyzed
    cursor.execute("SELECT COUNT(id) FROM forms WHERE user_id = ?", (current_user_id,))
    total_forms = cursor.fetchone()[0]
    
    # 2. Total fields extracted
    cursor.execute("""
        SELECT COUNT(f.id) 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ?
    """, (current_user_id,))
    total_fields = cursor.fetchone()[0]
    
    # 3. Average OCR Accuracy
    cursor.execute("""
        SELECT AVG(COALESCE(f.ocr_confidence, f.confidence_score)) 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ?
    """, (current_user_id,))
    avg_ocr_raw = cursor.fetchone()[0]
    avg_ocr_accuracy = round(avg_ocr_raw * 100, 1) if avg_ocr_raw is not None else 85.0
    
    # 4. AI Guidance Requests
    cursor.execute("""
        SELECT COUNT(id) 
        FROM activity_logs 
        WHERE user_id = ? AND (action = 'GUIDANCE_REQUESTED' OR action = 'FIELD_EXPLAINED')
    """, (current_user_id,))
    guidance_requests = cursor.fetchone()[0]
    
    # 5. Languages Used
    cursor.execute("""
        SELECT explanation_json 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ? AND f.explanation_json IS NOT NULL
    """, (current_user_id,))
    lang_rows = cursor.fetchall()
    langs_set = set()
    for row in lang_rows:
        try:
            cached_data = json.loads(row['explanation_json'])
            for l in cached_data.keys():
                langs_set.add(l)
        except Exception:
            pass
    languages_used = len(langs_set) if langs_set else 1
    
    # 6. Overall Field Complete vs Error Rates
    cursor.execute("""
        SELECT f.status, COUNT(f.id) as cnt 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ? 
        GROUP BY f.status
    """, (current_user_id,))
    status_counts = {r['status']: r['cnt'] for r in cursor.fetchall()}
    done_cnt = status_counts.get('done', 0)
    err_cnt = status_counts.get('error', 0)
    todo_cnt = status_counts.get('todo', 0)
    
    filled_cnt = done_cnt + err_cnt
    validation_success_rate = round((done_cnt / filled_cnt) * 100, 1) if filled_cnt > 0 else 100.0
    
    # Completion Rate (Filled Fields / Total Fields)
    completion_rate = round((done_cnt / total_fields) * 100, 1) if total_fields > 0 else 100.0
    
    # 7. Category Distribution counts (including defaults)
    cursor.execute("SELECT form_type, COUNT(id) as cnt FROM forms WHERE user_id = ? GROUP BY form_type", (current_user_id,))
    cat_counts = {r['form_type']: r['cnt'] for r in cursor.fetchall()}
    
    supported_cats = ["Healthcare Forms", "Education Forms", "Government Forms", "Banking Forms", "Employment Forms"]
    categories_distribution = []
    for cat in supported_cats:
        categories_distribution.append({
            "category": cat.replace(" Forms", ""),
            "count": cat_counts.get(cat, 0)
        })
    other_count = sum(cnt for cat, cnt in cat_counts.items() if cat not in supported_cats)
    categories_distribution.append({
        "category": "Other",
        "count": other_count
    })
    
    # 8. Recent analyzed forms list
    cursor.execute("SELECT id, filename, form_type, difficulty_score, created_at FROM forms WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (current_user_id,))
    recent_forms = []
    for r in cursor.fetchall():
        recent_forms.append({
            'id': r['id'],
            'filename': r['filename'],
            'form_type': r['form_type'],
            'difficulty_score': r['difficulty_score'],
            'created_at': r['created_at']
        })
        
    # 9. Get recent activity logs
    cursor.execute("SELECT action, details, created_at FROM activity_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 8", (current_user_id,))
    logs = []
    for r in cursor.fetchall():
        logs.append({
            'action': r['action'],
            'details': r['details'],
            'created_at': r['created_at']
        })
        
    # 10. OCR Confidence and Validation Trends (chronological per form)
    cursor.execute("SELECT id, filename, created_at FROM forms WHERE user_id = ? ORDER BY created_at ASC", (current_user_id,))
    forms_rows = cursor.fetchall()
    
    ocr_trend = []
    val_trend = []
    
    for r in forms_rows:
        form_id = r['id']
        cursor.execute("SELECT ocr_confidence, status FROM fields WHERE form_id = ?", (form_id,))
        fields_data = cursor.fetchall()
        
        if fields_data:
            avg_conf = sum(x['ocr_confidence'] if x['ocr_confidence'] is not None else 0.85 for x in fields_data) / len(fields_data)
            done_f = sum(1 for x in fields_data if x['status'] == 'done')
            err_f = sum(1 for x in fields_data if x['status'] == 'error')
            
            total_filled = done_f + err_f
            val_success = (done_f / total_filled) * 100 if total_filled > 0 else 100.0
            
            name_short = r['filename'].split('_')[-1][:12]
            
            ocr_trend.append({
                "name": name_short,
                "confidence": round(avg_conf * 100, 1),
                "date": r['created_at'][:10]
            })
            val_trend.append({
                "name": name_short,
                "success_rate": round(val_success, 1),
                "date": r['created_at'][:10]
            })
            
    # 11. OCR vs User Correction Analytics
    cursor.execute("""
        SELECT COUNT(f.id) 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ? AND f.original_ocr_value IS NOT NULL AND f.current_value != f.original_ocr_value
    """, (current_user_id,))
    fields_corrected = cursor.fetchone()[0]
    
    correction_percentage = round((fields_corrected / total_fields) * 100, 1) if total_fields > 0 else 0.0
    
    cursor.execute("""
        SELECT f.detected_type, COUNT(f.id) as cnt 
        FROM fields f 
        JOIN forms fo ON f.form_id = fo.id 
        WHERE fo.user_id = ? AND f.original_ocr_value IS NOT NULL AND f.current_value != f.original_ocr_value
        GROUP BY f.detected_type
        ORDER BY cnt DESC
        LIMIT 5
    """, (current_user_id,))
    most_corrected = [{"type": row['detected_type'], "count": row['cnt']} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_forms': total_forms,
        'fields_extracted': total_fields,
        'avg_ocr_accuracy': avg_ocr_accuracy,
        'ai_guidance_requests': guidance_requests,
        'languages_used': languages_used,
        'validation_success_rate': validation_success_rate,
        'completion_rate': completion_rate,
        'field_status': {
            'done': done_cnt,
            'errors': err_cnt,
            'todo': todo_cnt
        },
        'categories': cat_counts,
        'categories_distribution': categories_distribution,
        'ocr_trend': ocr_trend,
        'val_trend': val_trend,
        'fields_corrected': fields_corrected,
        'correction_percentage': correction_percentage,
        'most_corrected': most_corrected,
        'recent_forms': recent_forms,
        'activity_logs': logs
    }), 200

# -------------------------------------------------------------
# DEMO MODE ROUTE
# -------------------------------------------------------------
@app.route('/api/forms/demo', methods=['POST'])
@token_required
def create_demo_form(current_user_id):
    data = request.get_json()
    form_key = data.get('form_key', 'healthcare').strip().lower()
    
    # Preloaded sample schemas
    demo_schemas = {
        "healthcare": {
            "name": "Sample_Patient_Registration.png",
            "type": "Healthcare Forms",
            "diff": 3.5,
            "fields": [
                {"label": "Full Name", "type": "full_name", "val": "John Doe", "req": True, "ocr_conf": 0.96},
                {"label": "Date of Birth", "type": "dob", "val": "12/08/1988", "req": True, "ocr_conf": 0.94},
                {"label": "Gender", "type": "gender", "val": "Male", "req": True, "ocr_conf": 0.98},
                {"label": "Phone Number", "type": "phone", "val": "98765432", "req": True, "ocr_conf": 0.65},
                {"label": "Email Address", "type": "email", "val": "john.doe@example", "req": True, "ocr_conf": 0.88},
                {"label": "Insurance Number", "type": "insurance", "val": "INS12345678", "req": False, "ocr_conf": 0.92},
                {"label": "MRN Number", "type": "mrn", "val": "MRN87654", "req": True, "ocr_conf": 0.91},
                {"label": "Blood Group", "type": "blood_group", "val": "O+", "req": False, "ocr_conf": 0.95},
                {"label": "Allergies", "type": "text", "val": "None", "req": False, "ocr_conf": 0.93}
            ]
        },
        "education": {
            "name": "Sample_Student_Admission.png",
            "type": "Education Forms",
            "diff": 4.0,
            "fields": [
                {"label": "Full Name", "type": "full_name", "val": "Alice Smith", "req": True, "ocr_conf": 0.97},
                {"label": "First Name", "type": "first_name", "val": "Alice", "req": True, "ocr_conf": 0.95},
                {"label": "Last Name", "type": "last_name", "val": "Smith", "req": True, "ocr_conf": 0.96},
                {"label": "Gender", "type": "gender", "val": "Female", "req": True, "ocr_conf": 0.94},
                {"label": "Date of Birth", "type": "dob", "val": "05-05-2005", "req": True, "ocr_conf": 0.93},
                {"label": "Email Address", "type": "email", "val": "alice@university", "req": True, "ocr_conf": 0.62},
                {"label": "Phone Number", "type": "phone", "val": "8765432109", "req": True, "ocr_conf": 0.95},
                {"label": "PIN Code", "type": "pincode", "val": "400001", "req": True, "ocr_conf": 0.92},
                {"label": "City", "type": "city", "val": "Mumbai", "req": True, "ocr_conf": 0.94},
                {"label": "State", "type": "state", "val": "Maharashtra", "req": True, "ocr_conf": 0.96}
            ]
        },
        "government": {
            "name": "Sample_Government_Application.png",
            "type": "Government Forms",
            "diff": 5.0,
            "fields": [
                {"label": "Full Name", "type": "full_name", "val": "Rajesh Kumar", "req": True, "ocr_conf": 0.95},
                {"label": "Gender", "type": "gender", "val": "Male", "req": True, "ocr_conf": 0.96},
                {"label": "Date of Birth", "type": "dob", "val": "15/06/1980", "req": True, "ocr_conf": 0.94},
                {"label": "Aadhaar Number", "type": "aadhaar", "val": "123456789012", "req": True, "ocr_conf": 0.92},
                {"label": "PAN Number", "type": "pan", "val": "ABCDE1234F", "req": True, "ocr_conf": 0.95},
                {"label": "Voter ID", "type": "voter_id", "val": "XYZ1234567", "req": True, "ocr_conf": 0.93},
                {"label": "PIN Code", "type": "pincode", "val": "110001", "req": True, "ocr_conf": 0.91}
            ]
        },
        "banking": {
            "name": "Sample_Banking_KYC.png",
            "type": "Banking Forms",
            "diff": 4.5,
            "fields": [
                {"label": "Full Name", "type": "full_name", "val": "Sanjay Mehta", "req": True, "ocr_conf": 0.96},
                {"label": "Account Number", "type": "account_number", "val": "123456789012", "req": True, "ocr_conf": 0.93},
                {"label": "IFSC Code", "type": "ifsc", "val": "SBIN0001234", "req": True, "ocr_conf": 0.94},
                {"label": "Email Address", "type": "email", "val": "sanjay.mehta@bank.com", "req": True, "ocr_conf": 0.95},
                {"label": "Phone Number", "type": "phone", "val": "7654321098", "req": True, "ocr_conf": 0.92}
            ]
        }
    }
    
    schema = demo_schemas.get(form_key, demo_schemas["healthcare"])
    
    # Save dummy form
    conn = db.get_connection()
    cursor = conn.cursor()
    
    import validation_engine
    
    # Build summary dict
    summary = {
        "purpose": f"Sample form configuration representing {schema['type']}.",
        "who": "FormSathi demo user testing validation alerts and guidance systems.",
        "est_time": "3-5 minutes",
        "warnings": "This is a demo mode configuration with preloaded field parameters.",
        "classification_confidence": 0.99,
        "classification_reason": "Preloaded sample metadata form.",
        "ocr_accuracy": sum(f['ocr_conf'] for f in schema['fields']) / len(schema['fields']),
        "field_detection_confidence": 0.98,
        "field_mapping_confidence": 0.97,
        "sections": ["Personal Details", "Verification ID", "Signature Block"],
        "extracted_documents": [{"name": "Aadhaar Card", "hint": "For KYC identity mapping"}, {"name": "PAN Card", "hint": "For income verification"}]
    }
    
    cursor.execute("""
        INSERT INTO forms (user_id, filename, file_path, form_type, difficulty_score, summary_json)
        VALUES (?, ?, 'demo_mode_path.png', ?, ?, ?)
    """, (current_user_id, schema['name'], schema['type'], schema['diff'], json.dumps(summary)))
    
    cursor.execute("SELECT last_insert_rowid() as id" if isinstance(conn, sqlite3.Connection) else "SELECT currval(pg_get_serial_sequence('forms','id')) as id")
    form_id = cursor.fetchone()[0]
    
    fields_data = []
    for f in schema['fields']:
        val_res = validation_engine.validate_field_value(f['type'], f['label'], f['val'])
        status = 'done' if val_res['is_valid'] else 'error'
        err_msg = ""
        if not val_res['is_valid']:
            err_msg = " · ".join(val_res['messages'])
            
        fields_data.append((
            form_id,
            f['label'],
            f['label'], # expanded_label is same as label for demo
            f['type'],
            f['val'],
            1 if f['req'] else 0,
            f['ocr_conf'],
            status,
            err_msg if err_msg else None,
            f['ocr_conf'],
            0.98,
            'General',
            'Sample OCR background context text',
            f['val'],
            val_res['score'],
            json.dumps(val_res)
        ))
        
    cursor.executemany("""
        INSERT INTO fields (form_id, label, expanded_label, detected_type, current_value, is_required, confidence_score, status, error_message, ocr_confidence, field_detection_confidence, section_title, nearby_ocr_text, original_ocr_value, validation_score, validation_json) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fields_data)
    
    if hasattr(conn, 'commit'):
        conn.commit()
    conn.close()
    
    log_activity(current_user_id, "DEMO_FORM_CREATED", f"Created demo form '{schema['name']}' (ID: {form_id})")
    
    return jsonify({
        'form_id': form_id,
        'form_type': schema['type'],
        'difficulty_score': schema['diff']
    }), 201

# -------------------------------------------------------------
# EXPORT API ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/forms/<int:form_id>/export/json', methods=['GET'])
@token_required
def export_form_json(current_user_id, form_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check ownership
    cursor.execute("SELECT id, filename, form_type, created_at, user_id FROM forms WHERE id = ?", (form_id,))
    form_row = cursor.fetchone()
    if not form_row or form_row['user_id'] != current_user_id:
        conn.close()
        return jsonify({'message': 'Form not found or access denied.'}), 404
        
    cursor.execute("""
        SELECT id, label, expanded_label, detected_type, current_value, is_required, ocr_confidence, status, error_message, validation_score, validation_json 
        FROM fields 
        WHERE form_id = ?
    """, (form_id,))
    fields_rows = cursor.fetchall()
    conn.close()
    
    import export_service
    json_data = export_service.generate_json_report(
        form_row['filename'],
        form_row['form_type'],
        form_row['created_at'],
        [dict(r) for r in fields_rows]
    )
    
    return jsonify(json_data), 200

@app.route('/api/forms/<int:form_id>/export/pdf', methods=['GET'])
@token_required
def export_form_pdf(current_user_id, form_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check ownership
    cursor.execute("SELECT id, filename, form_type, created_at, user_id FROM forms WHERE id = ?", (form_id,))
    form_row = cursor.fetchone()
    if not form_row or form_row['user_id'] != current_user_id:
        conn.close()
        return jsonify({'message': 'Form not found or access denied.'}), 404
        
    cursor.execute("""
        SELECT id, label, expanded_label, detected_type, current_value, is_required, ocr_confidence, status, error_message, validation_score, validation_json 
        FROM fields 
        WHERE form_id = ?
    """, (form_id,))
    fields_rows = cursor.fetchall()
    conn.close()
    
    import export_service
    pdf_bytes = export_service.generate_pdf_report(
        form_row['filename'],
        form_row['form_type'],
        form_row['created_at'],
        [dict(r) for r in fields_rows]
    )
    
    from flask import send_file
    import io
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"{form_row['filename']}_report.pdf"
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )
