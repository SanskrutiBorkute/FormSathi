import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

# -------------------------------------------------------------
# 1. VERHOEFF ALGORITHM FOR REAL AADHAAR VALIDATION
# -------------------------------------------------------------
# Multiplication table d
d = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

# Permutation table p
p = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

# Inverse table
inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]

def validate_verhoeff(num_str):
    """Validate number string using Verhoeff algorithm."""
    try:
        digits = [int(x) for x in str(num_str)]
        c = 0
        for i, item in enumerate(reversed(digits)):
            c = d[c][p[i % 8][item]]
        return c == 0
    except ValueError:
        return False

# -------------------------------------------------------------
# 2. NLP FORM CLASSIFIER (TF-IDF + ML Baseline)
# -------------------------------------------------------------
CATEGORIES = [
    "Government Forms",
    "Banking Forms",
    "Education Forms",
    "Healthcare Forms",
    "Employment Forms",
    "Legal Forms",
    "Business Forms",
    "Insurance Forms",
    "Travel Forms",
    "Membership Forms",
    "Custom Form"
]

# Mini corpus of training texts representing different Universal forms
TRAINING_CORPUS = [
    # Government Forms
    ("ration card civil supplies public distribution passport voter id domicile residential certificate tehsildar office birth certificate state authority portal driving license visa permit local council death registration certificate", "Government Forms"),
    ("pan card application form aadhar linking registration national portal state government certificate municipal corporation certificate land record 7/12 extract property tax bill", "Government Forms"),
    # Banking Forms
    ("bank account opening form savings bank account term deposit kyc requirements signature card nominee sbi branch pan card identity proof address check", "Banking Forms"),
    ("fixed deposit account auto renewal recurring deposit internet banking mobile banking cheque book branch code customer identification file kyc deposit withdrawal transfer transaction card cash ledger", "Banking Forms"),
    # Education Forms
    ("post matric scholarship portal ebc merit cum means nsp caste certificate income limits marksheet college hostel fee concession scholarship renewal social justice department", "Education Forms"),
    ("school admission university enrollment course registration mark list student profile college fee payment hostel registration migration passing certificate library card issue", "Education Forms"),
    # Healthcare Forms
    ("hospital admission chart case summary patient history emergency ward details discharge summary treatment diagnostic report doctor prescription bed charge clinical trial consent", "Healthcare Forms"),
    ("medical certificate fitness sick leave application medical practitioner stamp prescription reports laboratory reports hospital bill diagnosis physical test pulse bp sugar", "Healthcare Forms"),
    # Employment Forms
    ("job application resume cv employment history pf account epf registration employee state insurance designation job code compensation details reference checks experience letter offer", "Employment Forms"),
    ("epfo login employee uan universal account number salary details qualification experience resume bio-data pf withdrawal transfer application onboarding contract non disclosure joining report", "Employment Forms"),
    # Legal Forms
    ("rent agreement lease deed tenant landlord notary stamp paper affidavit rent court witness flat agreement security deposit registration court case stamp duty power of attorney", "Legal Forms"),
    ("affidavit of declaration name correction indemnity bond advocate notary stamp register court registry stamp paper partition deed partition release memorandum of understanding", "Legal Forms"),
    # Business Forms
    ("gst registration gst number partnership deed trade license commercial establishment board resolution invoice purchase order tax invoice vendor onboarding company details cin registration certificate", "Business Forms"),
    ("corporate account application business registration msme certificate udyam startup india registration import export code tax filing balance sheet profit loss statement", "Business Forms"),
    # Insurance Forms
    ("insurance policy coverage medical claim accidental coverage term insurance premium receipt nominee death benefit hospitalization coverage policy number claim form vehicle insurance", "Insurance Forms"),
    ("third party car insurance claim form policy cover pre-existing diseases health insurance premium quotation copay sum assured details life cover claim payout agent signature", "Insurance Forms"),
    # Travel Forms
    ("visa application travel history passport details hotel booking itinerary flight ticket reservation boarding pass passenger landing card immigration custom declaration tourism stay duration", "Travel Forms"),
    ("foreign travel declaration travel insurance visa on arrival port of entry customs clearance luggage declare ticket booking travel agent boarding gate flight class details", "Travel Forms"),
    # Membership Forms
    ("club membership library subscription gym enrollment join club member registration access card renew membership terms conditions monthly fee community center application registration", "Membership Forms"),
    ("membership form association subscription plan group pass entry card annual fee details register membership agreement benefit plan discounts registration rules", "Membership Forms"),
    # Custom Form
    ("generic custom template raw fields details custom application custom information user input custom label fields checklist test values custom configuration form extra fields blank format placeholder metadata", "Custom Form")
]

# Train the classifier pipeline
texts = [x[0] for x in TRAINING_CORPUS]
labels = [x[1] for x in TRAINING_CORPUS]

