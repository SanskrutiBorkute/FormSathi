import re
from datetime import datetime
from models import validate_verhoeff

def get_validation_type(detected_type, label):
    lbl = (label or "").strip().lower()
    dt = (detected_type or "").strip().lower()
    
    # 1. Identity
    if "full name" in lbl or "name of applicant" in lbl or "applicant name" in lbl or "patient name" in lbl or "student name" in lbl or "candidate name" in lbl or lbl == "name" or "father name" in lbl or "mother name" in lbl or "guardian name" in lbl or "emergency contact name" in lbl or "emergency name" in lbl:
        return "full_name"
    if "first name" in lbl:
        return "first_name"
    if "last name" in lbl or "surname" in lbl:
        return "last_name"
    if "gender" in lbl or "sex" in lbl or dt == "gender":
        return "gender"
        
    # 2. Contact
    if "alternate" in lbl and ("phone" in lbl or "mobile" in lbl or "contact" in lbl or "no" in lbl):
        return "alternate_phone"
    if "phone" in lbl or "mobile" in lbl or "contact" in lbl or "tel" in lbl or dt == "mobile" or dt == "phone":
        return "phone"
    if "email" in lbl or dt == "email":
        return "email"
    if "pin" in lbl or "zip" in lbl or "pincode" in lbl or dt == "pincode":
        return "pincode"
    if "city" in lbl:
        return "city"
    if "state" in lbl:
        return "state"
        
    # 3. Personal
    if "birth" in lbl or "dob" in lbl or dt == "dob":
        return "dob"
    if "age" in lbl or dt == "age":
        return "age"
    if "blood" in lbl or dt == "blood_group":
        return "blood_group"
        
    # 4. Government / KYC
    if "aadhaar" in lbl or "aadhar" in lbl or dt == "aadhaar":
        return "aadhaar"
    if "pan" in lbl or "permanent account" in lbl or dt == "pan":
        return "pan"
    if "passport" in lbl:
        return "passport"
    if "driving license" in lbl or "dl no" in lbl or "license" in lbl:
        return "dl"
    if "voter" in lbl or "epic" in lbl:
        return "voter_id"
        
    # 5. Banking
    if "account number" in lbl or "acc number" in lbl or "ac no" in lbl:
        return "account_number"
    if "ifsc" in lbl or dt == "ifsc":
        return "ifsc"
        
    # 6. Healthcare
    if "mrn" in lbl or "medical record" in lbl:
        return "mrn"
    if "insurance" in lbl or "policy no" in lbl:
        return "insurance"
        
    # Fallback to detected_type
    if dt == "email": return "email"
    if dt == "mobile" or dt == "phone": return "phone"
    if dt == "aadhaar": return "aadhaar"
    if dt == "pan": return "pan"
    if dt == "ifsc": return "ifsc"
    if dt == "pincode": return "pincode"
    if dt == "dob": return "dob"
    if dt == "age": return "age"
    if dt == "blood_group": return "blood_group"
    
    return None