classifier_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(min_df=1, stop_words='english')),
    ('nb', MultinomialNB(alpha=1.0))
])
classifier_pipeline.fit(texts, labels)

def get_classification_reason(full_text, form_type):
    """Explains why the form was classified under a specific category by matching vocabulary keywords."""
    text_lower = (full_text or "").lower()
    category_keywords = {
        "Government Forms": ["ration", "supplies", "domicile", "voter", "tehsildar", "aadhaar", "pan", "municipal", "residential"],
        "Banking Forms": ["bank", "savings", "kyc", "nominee", "cheque", "ifsc", "account", "transaction", "ledger"],
        "Education Forms": ["scholarship", "matric", "ebc", "marksheet", "college", "school", "admission", "enrollment", "cgpa", "percentage", "university", "student", "passing"],
        "Healthcare Forms": ["hospital", "patient", "discharge", "prescription", "medical", "doctor", "clinical", "consent", "treatment"],
        "Employment Forms": ["employment", "pf", "epf", "uan", "salary", "onboarding", "resume", "designation", "experience"],
        "Legal Forms": ["rent", "lease", "tenant", "landlord", "notary", "stamp", "deed", "affidavit", "agreement"],
        "Business Forms": ["gst", "invoice", "vendor", "cin", "msme", "balance", "profit", "partnership", "trade"],
        "Insurance Forms": ["insurance", "policy", "premium", "nominee", "hospitalization", "claim", "vehicle", "accidental"],
        "Travel Forms": ["visa", "passport", "flight", "itinerary", "immigration", "customs", "tourism", "boarding"],
        "Membership Forms": ["club", "subscription", "gym", "membership", "fee", "subscriber", "enrollment"],
    }
    
    matched_keywords = []
    keywords = category_keywords.get(form_type, [])
    for kw in keywords:
        if kw in text_lower:
            matched_keywords.append(kw)
            
    if matched_keywords:
        return f"Detected relevant domain keywords: {', '.join(matched_keywords)}."
    return "Classified based on general vocabulary similarity indicators."

def classify_form_text(full_text):
    """Predicts form category from text body using a hybrid Keyword + Naive Bayes ML classifier."""
    if not full_text or len(full_text.strip()) < 10:
        return "Custom Form", 0.50
        
    text_lower = full_text.lower()
    
    category_keywords = {
        "Government Forms": ["ration", "supplies", "domicile", "voter", "tehsildar", "aadhaar", "pan", "municipal", "residential", "aadhar"],
        "Banking Forms": ["bank", "savings", "kyc", "nominee", "cheque", "ifsc", "account", "transaction", "ledger"],
        "Education Forms": ["scholarship", "matric", "ebc", "marksheet", "college", "school", "admission", "enrollment", "cgpa", "percentage", "university", "student", "passing", "admissions", "academic", "undergraduate", "postgraduate"],
        "Healthcare Forms": ["hospital", "patient", "discharge", "prescription", "medical", "doctor", "clinical", "consent", "treatment"],
        "Employment Forms": ["employment", "pf", "epf", "uan", "salary", "onboarding", "resume", "designation", "experience"],
        "Legal Forms": ["rent", "lease", "tenant", "landlord", "notary", "stamp", "deed", "affidavit", "agreement"],
        "Business Forms": ["gst", "invoice", "vendor", "cin", "msme", "balance", "profit", "partnership", "trade", "gstin"],
        "Insurance Forms": ["insurance", "policy", "premium", "nominee", "hospitalization", "claim", "vehicle", "accidental"],
        "Travel Forms": ["visa", "passport", "flight", "itinerary", "immigration", "customs", "tourism", "boarding"],
        "Membership Forms": ["club", "subscription", "gym", "membership", "fee", "subscriber", "enrollment"]
    }
    
    # 1. Keyword-based matching
    keyword_counts = {}
    for cat, keywords in category_keywords.items():
        count = 0
        for kw in keywords:
            # Use word boundaries for matching keywords
            if bool(re.search(r'\b' + re.escape(kw) + r'\b', text_lower)):
                count += 1
        keyword_counts[cat] = count
        
    best_kw_cat = max(keyword_counts, key=keyword_counts.get)
    max_kw_count = keyword_counts[best_kw_cat]
    
    # 2. ML classifier pipeline prediction
    probs = classifier_pipeline.predict_proba([full_text])[0]
    best_idx = np.argmax(probs)
    predicted_ml_label = classifier_pipeline.classes_[best_idx]
    ml_confidence = float(probs[best_idx])
    
    # 3. Decision Logic: Boost or override based on keyword matches
    if max_kw_count >= 2:
        # Boost confidence score based on the number of domain keyword matches
        confidence = min(0.98, 0.70 + (max_kw_count * 0.04))
        # If the ML prediction is different but keywords are strong for the same category, use keyword category
        return best_kw_cat, confidence
        
    # If ML prediction has very low confidence, fallback to Custom Form
    if ml_confidence < 0.20:
        return "Custom Form", 0.30
        
    return predicted_ml_label, ml_confidence

# -------------------------------------------------------------
# 3. DOCUMENT CHECKLIST REQUIREMENT PREDICTOR
# -------------------------------------------------------------
def predict_documents(form_type, fields=None, full_text=""):
    """
    Predicts required documents dynamically based on detected fields
    and the actual text content of the form.
    """
    predicted_docs = []
    seen_docs = set()
    
    def add_doc(name, hint):
        if name not in seen_docs:
            predicted_docs.append({"name": name, "hint": hint})
            seen_docs.add(name)
            
    # Always include a general identity/reference proof as baseline
    add_doc("Identity Proof", "Government-issued photo ID (Passport, Voter ID, Driving License, or Aadhaar)")
    
    # Analyze fields and labels if provided
    field_types = []
    field_labels_lower = ""
    if fields:
        field_types = [f.get('detected_type') for f in fields]
        field_labels_lower = " ".join([f.get('label', '').lower() for f in fields])
        
    text_lower = (full_text or "").lower() + " " + field_labels_lower
    
    # Heuristics based on field types
    if 'aadhaar' in field_types or 'aadhar' in text_lower or 'आधार' in text_lower:
        add_doc("Aadhaar Card copy", "Copy of your 12-digit Aadhaar Card (Self-Attested)")
        
    if 'pan' in field_types or 'pan' in text_lower or 'पॅन' in text_lower:
        add_doc("PAN Card copy", "Copy of your Permanent Account Number card")
        
    if 'income' in field_types or 'income' in text_lower or 'उत्पन्न' in text_lower or 'salary' in text_lower:
        add_doc("Income Proof Document", "Recent Income Certificate or Salary Slip / Form 16")
        
    if 'ifsc' in field_types or 'account_number' in field_types or 'bank' in text_lower or 'खाते' in text_lower:
        add_doc("Bank Details copy", "First page of bank passbook or cancelled cheque displaying account details")
        
    if 'dob' in field_types or 'birth' in text_lower or 'जन्म' in text_lower:
        add_doc("Proof of Age / Birth Certificate", "School leaving certificate, birth certificate, or passport page")
        
    # Heuristics based on full text keywords
    if any(kw in text_lower for kw in ['caste', 'category', 'tribe', 'obc', 'sc', 'st', 'जातीचा', 'वर्ग']):
        add_doc("Caste / Social Category Certificate", "Required if applying under specific social categories or reservation brackets")
        
    if any(kw in text_lower for kw in ['domicile', 'residence', 'resident', 'local', 'रहवासी', 'स्थानिक']):
        add_doc("Domicile / Residency Certificate", "Proof of continuous residency in the state or region")
        
    if any(kw in text_lower for kw in ['marksheet', 'marks', 'passing', 'qualification', 'degree', 'diploma', 'educational', 'गुणपत्रिका']):
        add_doc("Academic Marksheets / Certificates", "Supporting sheets of your highest educational qualifications")
        
    if any(kw in text_lower for kw in ['rent', 'lease', 'tenant', 'landlord', 'भाडेकरार']):
        add_doc("Rent / Lease Agreement copy", "Notarized rental agreement copy between tenant and landlord")
        
    if any(kw in text_lower for kw in ['photo', 'photograph', 'passport size', 'फोटो']):
        add_doc("Passport Size Photograph", "Recent colored passport size photo (white background recommended)")
        
    if any(kw in text_lower for kw in ['signature', 'sign', 'स्वाक्षरी', 'सही']):
        add_doc("Signature Specimen", "Scan of your signature done on blank white paper")
        
    # Fallbacks based on form category if no specific fields matched
    if not predicted_docs or len(predicted_docs) <= 1:
        if "Education" in form_type:
            add_doc("Academic Marksheets / Certificates", "Supporting sheets of your highest educational qualifications")
            add_doc("Institution ID Card", "Proof of enrollment in the current course")
        elif "Banking" in form_type or "Business" in form_type:
            add_doc("Proof of Address", "Recent utility bill (electricity, water, telephone) or rent deed")
        elif "Employment" in form_type:
            add_doc("Experience Certificate", "Relieving letters or certificates from past employers")
            
    return predicted_docs