def validate_field_value(detected_type, label, value):
    val_str = str(value or "").strip()
    
    # Empty check
    if not val_str:
        return {
            "is_valid": False,
            "score": 0,
            "messages": ["Field is required but empty."]
        }
        
    v_type = get_validation_type(detected_type, label)
    
    if not v_type:
        # Default text validation
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid text format."]
        }
        
    if v_type == "full_name":
        # Check non-alphabets
        if not re.match(r'^[a-zA-Z\s\.]+$', val_str):
            return {
                "is_valid": False,
                "score": 40,
                "messages": ["Name contains invalid characters (numbers or symbols)."]
            }
        # Check single word
        if " " not in val_str:
            return {
                "is_valid": True,
                "score": 75,
                "messages": ["Only one name detected. Please verify if first and last name are required."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid name format."]
        }
        
    elif v_type in ["first_name", "last_name"]:
        if not re.match(r'^[a-zA-Z]+$', val_str):
            return {
                "is_valid": False,
                "score": 40,
                "messages": ["Must contain letters only."]
            }
        if len(val_str) < 2:
            return {
                "is_valid": True,
                "score": 70,
                "messages": ["Name value is unusually short."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid name format."]
        }
        
    elif v_type == "gender":
        clean_val = val_str.upper()
        if clean_val in ["MALE", "FEMALE", "OTHER", "M", "F", "O", "T", "TRANSGENDER"]:
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Valid gender value."]
            }
        return {
            "is_valid": False,
            "score": 30,
            "messages": ["Gender must be Male, Female, or Other."]
        }
        
    elif v_type in ["phone", "alternate_phone"]:
        clean_val = re.sub(r'[\s\-+()🗣]', '', val_str)
        if clean_val.startswith("91") and len(clean_val) == 12:
            clean_val = clean_val[2:]
        elif clean_val.startswith("+91"):
            clean_val = clean_val[3:]
            
        if not re.match(r'^[0-9]+$', clean_val):
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Phone number must contain digits only."]
            }
        if len(clean_val) != 10:
            return {
                "is_valid": False,
                "score": 30,
                "messages": [f"Phone number must be 10 digits. Detected {len(clean_val)} digits."]
            }
        if clean_val[0] not in ['6', '7', '8', '9']:
            return {
                "is_valid": True,
                "score": 70,
                "messages": ["Phone number does not start with standard digits 6, 7, 8, or 9."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid 10-digit phone number."]
        }
        
    elif v_type == "email":
        # Strict email matching
        if re.match(r'^[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,4}$', val_str):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Valid email format."]
            }
        return {
            "is_valid": False,
            "score": 20,
            "messages": ["Invalid email format (e.g. name@example.com)."]
        }
        
    elif v_type == "pincode":
        clean_val = re.sub(r'\s', '', val_str)
        if not re.match(r'^[0-9]{6}$', clean_val):
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["PIN code must be exactly 6 digits."]
            }
        if clean_val[0] == '0':
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["PIN code cannot start with 0."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid 6-digit PIN code."]
        }
        
    elif v_type in ["city", "state"]:
        if re.search(r'[0-9]', val_str):
            return {
                "is_valid": False,
                "score": 40,
                "messages": ["Location name must not contain numbers."]
            }
        if len(val_str) < 2:
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Location name is too short."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid location name."]
        }
        
    elif v_type == "dob":
        patterns = [
            ("%d/%m/%Y", r'^\d{2}/\d{2}/\d{4}$'),
            ("%d-%m-%Y", r'^\d{2}-\d{2}-\d{4}$'),
            ("%Y-%m-%d", r'^\d{4}-\d{2}-\d{2}$'),
        ]
        
        parsed_date = None
        for fmt, regex in patterns:
            if re.match(regex, val_str):
                try:
                    parsed_date = datetime.strptime(val_str, fmt)
                    break
                except ValueError:
                    pass
                    
        if not parsed_date:
            return {
                "is_valid": False,
                "score": 20,
                "messages": ["Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD."]
            }
            
        today = datetime.today()
        if parsed_date > today:
            return {
                "is_valid": False,
                "score": 10,
                "messages": ["Date of birth cannot be in the future."]
            }
            
        age = today.year - parsed_date.year - ((today.month, today.day) < (parsed_date.month, parsed_date.day))
        
        if age > 110:
            return {
                "is_valid": True,
                "score": 70,
                "messages": ["Valid date.", f"Calculated age is unusually high: {age} years."]
            }
            
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Valid date.", f"Age calculated: {age} years."]
        }
        
    elif v_type == "age":
        if not re.match(r'^[0-9]+$', val_str):
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Age must be a numeric integer."]
            }
        try:
            age_val = int(val_str)
            if age_val < 0 or age_val > 120:
                return {
                    "is_valid": False,
                    "score": 30,
                    "messages": ["Age must be between 0 and 120."]
                }
            if age_val < 5:
                return {
                    "is_valid": True,
                    "score": 75,
                    "messages": ["Age is very young. Verify credentials."]
                }
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Valid age value."]
            }
        except ValueError:
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Invalid integer format for age."]
            }
            
    elif v_type == "blood_group":
        clean_val = re.sub(r'\s', '', val_str).upper()
        if clean_val in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Valid blood group."]
            }
        return {
            "is_valid": False,
            "score": 30,
            "messages": ["Invalid blood group format (e.g. A+, O-, AB+)."]
        }
        
    elif v_type == "aadhaar":
        clean_val = re.sub(r'[\s\-]', '', val_str)
        if not re.match(r'^[0-9]{12}$', clean_val):
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Aadhaar number must be exactly 12 digits."]
            }
        if not validate_verhoeff(clean_val):
            return {
                "is_valid": False,
                "score": 40,
                "messages": ["Verhoeff checksum verification failed. Please check Aadhaar digits."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["12 digits detected.", "Verhoeff checksum verified."]
        }
        
    elif v_type == "pan":
        clean_val = val_str.upper()
        if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["PAN format valid."]
            }
        return {
            "is_valid": False,
            "score": 30,
            "messages": ["PAN must be in standard format: 5 letters, 4 digits, 1 letter."]
        }
        
    elif v_type == "passport":
        clean_val = val_str.upper()
        if re.match(r'^[A-Z][0-9]{7}$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Passport format valid."]
            }
        return {
            "is_valid": False,
            "score": 40,
            "messages": ["Must be 1 letter followed by 7 digits."]
        }
        
    elif v_type == "dl":
        clean_val = re.sub(r'[\s\-]', '', val_str).upper()
        if len(clean_val) >= 10 and len(clean_val) <= 16 and re.match(r'^[A-Z]{2}', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Driving License format valid."]
            }
        return {
            "is_valid": False,
            "score": 40,
            "messages": ["Must start with 2 state letters and be 10-16 characters long."]
        }
        
    elif v_type == "voter_id":
        clean_val = re.sub(r'[\s/]', '', val_str).upper()
        if re.match(r'^[A-Z]{3}[0-9]{7}$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Voter ID format valid."]
            }
        return {
            "is_valid": False,
            "score": 40,
            "messages": ["Must be 3 letters followed by 7 digits."]
        }
        
    elif v_type == "account_number":
        clean_val = re.sub(r'[\s\-]', '', val_str)
        if not re.match(r'^[0-9]{9,18}$', clean_val):
            return {
                "is_valid": False,
                "score": 30,
                "messages": ["Account number must contain 9 to 18 digits."]
            }
        return {
            "is_valid": True,
            "score": 100,
            "messages": ["Account number format valid."]
        }
        
    elif v_type == "ifsc":
        clean_val = val_str.upper()
        if re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["IFSC code valid."]
            }
        return {
            "is_valid": False,
            "score": 30,
            "messages": ["IFSC must be 11 characters: 4 letters, 0, and 6 letters/digits."]
        }
        
    elif v_type == "mrn":
        clean_val = val_str.upper()
        if re.match(r'^[A-Z0-9-]{4,12}$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["MRN format valid."]
            }
        return {
            "is_valid": False,
            "score": 40,
            "messages": ["MRN must be 4-12 alphanumeric characters."]
        }
        
    elif v_type == "insurance":
        clean_val = val_str.upper()
        if re.match(r'^[A-Z0-9-]{6,15}$', clean_val):
            return {
                "is_valid": True,
                "score": 100,
                "messages": ["Insurance policy format valid."]
            }
        return {
            "is_valid": False,
            "score": 40,
            "messages": ["Insurance must be 6-15 alphanumeric characters."]
        }
        
    return {
        "is_valid": True,
        "score": 100,
        "messages": ["Valid input."]
    }