# -------------------------------------------------------------
# 4. DIFFICULTY SCORING MODEL
# -------------------------------------------------------------
def calculate_difficulty_score(fields, docs_predicted):
    """
    Computes a form complexity score between 1.0 and 10.0.
    """
    if not fields:
        return 1.0
        
    score = 1.0
    # Field count metrics
    score += min(3.0, len(fields) * 0.25)
    
    # Mandatory field count metrics
    mandatory_fields = [f for f in fields if f.get('is_required')]
    score += min(3.0, len(mandatory_fields) * 0.35)
    
    # Documents predicted count metrics
    score += min(2.0, len(docs_predicted) * 0.40)
    
    # Field type complexity penalties
    types = [f.get('detected_type') for f in fields]
    if 'signature' in types:
        score += 0.5
    if 'account_number' in types or 'ifsc' in types:
        score += 0.5
        
    final_score = min(10.0, score)
    return float(round(final_score, 1))

# -------------------------------------------------------------
# 5. REAL FORMAT VALIDATION ENGINE
# -------------------------------------------------------------
def validate_field_format(field_type, value):
    """
    Validates field formatting. Returns (is_valid, error_message)
    """
    if not value or not str(value).strip():
        return True, "" # Leave required check to main analyzer
        
    val_str = str(value).strip()
    
    if field_type == 'aadhaar':
        # Strip spaces and hyphens
        clean_val = re.sub(r'[\s\-]', '', val_str)
        if not re.match(r'^[0-9]{12}$', clean_val):
            return False, "Aadhaar must be exactly 12 digits."
        if not validate_verhoeff(clean_val):
            return False, "Invalid Aadhaar. Sum verification check failed. Please check digits."
            
    elif field_type == 'pan':
        clean_val = val_str.upper()
        # PAN format: 5 letters, 4 numbers, 1 letter
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', clean_val):
            return False, "PAN format is invalid. Must be like ABCDE1234F (5 letters, 4 digits, 1 letter)."
            
    elif field_type == 'ifsc':
        clean_val = val_str.upper()
        # IFSC format: 4 letters, 0, 6 alpha/numeric
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', clean_val):
            return False, "IFSC format is invalid. Must be 11 characters (e.g. SBIN0001234)."
            
    elif field_type == 'mobile':
        clean_val = re.sub(r'[\s\-+]', '', val_str)
        # Handle +91 prefix
        if clean_val.startswith('91') and len(clean_val) == 12:
            clean_val = clean_val[2:]
        if not re.match(r'^[6-9][0-9]{9}$', clean_val):
            return False, "Mobile number is invalid. Must be a 10-digit number starting with 6, 7, 8, or 9."
            
    elif field_type == 'email':
        if not re.match(r'^[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,4}$', val_str):
            return False, "Email address format is invalid (e.g. name@example.com)."
            
    elif field_type == 'pincode':
        clean_val = re.sub(r'\s', '', val_str)
        if not re.match(r'^[1-9][0-9]{5}$', clean_val):
            return False, "Pincode is invalid. Must be exactly 6 digits."
            
    elif field_type == 'dob':
        # Common formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        patterns = [
            r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$',
            r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$',
            r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'
        ]
        if not any(re.match(p, val_str) for p in patterns):
            return False, "Date of birth format is invalid. Use DD/MM/YYYY or YYYY-MM-DD."
            
    elif field_type == 'income':
        # Numbers only, optionally decimals
        clean_val = re.sub(r'[₹,]', '', val_str)
        if not re.match(r'^[0-9]+(\.[0-9]+)?$', clean_val):
            return False, "Annual income must contain numbers only. Remove ₹ symbols or commas."
            
    elif field_type == 'age':
        if not re.match(r'^[0-9]+$', val_str):
            return False, "Age must be a positive number of years."
        try:
            age_val = int(val_str)
            if age_val < 0 or age_val > 125:
                return False, "Age must be a realistic number between 0 and 125."
        except ValueError:
            return False, "Age must be a valid integer."
            
    elif field_type == 'blood_group':
        clean_val = re.sub(r'\s', '', val_str).upper()
        valid_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if clean_val not in valid_groups:
            return False, "Invalid blood group. Must be one of A+, A-, B+, B-, AB+, AB-, O+, O-."
            
    elif field_type == 'cgpa':
        clean_val = val_str.replace('/10', '').strip()
        try:
            val_float = float(clean_val)
            if val_float < 0.0 or val_float > 10.0:
                return False, "CGPA must be a score between 0.0 and 10.0."
        except ValueError:
            return False, "CGPA must be a valid decimal number (e.g. 8.5)."
            
    elif field_type == 'percentage':
        clean_val = val_str.replace('%', '').strip()
        try:
            val_float = float(clean_val)
            if val_float < 0.0 or val_float > 100.0:
                return False, "Percentage must be a score between 0.0 and 100.0."
        except ValueError:
            return False, "Percentage must be a valid number (e.g. 85.5)."
            
    elif field_type == 'last_school':
        if len(val_str) < 3:
            return False, "Please enter a valid institution name (at least 3 characters)."
            
    return True, ""
