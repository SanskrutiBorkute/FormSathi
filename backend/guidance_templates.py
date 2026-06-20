import re
from difflib import SequenceMatcher

TEMPLATES = {
    # IDENTITY
    "full_name": {
        "name": "Full Name",
        "aliases": ["full name", "applicant name", "student name", "candidate name", "patient name", "name of candidate", "candidate's name", "name of applicant", "applicant's name", "patient's name", "name", "name of patient", "first name last name", "full name of applicant", "candidate full name", "applicant full name", "patient full name"],
        "en": {
            "what": "Your complete legal name or the registered name of the applicant.",
            "input_guidance": "Enter your official name exactly as printed on your government photo ID card (like Aadhaar, PAN, or Passport).",
            "why": "Required to establish official identity, record ownership, and create database references.",
            "formats": "Alphabets and spaces only.",
            "example": "RAHUL SHARMA",
            "mistakes": "Using unofficial initials, nicknames, or abbreviations.",
            "validation": "Must not contain numbers or special characters."
        },
        "hi": {
            "what": "आपका पूरा कानूनी नाम या आवेदक का पंजीकृत नाम।",
            "input_guidance": "अपना आधिकारिक नाम बिल्कुल वैसे ही दर्ज करें जैसे आपके सरकारी फोटो पहचान पत्र पर मुद्रित है।",
            "why": "आधिकारिक पहचान स्थापित करने, स्वामित्व दर्ज करने और संदर्भ बनाने के लिए आवश्यक।",
            "formats": "केवल अक्षर और रिक्त स्थान।",
            "example": "राहुल शर्मा",
            "mistakes": "अनौपचारिक आद्याक्षर, उपनाम या संक्षिप्ताक्षरों का उपयोग करना।",
            "validation": "इसमें अंक या विशेष वर्ण नहीं होने चाहिए।"
        },
        "mr": {
            "what": "तुमचे संपूर्ण कायदेशीर नाव किंवा अर्जदाराचे नोंदणीकृत नाव.",
            "input_guidance": "तुमचे अधिकृत नाव तुमच्या सरकारी फोटो ओळखपत्रावर असल्याप्रमाणे अचूक लिहा.",
            "why": "अधिकृत ओळख स्थापित करण्यासाठी, मालकीची नोंद करण्यासाठी आणि संदर्भ तयार करण्यासाठी आवश्यक.",
            "formats": "फक्त अक्षरे आणि मोकळी जागा.",
            "example": "राहुल शर्मा",
            "mistakes": "अनधिकृत आद्याक्षरे, टोपणनावे किंवा संक्षेप वापरणे.",
            "validation": "यामध्ये अंक किंवा विशेष चिन्हे नसावीत."
        }
    },
    "first_name": {
        "name": "First Name",
        "aliases": ["first name", "given name", "fname"],
        "en": {
            "what": "Your individual/personal name that distinguishes you within a family.",
            "input_guidance": "Enter your first name as shown on your legal identity documents. Exclude middle or last names.",
            "why": "Used for personal identification, addressing communications, and verifying identity documents.",
            "formats": "Alphabets only.",
            "example": "RAHUL",
            "mistakes": "Including your surname or middle name in this field.",
            "validation": "Must not contain digits, spaces, or special characters."
        },
        "hi": {
            "what": "आपका व्यक्तिगत नाम जो आपको परिवार के भीतर विशिष्ट बनाता है।",
            "input_guidance": "अपने कानूनी पहचान दस्तावेजों के अनुसार अपना पहला नाम दर्ज करें। मध्य या उपनाम शामिल न करें।",
            "why": "व्यक्तिगत पहचान, संचार को संबोधित करने और पहचान दस्तावेजों को सत्यापित करने के लिए उपयोग किया जाता है।",
            "formats": "केवल अक्षर।",
            "example": "राहुल",
            "mistakes": "इस क्षेत्र में अपना उपनाम या मध्य नाम शामिल करना।",
            "validation": "इसमें अंक, रिक्त स्थान या विशेष वर्ण नहीं होने चाहिए।"
        },
        "mr": {
            "what": "तुमचे वैयक्तिक नाव जे तुम्हाला कुटुंबात ओळख देते.",
            "input_guidance": "तुमच्या कायदेशीर दस्तऐवजांनुसार registre तुमचे पहिले नाव लिहा. मधले किंवा आडनाव समाविष्ट करू नका.",
            "why": "वैयक्तिक ओळख, संवादासाठी आणि ओळखपत्र पडताळणीसाठी वापरले जाते.",
            "formats": "फक्त अक्षरे.",
            "example": "राहुल",
            "mistakes": "या रकान्यात आडनाव किंवा मधले नाव लिहिणे.",
            "validation": "यामध्ये अंक, मोकळी जागा (spaces) किंवा विशेष चिन्हे नसावीत."
        }
    },
    "last_name": {
        "name": "Last Name",
        "aliases": ["last name", "surname", "family name", "lname"],
        "en": {
            "what": "Your family name, surname, or inherited name.",
            "input_guidance": "Enter your family surname exactly as printed on your official ID proofs.",
            "why": "Required for familial lineage matching, legal profiling, and official database queries.",
            "formats": "Alphabets only.",
            "example": "SHARMA",
            "mistakes": "Entering middle names, titles (like Shri or Dr), or leaving blank if you have a single name.",
            "validation": "Must not contain digits, spaces, or special characters."
        },
        "hi": {
            "what": "आपका पारिवारिक नाम, उपनाम या विरासत में मिला नाम।",
            "input_guidance": "अपने आधिकारिक आईडी प्रमाणों पर मुद्रित अपना पारिवारिक उपनाम दर्ज करें।",
            "why": "पारिवारिक वंशावली मिलान, कानूनी प्रोफाइलिंग और आधिकारिक डेटाबेस प्रश्नों के लिए आवश्यक।",
            "formats": "केवल अक्षर।",
            "example": "शर्मा",
            "mistakes": "मध्य नाम, शीर्षक (जैसे श्री या डॉ) दर्ज करना, या एकल नाम होने पर इसे खाली छोड़ना।",
            "validation": "इसमें अंक, रिक्त स्थान या विशेष वर्ण नहीं होने चाहिए।"
        },
        "mr": {
            "what": "तुमचे कौटुंबिक नाव, आडनाव किंवा वारसाहक्काने मिळालेले नाव.",
            "input_guidance": "तुमच्या अधिकृत ओळखपत्रावर असल्याप्रमाणे registre तुमचे आडनाव अचूक लिहा.",
            "why": "कौटुंबिक नातेसंबंध पडताळण्यासाठी आणि ओळख स्थापित करण्यासाठी आवश्यक.",
            "formats": "फक्त अक्षरे.",
            "example": "शर्मा",
            "mistakes": "मधले नाव, पदव्या (उदा. श्री किंवा डॉ) लिहिणे, किंवा एकच नाव असल्यास रकाना मोकळा ठेवणे.",
            "validation": "यामध्ये अंक, मोकळी जागा किंवा विशेष चिन्हे नसावीत."
        }
    },
    "fathers_name": {
        "name": "Father's Name",
        "aliases": ["father's name", "father name", "fathers name", "father/husband name"],
        "en": {
            "what": "The legal name of the applicant's father.",
            "input_guidance": "Write your father's full name exactly as shown on his government identity proof.",
            "why": "Used to establish family relationship, verify legal background, and complete guardianship records.",
            "formats": "Alphabets and spaces only.",
            "example": "RAMESH SHARMA",
            "mistakes": "Adding prefixes like 'Mr.', 'Shri', or 'Late' before the name.",
            "validation": "Must not contain numbers or special symbols."
        },
        "hi": {
            "what": "आवेदक के पिता का कानूनी नाम।",
            "input_guidance": "अपने पिता का पूरा नाम बिल्कुल वैसे ही लिखें जैसे उनके सरकारी पहचान पत्र पर दिखाया गया है।",
            "why": "पारिवारिक संबंध स्थापित करने, कानूनी पृष्ठभूमि को सत्यापित करने और अभिभावक रिकॉर्ड पूरा करने के लिए उपयोग किया जाता है।",
            "formats": "केवल अक्षर और रिक्त स्थान।",
            "example": "रमेश शर्मा",
            "mistakes": "नाम से पहले 'श्री', 'मिस्टर' या 'स्वर्गीय' जैसे उपसर्ग जोड़ना।",
            "validation": "इसमें अंक या विशेष प्रतीक नहीं होने चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या वडिलांचे कायदेशीर नाव.",
            "input_guidance": "तुमच्या वडिलांचे पूर्ण नाव त्यांच्या सरकारी ओळखपत्रावर असल्याप्रमाणे अचूक लिहा.",
            "why": "कौटुंबिक नातेसंबंध प्रस्थापित करण्यासाठी, कायदेशीर पडताळणीसाठी आवश्यक.",
            "formats": "फक्त अक्षरे आणि मोकळी जागा.",
            "example": "रमेश शर्मा",
            "mistakes": "नावाच्या आधी 'श्री.', 'मिस्टर' किंवा 'कै.' सारखे उपसर्ग लावणे.",
            "validation": "यामध्ये अंक किंवा विशेष चिन्हे नसावीत."
        }
    },
    "mothers_name": {
        "name": "Mother's Name",
        "aliases": ["mother's name", "mother name", "mothers name"],
        "en": {
            "what": "The legal name of the applicant's mother.",
            "input_guidance": "Write your mother's full name exactly as shown on her official identity cards.",
            "why": "Required for relationship mapping, secondary parental verification, and minor applications.",
            "formats": "Alphabets and spaces.",
            "example": "SUNITA SHARMA",
            "mistakes": "Adding prefixes like 'Mrs.' or 'Smt.' or typing nicknames.",
            "validation": "Must not contain numbers or punctuation."
        },
        "hi": {
            "what": "आवेदक की माता का कानूनी नाम।",
            "input_guidance": "अपनी माता का पूरा नाम बिल्कुल वैसे ही लिखें जैसे उनके आधिकारिक पहचान पत्रों पर दिखाया गया है।",
            "why": "संबंध मिलान, माध्यमिक माता-पिता सत्यापन और नाबालिग आवेदनों के लिए आवश्यक।",
            "formats": "केवल अक्षर और रिक्त स्थान।",
            "example": "सुनीता शर्मा",
            "mistakes": "नाम से पहले 'श्रीमती', 'मिसेज' या उपनाम जोड़ना।",
            "validation": "इसमें अंक या विराम चिह्न नहीं होने चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या आईचे कायदेशीर नाव.",
            "input_guidance": "तुमच्या आईचे पूर्ण नाव तिच्या अधिकृत ओळखपत्रावर असल्याप्रमाणे अचूक लिहा.",
            "why": "नातेसंबंध पडताळणी आणि इतर कौटुंबिक नोंदींसाठी आवश्यक.",
            "formats": "फक्त अक्षरे आणि मोकळी जागा.",
            "example": "सुनीता शर्मा",
            "mistakes": "नावाच्या आधी 'श्रीमती', 'मिसेज' लावणे किंवा टोपणनावे लिहिणे.",
            "validation": "यामध्ये अंक किंवा विरामचिन्हे नसावीत."
        }
    },
    "guardian_name": {
        "name": "Guardian Name",
        "aliases": ["guardian name", "guardian's name", "parent/guardian name", "name of guardian"],
        "en": {
            "what": "The name of your legal guardian or authorized representative.",
            "input_guidance": "Enter the full name of your legal guardian if applicant is a minor or under care.",
            "why": "Acts as legal custodian contact for minor declarations or emergency approvals.",
            "formats": "Alphabets and spaces.",
            "example": "ANIL SHARMA",
            "mistakes": "Entering father's name here if father is not the official guardian.",
            "validation": "Must not contain numbers or special characters."
        },
        "hi": {
            "what": "आपके कानूनी अभिभावक या अधिकृत प्रतिनिधि का नाम।",
            "input_guidance": "यदि आवेदक नाबालिग है या देखरेख में है, तो अपने कानूनी अभिभावक का पूरा नाम दर्ज करें।",
            "why": "आपातकालीन या कानूनी मामलों में नाबालिग घोषणाओं के लिए संपर्क के रूप में कार्य करता है।",
            "formats": "केवल अक्षर और रिक्त स्थान।",
            "example": "अनिल शर्मा",
            "mistakes": "अभिभावक के रूप में पिता न होने पर भी पिता का नाम दर्ज करना।",
            "why": "अल्पवयीन अर्जदारांच्या बाबतीत कायदेशीर संमती आणि आपत्कालीन संपर्कासाठी आवश्यक.",
            "formats": "फक्त अक्षरे आणि मोकळी जागा.",
            "example": "अनिल शर्मा",
            "mistakes": "वडील अधिकृत पालक नसतानाही वडिलांचे नाव पालक म्हणून लिहिणे.",
            "validation": "यामध्ये अंक किंवा विशेष चिन्हे नसावीत."
        }
    },
    "father_occupation": {
        "name": "Father Occupation",
        "aliases": ["father occupation", "father's occupation", "occupation of father"],
        "en": {
            "what": "The current job, profession, or employment status of the applicant's father.",
            "input_guidance": "Enter your father's active profession (e.g. Farmer, Teacher, Business Owner, Software Engineer, Retired).",
            "why": "Used to assess eligibility, family background, or financial concessions for scholarships.",
            "formats": "Text details.",
            "example": "TEACHER",
            "mistakes": "Providing past occupation or details of other family members.",
            "validation": "Should match your father's current employment profile."
        },
        "hi": {
            "what": "आवेदक के पिता की वर्तमान नौकरी, पेशा या रोजगार की स्थिति।",
            "input_guidance": "अपने पिता का सक्रिय पेशा दर्ज करें (जैसे किसान, शिक्षक, व्यवसायी, सेवानिवृत्त)।",
            "why": "छात्रवृत्ति के लिए पात्रता, पारिवारिक पृष्ठभूमि या वित्तीय रियायतों का आकलन करने के लिए उपयोग किया जाता है।",
            "formats": "पाठ विवरण।",
            "example": "शिक्षक (TEACHER)",
            "mistakes": "पिछला व्यवसाय या परिवार के अन्य सदस्यों का विवरण देना।",
            "validation": "आपके पिता की वर्तमान रोजगार प्रोफ़ाइल से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या वडिलांचे सध्याचे काम, नोकरी किंवा व्यवसाय.",
            "input_guidance": "तुमच्या वडिलांचा सध्याचा व्यवसाय लिहा (उदा. शेतकरी, शिक्षक, व्यावसायिक, निवृत्त).",
            "why": "विविध शासकीय सवलती किंवा शिष्यवृत्तीच्या पात्रतेसाठी आवश्यक.",
            "formats": "अक्षरे.",
            "example": "शिक्षक (TEACHER)",
            "mistakes": "वडिलांचे जुने काम किंवा इतर कुटुंबातील व्यक्तींची माहिती देणे.",
            "validation": "चालू रोजगाराची माहिती दर्शवणारे असावे."
        }
    },
    "mother_occupation": {
        "name": "Mother Occupation",
        "aliases": ["mother occupation", "mother's occupation", "occupation of mother"],
        "en": {
            "what": "The current job, profession, or employment status of the applicant's mother.",
            "input_guidance": "Enter your mother's active profession (e.g. Homemaker, Teacher, Doctor, Business, Retired).",
            "why": "Used to assess eligibility, family background, or financial concessions for scholarships.",
            "formats": "Text details.",
            "example": "HOMEMAKER",
            "mistakes": "Providing past occupation or leaving blank.",
            "validation": "Should match your mother's current employment profile."
        },
        "hi": {
            "what": "आवेदक की माता की वर्तमान नौकरी, पेशा या रोजगार की स्थिति।",
            "input_guidance": "अपनी माता का सक्रिय पेशा दर्ज करें (जैसे गृहणी, शिक्षिका, डॉक्टर, व्यवसायी, सेवानिवृत्त)।",
            "why": "छात्रवृत्ति के लिए पात्रता, पारिवारिक पृष्ठभूमि या वित्तीय रियायतों का आकलन करने के लिए उपयोग किया जाता है।",
            "formats": "पाठ विवरण।",
            "example": "गृहणी (HOMEMAKER)",
            "mistakes": "पिछला व्यवसाय दर्ज करना या खाली छोड़ना।",
            "validation": "आपकी माता की वर्तमान रोजगार प्रोफ़ाइल से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या आईचे सध्याचे काम, नोकरी किंवा व्यवसाय.",
            "input_guidance": "तुमच्या आईचा सध्याचा व्यवसाय लिहा (उदा. गृहिणी, शिक्षिका, डॉक्टर, व्यावसायिक, निवृत्त).",
            "why": "विविध शासकीय सवलती किंवा शिष्यवृत्तीच्या पात्रतेसाठी आवश्यक.",
            "formats": "अक्षरे.",
            "example": "गृहिणी (HOMEMAKER)",
            "mistakes": "आईचे जुने काम किंवा रकाना कोरा ठेवणे.",
            "validation": "आईच्या चालू रोजगाराची अचूक माहिती लिहावी."
        }
    },
    "guardian_occupation": {
        "name": "Guardian Occupation",
        "aliases": ["guardian occupation", "guardian's occupation", "occupation of guardian"],
        "en": {
            "what": "The current job, profession, or employment status of the applicant's legal guardian.",
            "input_guidance": "Enter your legal guardian's active profession (e.g. Advocate, Shopkeeper, Farmer, Service, Retired).",
            "why": "Required to check the financial status and guardianship responsibilities.",
            "formats": "Text details.",
            "example": "ADVOCATE",
            "mistakes": "Entering parents' occupation here if they are not the official guardian.",
            "validation": "Should match your guardian's current employment profile."
        },
        "hi": {
            "what": "आवेदक के कानूनी अभिभावक की वर्तमान नौकरी, पेशा या रोजगार की स्थिति।",
            "input_guidance": "अपने कानूनी अभिभावक का सक्रिय पेशा दर्ज करें (जैसे अधिवक्ता, दुकानदार, किसान, नौकरी, सेवानिवृत्त)।",
            "why": "वित्तीय स्थिति और अभिभावक की जिम्मेदारियों की जांच करने के लिए आवश्यक।",
            "formats": "पाठ विवरण।",
            "example": "अधिवक्ता (ADVOCATE)",
            "mistakes": "अभिभावक न होने पर भी माता-पिता का व्यवसाय दर्ज करना।",
            "validation": "आपके अभिभावक की वर्तमान रोजगार प्रोफ़ाइल से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या कायदेशीर पालकांचे सध्याचे काम, नोकरी किंवा व्यवसाय.",
            "input_guidance": "तुमच्या कायदेशीर पालकांचा सध्याचा व्यवसाय लिहा (उदा. वकील, दुकानदार, शेतकरी, नोकरी, निवृत्त).",
            "why": "पालकांची आर्थिक पत आणि जबाबदारी पडताळण्यासाठी आवश्यक.",
            "formats": "अक्षरे.",
            "example": "वकील (ADVOCATE)",
            "mistakes": "अधिकृत पालक नसतानाही आई-वडिलांचे काम लिहिणे.",
            "validation": "पालकांच्या चालू रोजगाराची अचूक माहिती लिहावी."
        }
    },
    "father_phone": {
        "name": "Father Mobile Number",
        "aliases": ["father mobile number", "father mobile", "father contact number", "father phone number", "father's phone number", "father's mobile number", "father's contact number", "father phone", "father contact"],
        "en": {
            "what": "The official 10-digit mobile number of the applicant's father.",
            "input_guidance": "Enter your father's active 10-digit mobile number. Do not prefix +91 or 0 unless requested.",
            "why": "Used for sending updates, verification OTPs, and communicating in case of emergency.",
            "formats": "10-digit numeric value starting with 6-9.",
            "example": "9876543210",
            "mistakes": "Entering a phone number that is out of service, or adding country code prefixes.",
            "validation": "Must be exactly 10 digits."
        },
        "hi": {
            "what": "आवेदक के पिता का आधिकारिक 10-अंकीय मोबाइल नंबर।",
            "input_guidance": "अपने पिता का सक्रिय 10-अंकीय मोबाइल नंबर दर्ज करें। अनुरोध के बिना +91 या 0 उपसर्ग न जोड़ें।",
            "why": "अपडेट भेजने, सत्यापन ओटीपी, और आपातकालीन स्थिति में संपर्क करने के लिए उपयोग किया जाता है।",
            "formats": "6-9 से शुरू होने वाला 10-अंकीय संख्यात्मक मान।",
            "example": "9876543210",
            "mistakes": "ऐसा फोन नंबर दर्ज करना जो सेवा से बाहर हो, या देश कोड उपसर्ग जोड़ना।",
            "validation": "ठीक 10 अंक होने चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या वडिलांचा अधिकृत १०-अंकी मोबाईल क्रमांक.",
            "input_guidance": "तुमच्या वडिलांचा चालू १०-अंकी मोबाईल नंबर लिहा. आधी +91 किंवा 0 लावू नका.",
            "why": "ओळख पडताळणी, महत्त्वाचे मेसेज पाठवण्यासाठी किंवा आपत्कालीन संपर्कासाठी आवश्यक.",
            "formats": "६-९ ने सुरू होणारा १०-अंकी क्रमांक.",
            "example": "9876543210",
            "mistakes": "बंद असलेला नंबर देणे, किंवा देश कोड लावणे.",
            "validation": "अचूक १०-अंकी क्रमांक असावा."
        }
    },
    "mother_phone": {
        "name": "Mother Mobile Number",
        "aliases": ["mother mobile number", "mother mobile", "mother contact number", "mother phone number", "mother's phone number", "mother's mobile number", "mother's contact number", "mother phone", "mother contact"],
        "en": {
            "what": "The official 10-digit mobile number of the applicant's mother.",
            "input_guidance": "Enter your mother's active 10-digit mobile number. Do not prefix +91 or 0 unless requested.",
            "why": "Used for secondary communication, verification updates, and parent coordination.",
            "formats": "10-digit numeric value starting with 6-9.",
            "example": "9876543211",
            "mistakes": "Entering landline numbers without area codes or entering incorrect digits.",
            "validation": "Must be exactly 10 digits."
        },
        "hi": {
            "what": "आवेदक की माता का आधिकारिक 10-अंकीय मोबाइल नंबर।",
            "input_guidance": "अपनी माता का सक्रिय 10-अंकीय मोबाइल नंबर दर्ज करें। अनुरोध के बिना +91 या 0 उपसर्ग न जोड़ें।",
            "why": "माध्यमिक संचार, सत्यापन अपडेट, and माता-पिता के समन्वय के लिए उपयोग किया जाता है।",
            "formats": "6-9 से शुरू होने वाला 10-अंकीय संख्यात्मक मान।",
            "example": "9876543211",
            "mistakes": "एरिया कोड के बिना लैंडलाइन नंबर दर्ज करना या गलत अंक दर्ज करना।",
            "validation": "ठीक 10 अंक होने चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराच्या आईचा अधिकृत १०-अंकी मोबाईल क्रमांक.",
            "input_guidance": "तुमच्या आईचा चालू १०-अंकी मोबाईल नंबर लिहा. आधी +91 किंवा 0 लावू नका.",
            "why": "माध्यमिक संपर्क, अर्जाचे अपडेट्स आणि पालकांशी समन्वयासाठी आवश्यक.",
            "formats": "६-९ ने सुरू होणारा १०-अंकी क्रमांक.",
            "example": "9876543211",
            "mistakes": "अयोग्य किंवा बंद असलेला मोबाईल क्रमांक लिहिणे.",
            "validation": "अचूक १०-अंकी क्रमांक असावा."
        }
    },
    "guardian_phone": {
        "name": "Guardian Mobile Number",
        "aliases": ["guardian mobile number", "guardian mobile", "guardian contact number", "guardian phone number", "guardian's phone number", "guardian's mobile number", "guardian's contact number", "guardian phone", "guardian contact", "guardian contact number"],
        "en": {
            "what": "The official 10-digit mobile number of the applicant's legal guardian.",
            "input_guidance": "Enter your legal guardian's active 10-digit mobile number. Do not prefix +91 or 0 unless requested.",
            "why": "Acts as the primary legal representative contact for minor updates or emergency approvals.",
            "formats": "10-digit numeric value starting with 6-9.",
            "example": "9876543212",
            "mistakes": "Entering parent's contact number here if they are not the official legal guardian.",
            "validation": "Must be exactly 10 digits."
        },
        "hi": {
            "what": "आवेदक के कानूनी अभिभावक का आधिकारिक 10-अंकीय मोबाइल नंबर।",
            "input_guidance": "अपने कानूनी अभिभावक का सक्रिय 10-अंकीय मोबाइल नंबर दर्ज करें। अनुरोध के बिना +91 या 0 उपसर्ग न जोड़ें।",
            "why": "नाबालिग के लिए मुख्य कानूनी प्रतिनिधि संपर्क के रूप में कार्य करता है।",
            "formats": "6-9 से शुरू होने वाला 10-अंकीय संख्यात्मक मान।",
            "example": "9876543212",
            "mistakes": "अभिभावक न होने पर भी माता-पिता का संपर्क नंबर दर्ज करना।",
            "validation": "ठीक 10 अंक होने चाहिए।"
        },
        "mr": {
            "what": "तुमच्या कायदेशीर पालकांचा अधिकृत १०-अंकी मोबाईल क्रमांक.",
            "input_guidance": "तुमच्या पालकांचा चालू १०-अंकी मोबाईल नंबर लिहा. आधी +91 किंवा 0 लावू नका.",
            "why": "अल्पवयीन अर्जदारांच्या बाबतीत मुख्य कायदेशीर प्रतिनिधीच्या संपर्कासाठी आवश्यक.",
            "formats": "६-९ ने सुरू होणारा १०-अंकी क्रमांक.",
            "example": "9876543212",
            "mistakes": "अधिकृत पालक नसतानाही आई-वडिलांचा नंबर पालक संपर्क म्हणून लिहिणे.",
            "validation": "अचूक १०-अंकी क्रमांक असावा."
        }
    },
    "emergency_contact_phone": {
        "name": "Emergency Contact Mobile Number",
        "aliases": ["emergency contact number", "emergency contact phone", "emergency contact mobile number", "emergency contact mobile", "emergency phone number", "emergency mobile number"],
        "en": {
            "what": "The mobile number of the designated contact person to call in case of emergency.",
            "input_guidance": "Enter a reliable 10-digit mobile number of a relative or friend who can be reached immediately.",
            "why": "Required for urgent medical, academic, or legal updates if the applicant is unreachable.",
            "formats": "10-digit mobile number starting with 6-9.",
            "example": "9876543213",
            "mistakes": "Entering applicant's own mobile number or a number that is rarely active.",
            "validation": "Must be exactly 10 digits."
        },
        "hi": {
            "what": "आपातकालीन स्थिति में कॉल करने के लिए निर्दिष्ट संपर्क व्यक्ति का मोबाइल नंबर।",
            "input_guidance": "किसी ऐसे रिश्तेदार या मित्र का विश्वसनीय 10-अंकीय मोबाइल नंबर दर्ज करें जिससे तुरंत संपर्क किया जा सके।",
            "why": "आवेदक से संपर्क न होने पर तत्काल चिकित्सा, शैक्षणिक या कानूनी अपडेट के लिए आवश्यक।",
            "formats": "6-9 से शुरू होने वाला 10-अंकीय मोबाइल नंबर।",
            "example": "9876543213",
            "mistakes": "आवेदक का अपना मोबाइल नंबर दर्ज करना या ऐसा नंबर जो शायद ही कभी सक्रिय रहता हो।",
            "validation": "ठीक 10 अंक होने चाहिए।"
        },
        "mr": {
            "what": "आपत्कालीन परिस्थितीत संपर्क साधण्यासाठी नियुक्त व्यक्तीचा मोबाईल क्रमांक.",
            "input_guidance": "तातडीने संपर्क साधता येईल अशा जवळच्या नातेवाईक किंवा मित्राचा चालू १०-अंकी मोबाईल नंबर लिहा.",
            "why": "अर्जदाराशी संपर्क न झाल्यास वैद्यकीय किंवा कायदेशीर तातडीच्या प्रसंगी संपर्क साधण्यासाठी आवश्यक.",
            "formats": "१०-अंकी मोबाईल क्रमांक.",
            "example": "9876543213",
            "mistakes": "स्वतःचाच मोबाईल क्रमांक लिहिणे किंवा बंद असलेला नंबर देणे.",
            "validation": "अचूक १०-अंकी क्रमांक असावा."
        }
    },
    "gender": {
        "name": "Gender",
        "aliases": ["gender", "sex", "male/female", "biological sex"],
        "en": {
            "what": "Your biological sex or gender identity.",
            "input_guidance": "Select or write Male, Female, or Transgender/Other as applicable.",
            "why": "Used for demographic profiling, checking gender-specific eligibility, or reservation seats.",
            "formats": "Standard values: MALE, FEMALE, TRANSGENDER, or OTHER.",
            "example": "FEMALE",
            "mistakes": "Confusing it with marital status or filling arbitrary text.",
            "validation": "Must match one of the standard gender categories."
        },
        "hi": {
            "what": "आपका जैविक लिंग या लिंग पहचान।",
            "input_guidance": "लागू होने के अनुसार पुरुष, महिला, या अन्य चुनें या लिखें।",
            "why": "जनसांख्यिकीय रूपरेखा, लिंग-विशिष्ट पात्रता की जांच करने या आरक्षित सीटों के लिए उपयोग किया जाता है।",
            "formats": "मानक मान: MALE, FEMALE, TRANSGENDER, या OTHER।",
            "example": "FEMALE",
            "mistakes": "इसे वैवाहिक स्थिति के साथ भ्रमित करना या मनमाना पाठ भरना।",
            "validation": "मानक लिंग श्रेणियों में से एक से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "तुमचे जैविक लिंग किंवा लैंगिक ओळख.",
            "input_guidance": "लागू पडल्यास पुरुष (Male), स्त्री (Female), किंवा तृतीयपंथी/इतर (Other) निवडा.",
            "why": "लोकसंख्याशास्त्रीय नोंदी, लिंग-आधारित पात्रता किंवा आरक्षित जागा तपासण्यासाठी आवश्यक.",
            "formats": "मानक पर्याय: MALE, FEMALE, TRANSGENDER किंवा OTHER.",
            "example": "FEMALE",
            "mistakes": "वैवाहिक स्थितीशी संभ्रम करणे किंवा चुकीचा मजकूर लिहिणे.",
            "validation": "मानक लिंग पर्यायांपैकी एकाशी जुळले पाहिजे."
        }
    },
    "marital_status": {
        "name": "Marital Status",
        "aliases": ["marital status", "marriage status", "married/single", "marital"],
        "en": {
            "what": "Your current legal union or relationship status.",
            "input_guidance": "Write whether you are Single, Married, Divorced, Widowed, or Separated.",
            "why": "Required for tax category calculations, insurance policy coverage, or visa parameters.",
            "formats": "Single, Married, Divorced, Widowed.",
            "example": "SINGLE",
            "mistakes": "Leaving it unselected or selecting wrong relationship status.",
            "validation": "Must contain a valid option choice."
        },
        "hi": {
            "what": "आपका वर्तमान कानूनी संघ या संबंध स्थिति।",
            "input_guidance": "लिखें कि आप अविवाहित, विवाहित, तलाकशुदा, विधवा या अलग हैं।",
            "why": "कर श्रेणी गणना, बीमा पॉलिसी कवरेज, या वीज़ा मापदंडों के लिए आवश्यक।",
            "formats": "Single, Married, Divorced, Widowed।",
            "example": "SINGLE",
            "mistakes": "इसे अचयनित छोड़ना या गलत संबंध स्थिति चुनना।",
            "validation": "एक वैध विकल्प चयन होना चाहिए।"
        },
        "mr": {
            "what": "तुमची सध्याची कायदेशीर वैवाहिक स्थिती.",
            "input_guidance": "तुम्ही अविवाहित, विवाहित, घटस्फोटित, किंवा विधवा आहात का ते लिहा.",
            "why": "कर आकारणी, विमा पॉलिसीचे संरक्षण किंवा व्हिसा निकषांसाठी आवश्यक.",
            "formats": "Single, Married, Divorced, Widowed.",
            "example": "SINGLE",
            "mistakes": "पर्याय निवडायला विसरणे किंवा चुकीची स्थिती निवडणे.",
            "validation": "दिलेल्या पर्यायांपैकी एक वैध पर्याय असणे आवश्यक."
        }
    },
    "nationality": {
        "name": "Nationality",
        "aliases": ["nationality", "citizenship", "citizen of"],
        "en": {
            "what": "The nation of which you hold legal citizenship.",
            "input_guidance": "Enter the name of the country where you have official citizenship.",
            "why": "Required to check visa guidelines, travel rules, and eligibility under state welfare.",
            "formats": "Country name in text.",
            "example": "INDIAN",
            "mistakes": "Writing city or state name instead of country name.",
            "validation": "Must represent a valid sovereign country."
        },
        "hi": {
            "what": "वह देश जिसकी आपके पास कानूनी नागरिकता है।",
            "input_guidance": "उस देश का नाम दर्ज करें जहाँ आपकी आधिकारिक नागरिकता है।",
            "why": "वीज़ा दिशानिर्देशों, यात्रा नियमों और स्थानीय राज्य कल्याण पात्रता जांच के लिए आवश्यक।",
            "formats": "पाठ में देश का नाम।",
            "example": "INDIAN",
            "mistakes": "देश के नाम के बजाय शहर या राज्य का नाम लिखना।",
            "validation": "एक वैध संप्रभु देश का प्रतिनिधित्व होना चाहिए।"
        },
        "mr": {
            "what": "ज्या देशाचे तुमच्याकडे कायदेशीर नागरिकत्व आहे तो देश.",
            "input_guidance": "तुमच्याकडे ज्या देशाचे अधिकृत नागरिकत्व आहे त्या देशाचे नाव लिहा.",
            "why": "व्हिसा नियम, प्रवास निकष आणि शासकीय योजनांच्या पात्रतेसाठी आवश्यक.",
            "formats": "देशाचे नाव.",
            "example": "INDIAN",
            "mistakes": "देशाच्या नावाऐवजी शहर किंवा राज्याचे नाव लिहिणे.",
            "validation": "मान्यताप्राप्त सार्वभौम देश असणे आवश्यक."
        }
    },

    # CONTACT
    "phone_number": {
        "name": "Phone Number",
        "aliases": ["phone number", "phone no", "mobile number", "mobile no", "contact number", "contact no", "telephone no", "telephone number", "cell number", "mobile"],
        "en": {
            "what": "Your primary cellular or telephone contact number.",
            "input_guidance": "Enter your active 10-digit mobile number without any country code or leading zero.",
            "why": "Used for transaction alerts, sending OTP codes, and emergency calls.",
            "formats": "10-digit numeric sequence.",
            "example": "9876543210",
            "mistakes": "Entering country codes (+91) or trailing/leading blank spaces.",
            "validation": "Must be exactly 10 digits and start with 6, 7, 8, or 9."
        },
        "hi": {
            "what": "आपका प्राथमिक सेलुलर या टेलीफोन संपर्क नंबर।",
            "input_guidance": "बिना किसी कंट्री कोड या शुरुआती शून्य के अपना सक्रिय 10-अंकीय मोबाइल नंबर दर्ज करें।",
            "why": "लेनदेन अलर्ट, ओटीपी कोड भेजने और आपातकालीन कॉल के लिए उपयोग किया जाता है।",
            "formats": "10-अंकीय संख्यात्मक अनुक्रम।",
            "example": "9876543210",
            "mistakes": "कंट्री कोड (+91) या आगे/पीछे खाली स्थान दर्ज करना।",
            "validation": "ठीक 10 अंक होने चाहिए और 6, 7, 8 या 9 से शुरू होना चाहिए।"
        },
        "mr": {
            "what": "तुमचा प्राथमिक संपर्क मोबाईल किंवा दूरध्वनी क्रमांक.",
            "input_guidance": "कोणताही देश कोड (+91) न लावता तुमचा चालू १०-अंकी मोबाईल नंबर लिहा.",
            "why": "व्यवहार अलर्ट, OTP पडताळणी कोड पाठवणे आणि संपर्कासाठी आवश्यक.",
            "formats": "१०-अंकी मोबाईल क्रमांक.",
            "example": "9876543210",
            "mistakes": "देश कोड (+91) किंवा सुरुवातीला शून्य ('0') लावणे.",
            "validation": "अचूक १० अंक असावेत आणि सुरुवात ६, ७, ८ किंवा ९ ने व्हावी."
        }
    },
    "alternate_number": {
        "name": "Alternate Number",
        "aliases": ["alternate number", "alternate phone", "alternate mobile", "alt number", "alt phone", "secondary phone", "emergency phone"],
        "en": {
            "what": "A secondary phone number to reach you if the primary is unavailable.",
            "input_guidance": "Enter an active secondary 10-digit mobile number of a family member or yourself.",
            "why": "Acts as a backup communication channel if your main phone is switched off or out of range.",
            "formats": "10-digit numeric sequence.",
            "example": "9876501234",
            "mistakes": "Entering the same number as your primary phone number.",
            "validation": "Must be a valid 10-digit number different from the primary phone number."
        },
        "hi": {
            "what": "प्राथमिक नंबर अनुपलब्ध होने पर आपसे संपर्क करने के लिए एक द्वितीयक फोन नंबर।",
            "input_guidance": "अपने किसी पारिवारिक सदस्य या स्वयं का एक सक्रिय द्वितीयक 10-अंकीय मोबाइल नंबर दर्ज करें।",
            "why": "यदि आपका मुख्य फोन बंद या रेंज से बाहर है, तो बैकअप संचार चैनल के रूप में कार्य करता है।",
            "formats": "10-अंकीय संख्यात्मक अनुक्रम।",
            "example": "9876501234",
            "mistakes": "अपने प्राथमिक फोन नंबर के समान ही नंबर दर्ज करना।",
            "validation": "एक वैध 10-अंकीय नंबर होना चाहिए जो प्राथमिक फोन नंबर से भिन्न हो।"
        },
        "mr": {
            "what": "प्राथमिक मोबाईल क्रमांक व्यस्त किंवा बंद असल्यास वापरण्यासाठी दुसरा क्रमांक.",
            "input_guidance": "तुमच्या कुटुंबातील सदस्याचा किंवा स्वतःचा दुसरा चालू १०-अंकी मोबाईल नंबर लिहा.",
            "why": "मुख्य फोन बंद किंवा कव्हरेज क्षेत्राबाहेर असल्यास पर्यायी संपर्क म्हणून आवश्यक.",
            "formats": "१०-अंकी मोबाईल क्रमांक.",
            "example": "9876501234",
            "mistakes": "प्राथमिक मोबाईल नंबर आणि पर्यायी नंबर एकच लिहिणे.",
            "validation": "प्राथमिक क्रमांकापेक्षा वेगळा असलेला वैध १०-अंकी क्रमांक असावा."
        }
    },
    "email": {
        "name": "Email",
        "aliases": ["email", "email id", "email address", "e-mail", "email_id"],
        "en": {
            "what": "Your active electronic mail mailbox address.",
            "input_guidance": "Enter your complete email address containing '@' and domain extension (like name@example.com).",
            "why": "Required to send official updates, application updates, and payment receipts electronically.",
            "formats": "Standard RFC 5322 email string format.",
            "example": "contact@domain.com",
            "mistakes": "Missing the '@' symbol, typing blank spaces, or misspelling domain suffixes.",
            "validation": "Must be a valid email structure with '@' and domain extension."
        },
        "hi": {
            "what": "आपका सक्रिय इलेक्ट्रॉनिक मेल (ईमेल) पता।",
            "input_guidance": "अपना पूरा ईमेल पता दर्ज करें जिसमें '@' और डोमेन एक्सटेंशन शामिल हो (जैसे name@example.com)।",
            "why": "आधिकारिक अपडेट, आवेदन अपडेट और भुगतान रसीदें इलेक्ट्रॉनिक रूप से भेजने के लिए आवश्यक।",
            "formats": "मानक ईमेल स्ट्रिंग प्रारूप।",
            "example": "contact@domain.com",
            "mistakes": "'@' प्रतीक भूलना, रिक्त स्थान टाइप करना, या डोमेन प्रत्यय गलत लिखना।",
            "validation": "'@' और डोमेन एक्सटेंशन के साथ एक वैध ईमेल संरचना होनी चाहिए।"
        },
        "mr": {
            "what": "तुमचा चालू असलेला ईमेल पत्ता (ईमेल आयडी).",
            "input_guidance": "तुमचा संपूर्ण ईमेल आयडी लिहा, ज्यामध्ये '@' आणि डोमेन नाव समाविष्ट असेल (उदा. name@example.com).",
            "why": "अधिकृत माहिती, अर्जाचे अपडेट्स आणि पावत्या डिजिटल स्वरूपात पाठवण्यासाठी आवश्यक.",
            "formats": "मानक ईमेल स्वरूप.",
            "example": "contact@domain.com",
            "mistakes": "'@' चिन्ह विसरणे, अक्षरांमध्ये स्पेस देणे किंवा डोमेनचे स्पेलिंग चुकणे.",
            "validation": "'@' आणि डोमेनसह वैध ईमेल आयडी असावा."
        }
    },
    "address": {
        "name": "Address",
        "aliases": ["address", "permanent address", "residential address", "correspondence address", "mailing address", "current address", "communication address", "physical address"],
        "en": {
            "what": "Your primary residential or mailing physical location.",
            "input_guidance": "Write your detailed address including house number, street, locality, city, and pincode.",
            "why": "Needed to verify residency, send physical letters, or check regional eligibility.",
            "formats": "Complete text string including PIN code.",
            "example": "Flat 4B, Manish Nagar, Nagpur - 440015",
            "mistakes": "Omitting house/flat numbers, leaving out pincodes, or ignoring local landmarks.",
            "validation": "Must be detailed and contain a postal PIN code."
        },
        "hi": {
            "what": "आपका प्राथमिक आवासीय या पत्राचार का भौतिक स्थान।",
            "input_guidance": "मकान नंबर, गली, इलाका, शहर और पिनकोड सहित अपना विस्तृत पता लिखें।",
            "why": "निवास स्थान को सत्यापित करने, भौतिक पत्र भेजने या क्षेत्रीय पात्रता की जांच करने के लिए आवश्यक।",
            "formats": "पिन कोड सहित पूरा पाठ स्ट्रिंग।",
            "example": "फ्लैट 4बी, मनीष नगर, नागपुर - 440015",
            "mistakes": "मकान/फ्लैट नंबर छोड़ना, पिनकोड छोड़ना, या स्थानीय लैंडमार्क की अनदेखी करना।",
            "validation": "विस्तृत होना चाहिए और इसमें पोस्टल पिनकोड शामिल होना चाहिए।"
        },
        "mr": {
            "what": "तुमचा मूळ रहिवासी किंवा पत्रव्यवहाराचा पत्ता.",
            "input_guidance": "घराचा क्रमांक, रस्ता, परिसर, शहर आणि पिनकोडसह संपूर्ण पत्ता सविस्तर लिहा.",
            "why": "कायदेशीर रहिवासी पुरावा पडताळण्यासाठी आणि कागदपत्रे पोस्टाने पाठवण्यासाठी आवश्यक.",
            "formats": "पिनकोडसह संपूर्ण पत्ता.",
            "example": "फ्लॅट ४बी, मनीष नगर, नागपुर - ४४००१५",
            "mistakes": "घराचा क्रमांक किंवा पिनकोड लिहायला विसरणे.",
            "validation": "पत्ता सविस्तर असावा आणि त्यात पिनकोड समाविष्ट असावा."
        }
    },
    "city": {
        "name": "City",
        "aliases": ["city", "town", "village", "city/town"],
        "en": {
            "what": "The city, town, or village of your residence.",
            "input_guidance": "Enter the name of the city or town where you currently live.",
            "why": "Required for geographic categorizations and local branch mapping.",
            "formats": "Alphabets only.",
            "example": "NAGPUR",
            "mistakes": "Writing state or country names or typing numbers.",
            "validation": "Must not contain digits or special characters."
        },
        "hi": {
            "what": "आपके निवास का शहर, कस्बा या गाँव।",
            "input_guidance": "उस शहर या कस्बे का नाम दर्ज करें जहाँ आप वर्तमान में रहते हैं।",
            "why": "भौगोलिक श्रेणियों और स्थानीय शाखा मानचित्रण के लिए आवश्यक।",
            "formats": "केवल अक्षर।",
            "example": "NAGPUR",
            "mistakes": "राज्य या देश का नाम लिखना या अंक टाइप करना।",
            "validation": "इसमें अंक या विशेष वर्ण नहीं होने चाहिए।"
        },
        "mr": {
            "what": "तुमच्या रहिवासाचे शहर, गाव किंवा तालुका.",
            "input_guidance": "तुम्ही सध्या राहता त्या शहराचे किंवा गावाचे नाव लिहा.",
            "why": "भौगोलिक वर्गीकरण आणि जवळची शाखा निश्चित करण्यासाठी आवश्यक.",
            "formats": "फक्त अक्षरे.",
            "example": "NAGPUR",
            "mistakes": "शहराऐवजी जिल्ह्याचे किंवा राज्याचे नाव लिहिणे.",
            "validation": "यामध्ये अंक किंवा विशेष चिन्हे नसावीत."
        }
    },
    "state": {
        "name": "State",
        "aliases": ["state", "province", "state/ut"],
        "en": {
            "what": "The administrative state or territory of your residence.",
            "input_guidance": "Write the official name of the state or union territory.",
            "why": "Used to check state-specific benefits and regional reservation policies.",
            "formats": "Alphabets only.",
            "example": "MAHARASHTRA",
            "mistakes": "Writing city names or short abbreviations that are unofficial.",
            "validation": "Must be a recognized state or union territory."
        },
        "hi": {
            "what": "आपके निवास का प्रशासनिक राज्य या क्षेत्र।",
            "input_guidance": "राज्य या केंद्र शासित प्रदेश का आधिकारिक नाम लिखें।",
            "why": "राज्य-विशिष्ट लाभों और क्षेत्रीय आरक्षण नीतियों की जांच करने के लिए उपयोग किया जाता है।",
            "formats": "केवल अक्षर।",
            "example": "MAHARASHTRA",
            "mistakes": "शहर का नाम लिखना या अनौपचारिक संक्षिप्त रूप टाइप करना।",
            "validation": "एक मान्यता प्राप्त राज्य या केंद्र शासित प्रदेश होना चाहिए।"
        },
        "mr": {
            "what": "तुमच्या रहिवासाचे राज्य किंवा केंद्रशासित प्रदेश.",
            "input_guidance": "तुमच्या अधिकृत राज्याचे किंवा केंद्रशासित प्रदेशाचे नाव लिहा.",
            "why": "राज्य पातळीवरील योजनांच्या पात्रतेसाठी आवश्यक.",
            "formats": "फक्त अक्षरे.",
            "example": "MAHARASHTRA",
            "mistakes": "राज्याऐवजी देशाचे किंवा शहराचे नाव लिहिणे.",
            "validation": "राज्याचे नाव अधिकृत आणि योग्य असावे."
        }
    },
    "district": {
        "name": "District",
        "aliases": ["district", "county"],
        "en": {
            "what": "The administrative district within your state.",
            "input_guidance": "Enter the name of your official district.",
            "why": "Used for district-wise census categorization, routing files, or local office tracking.",
            "formats": "Alphabets only.",
            "example": "NAGPUR",
            "mistakes": "Confusing it with state name or local post office town.",
            "validation": "Must be a valid recognized district name."
        },
        "hi": {
            "what": "आपके राज्य के भीतर का प्रशासनिक जिला।",
            "input_guidance": "अपने आधिकारिक जिले का नाम दर्ज करें।",
            "why": "जिला-वार जनगणना वर्गीकरण, फाइलों को रूट करने या स्थानीय कार्यालय ट्रैकिंग के लिए उपयोग किया जाता है।",
            "formats": "केवल अक्षर।",
            "example": "NAGPUR",
            "mistakes": "इसे राज्य के नाम या स्थानीय डाकघर शहर के साथ भ्रमित करना।",
            "validation": "एक वैध मान्यता प्राप्त जिला नाम होना चाहिए।"
        },
        "mr": {
            "what": "तुमच्या राज्यातील अधिकृत जिल्हा.",
            "input_guidance": "तुमच्या जिल्ह्याचे नाव लिहा.",
            "why": "स्थानिक प्रशासकीय नोंदी आणि जिल्हा पातळीवरील नियोजनासाठी आवश्यक.",
            "formats": "फक्त अक्षरे.",
            "example": "NAGPUR",
            "mistakes": "जिल्ह्याऐवजी तालुक्याचे किंवा राज्याचे नाव लिहिणे.",
            "validation": "जिल्ह्याचे नाव वैध आणि अधिकृत असावे."
        }
    },
    "country": {
        "name": "Country",
        "aliases": ["country", "nation"],
        "en": {
            "what": "The sovereign country of your physical location.",
            "input_guidance": "Enter the full country name where you live.",
            "why": "Determines international eligibility and tax treaties.",
            "formats": "Country name text.",
            "example": "INDIA",
            "mistakes": "Writing state or continents.",
            "validation": "Must be a valid country."
        },
        "hi": {
            "what": "आपके भौतिक स्थान का संप्रभु देश।",
            "input_guidance": "उस देश का पूरा नाम दर्ज करें जहाँ आप रहते हैं।",
            "why": "अंतरराष्ट्रीय पात्रता और कर संधियों को निर्धारित करता है।",
            "formats": "देश का नाम पाठ।",
            "example": "INDIA",
            "mistakes": "राज्य या महाद्वीप लिखना।",
            "validation": "एक वैध देश होना चाहिए।"
        },
        "mr": {
            "what": "तुमच्या रहिवासाचा देश.",
            "input_guidance": "तुम्ही राहता त्या देशाचे नाव लिहा.",
            "why": "आंतरराष्ट्रीय निकष आणि कर नियमांसाठी आवश्यक.",
            "formats": "देशाचे नाव.",
            "example": "INDIA",
            "mistakes": "देशाऐवजी खंड किंवा राज्याचे नाव लिहिणे.",
            "validation": "देशाचे नाव वैध असावे."
        }
    },
    "pin_code": {
        "name": "PIN Code / ZIP Code",
        "aliases": ["pin code", "pincode", "zip code", "zipcode", "postal code", "pin", "zip"],
        "en": {
            "what": "Your local postal delivery code.",
            "input_guidance": "Enter the 6-digit postal PIN code of your residential address.",
            "why": "Required for post office sorting and geographic location checks.",
            "formats": "Exactly 6 digits (for PIN) or 5-9 alphanumeric (for ZIP).",
            "example": "440015",
            "mistakes": "Typing letters, entering wrong numbers, or leaving blank spaces.",
            "validation": "Must be exactly 6 digits starting with 1-9 (in India)."
        },
        "hi": {
            "what": "आपका स्थानीय डाक वितरण कोड।",
            "input_guidance": "अपने आवासीय पते का 6-अंकीय डाक पिन कोड दर्ज करें।",
            "why": "डाकघर छँटाई और भौगोलिक स्थिति जांच के लिए आवश्यक।",
            "formats": "ठीक 6 अंक (पिन के लिए)।",
            "example": "440015",
            "mistakes": "अक्षर टाइप करना, गलत अंक दर्ज करना, या खाली स्थान छोड़ना।",
            "validation": "1-9 से शुरू होने वाले ठीक 6 अंक होने चाहिए (भारत में)।"
        },
        "mr": {
            "what": "तुमच्या भागाचा टपाल वितरण (पिन) कोड.",
            "input_guidance": "तुमच्या पत्त्याचा ६-अंकी टपाल पिन कोड अचूक लिहा.",
            "why": "टपाल विभाग वर्गीकरण आणि अचूक पत्ता शोधण्यासाठी आवश्यक.",
            "formats": "अचूक ६-अंकी कोड.",
            "example": "440015",
            "mistakes": "अक्षरे लिहिणे, चुकीचा पिनकोड टाकणे.",
            "validation": "भारतात १ ते ९ ने सुरू होणारा अचूक ६-अंकी क्रमांक असावा."
        }
    },

    # PERSONAL
    "dob": {
        "name": "Date of Birth",
        "aliases": ["date of birth", "dob", "birth date", "date birth", "birthdate", "date of birth (dob)", "d.o.b.", "birth_date"],
        "en": {
            "what": "The official calendar date you were born.",
            "input_guidance": "Enter your birth date using DD/MM/YYYY or YYYY-MM-DD format as specified.",
            "why": "Used to verify age criteria limits and chronologically identify your record.",
            "formats": "DD/MM/YYYY or YYYY-MM-DD.",
            "example": "15/08/2000",
            "mistakes": "Confusing day and month order or entering the current year.",
            "validation": "Must be a valid date in the past."
        },
        "hi": {
            "what": "वह आधिकारिक कैलेंडर तिथि जब आप पैदा हुए थे।",
            "input_guidance": "निर्दिष्ट अनुसार DD/MM/YYYY या YYYY-MM-DD प्रारूप का उपयोग करके अपनी जन्म तिथि दर्ज करें।",
            "why": "आयु सीमा मानदंडों को सत्यापित करने और आपके रिकॉर्ड की कालानुक्रमिक पहचान करने के लिए उपयोग किया जाता है।",
            "formats": "DD/MM/YYYY या YYYY-MM-DD।",
            "example": "15/08/2000",
            "mistakes": "दिन और महीने के क्रम को भ्रमित करना या वर्तमान वर्ष दर्ज करना।",
            "validation": "अतीत की एक वैध तिथि होनी चाहिए।"
        },
        "mr": {
            "what": "तुमची अधिकृत जन्मतारीख.",
            "input_guidance": "जन्मतारीख DD/MM/YYYY किंवा YYYY-MM-DD या स्वरूपात लिहा.",
            "why": "अर्जदाराचे वय आणि योजनांच्या पात्रतेचे निकष तपासण्यासाठी आवश्यक.",
            "formats": "DD/MM/YYYY किंवा YYYY-MM-DD.",
            "example": "15/08/2000",
            "mistakes": "तारीख आणि महिना यांच्या क्रमामध्ये गोंधळ करणे किंवा चालू वर्ष टाकणे.",
            "validation": "तारीख भूतकाळातील आणि वैध असावी."
        }
    },
    "age": {
        "name": "Age",
        "aliases": ["age", "years", "current age"],
        "en": {
            "what": "Your current age calculated in completed years.",
            "input_guidance": "Enter your age as a whole positive number representing years.",
            "why": "Required to check eligibility criteria and verify against birth date.",
            "formats": "Positive integer.",
            "example": "24",
            "mistakes": "Writing age in text (like 'twenty-four') or mismatching with date of birth.",
            "validation": "Must be a reasonable positive number (e.g., 0 to 125)."
        },
        "hi": {
            "what": "पूर्ण वर्षों में आंकी गई आपकी वर्तमान आयु।",
            "input_guidance": "वर्षों का प्रतिनिधित्व करने वाले एक पूर्ण सकारात्मक नंबर के रूप में अपनी आयु दर्ज करें।",
            "why": "पात्रता मानदंडों की जांच करने और जन्म तिथि के साथ सत्यापित करने के लिए आवश्यक।",
            "formats": "सकारात्मक पूर्णांक।",
            "example": "24",
            "mistakes": "पाठ में आयु लिखना (जैसे 'चौबीस') या जन्म तिथि के साथ मेल न खाना।",
            "validation": "एक उचित सकारात्मक संख्या होनी चाहिए (जैसे, 0 से 125)।"
        },
        "mr": {
            "what": "वर्षांमध्ये मोजलेले तुमचे सध्याचे वय.",
            "input_guidance": "तुमचे वय केवळ संख्या स्वरूपात लिहा.",
            "why": "पात्रता निकष तपासण्यासाठी आणि जन्मतारखेशी जुळवून घेण्यासाठी आवश्यक.",
            "formats": "सकारात्मक पूर्णांक.",
            "example": "24",
            "mistakes": "अक्षरांमध्ये वय लिहिणे किंवा जन्मतारखेशी विसंगत असणे.",
            "validation": "वय ० ते १२५ च्या दरम्यान एक वैध संख्या असावी."
        }
    },
    "blood_group": {
        "name": "Blood Group",
        "aliases": ["blood group", "blood grp", "bloodgroup", "blood group type"],
        "en": {
            "what": "Your biological blood group classification.",
            "input_guidance": "Enter your blood group including the Rh factor.",
            "why": "Needed for emergency medical treatment and recording health records.",
            "formats": "A+, A-, B+, B-, AB+, AB-, O+, O-.",
            "example": "O+",
            "mistakes": "Entering arbitrary abbreviations or invalid types.",
            "validation": "Must match one of the standard 8 blood groups."
        },
        "hi": {
            "what": "आपका जैविक रक्त समूह वर्गीकरण।",
            "input_guidance": "आरएच कारक सहित अपना रक्त समूह दर्ज करें।",
            "why": "आपातकालीन चिकित्सा उपचार और स्वास्थ्य रिकॉर्ड दर्ज करने के लिए आवश्यक।",
            "formats": "A+, A-, B+, B-, AB+, AB-, O+, O-।",
            "example": "O+",
            "mistakes": "मनमाने संक्षिप्त नाम या अमान्य प्रकार दर्ज करना।",
            "validation": "मानक 8 रक्त समूहों में से किसी एक से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "तुमचा जैविक रक्तगट.",
            "input_guidance": "तुमचा रक्तगट Rh फॅक्टरसह लिहा.",
            "why": "आपत्कालीन वैद्यकीय उपचार आणि आरोग्याची माहिती ठेवण्यासाठी आवश्यक.",
            "formats": "A+, A-, B+, B-, AB+, AB-, O+, O-.",
            "example": "O+",
            "mistakes": "चुकीचा किंवा अमान्य रक्तगट लिहिणे.",
            "validation": "अधिकृत ८ रक्तगटांपैकी एक असावा."
        }
    },
    "occupation": {
        "name": "Occupation",
        "aliases": ["occupation", "profession", "work as", "employment status", "job type"],
        "en": {
            "what": "Your current job, business, or employment status.",
            "input_guidance": "Enter your active profession (e.g. Student, Software Engineer, Business Owner, Retired).",
            "why": "Helps organizations evaluate application relevance, financial status, or job categories.",
            "formats": "Text details.",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "Entering past roles or leaving blank.",
            "validation": "Should represent current employment status."
        },
        "hi": {
            "what": "आपकी वर्तमान नौकरी, व्यवसाय या रोजगार की स्थिति।",
            "input_guidance": "अपना सक्रिय पेशा दर्ज करें (जैसे छात्र, सॉफ्टवेयर इंजीनियर, व्यवसायी, सेवानिवृत्त)।",
            "why": "संगठनों को आवेदन प्रासंगिकता, वित्तीय स्थिति या नौकरी श्रेणियों का मूल्यांकन करने में मदद करता है।",
            "formats": "पाठ विवरण।",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "पिछली भूमिकाएँ दर्ज करना या खाली छोड़ना।",
            "validation": "वर्तमान रोजगार की स्थिति का प्रतिनिधित्व होना चाहिए।"
        },
        "mr": {
            "what": "तुमची सध्याची नोकरी, व्यवसाय किंवा रोजगाराची स्थिती.",
            "input_guidance": "तुमचे सध्याचे काम किंवा व्यवसाय लिहा (उदा. विद्यार्थी, इंजिनिअर, निवृत्त, व्यावसायिक).",
            "why": "आर्थिक कुवत आणि रोजगाराची माहिती तपासण्यासाठी आवश्यक.",
            "formats": "अक्षरे.",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "जुन्या कामाचे नाव लिहिणे किंवा रकाना कोरा ठेवणे.",
            "validation": "चालू रोजगाराची माहिती दर्शवणारे असावे."
        }
    },
    "annual_income": {
        "name": "Annual Income",
        "aliases": ["annual income", "family income", "annual family income", "yearly income", "income", "gross annual income"],
        "en": {
            "what": "The total yearly earnings of your family/household.",
            "input_guidance": "Enter the total annual earnings in digits. Do not include currency symbols or commas.",
            "why": "Determines eligibility for financial concessions, scholarships, or low-income benefits.",
            "formats": "Numeric value.",
            "example": "450000",
            "mistakes": "Adding ₹ symbols, typing commas, or entering monthly income instead of annual.",
            "validation": "Must contain numeric values only."
        },
        "hi": {
            "what": "आपके परिवार/घर की कुल वार्षिक आय।",
            "input_guidance": "अंकों में कुल वार्षिक कमाई दर्ज करें। मुद्रा प्रतीक या अल्पविराम शामिल न करें।",
            "why": "वित्तीय छूट, छात्रवृत्ति, या कम आय वाले लाभों के लिए पात्रता निर्धारित करता है।",
            "formats": "संख्यात्मक मान।",
            "example": "450000",
            "mistakes": "₹ प्रतीक जोड़ना, अल्पविराम टाइप करना, या वार्षिक के बजाय मासिक आय दर्ज करना।",
            "validation": "केवल संख्यात्मक मान होने चाहिए।"
        },
        "mr": {
            "what": "कुटुंबाचे एकूण एकत्रित वार्षिक उत्पन्न.",
            "input_guidance": "फक्त संख्या स्वरूपात वार्षिक उत्पन्न लिहा. चलनाचे चिन्ह किंवा स्वल्पविराम वापरू नका.",
            "why": "विविध शासकीय सवलती किंवा शिष्यवृत्तीच्या पात्रतेसाठी आवश्यक.",
            "formats": "अंक मूल्य.",
            "example": "450000",
            "mistakes": "₹ चिन्ह किंवा स्वल्पविराम वापरणे, किंवा वार्षिक ऐवजी मासिक उत्पन्न लिहिणे.",
            "validation": "फक्त अंकांमध्ये असावे."
        }
    },
    "category": {
        "name": "Category",
        "aliases": ["category", "caste category", "reservation class", "caste", "social status"],
        "en": {
            "what": "Your social caste or reservation category status.",
            "input_guidance": "Select or write your reservation class (e.g. General, OBC, SC, ST, EWS).",
            "why": "Used to apply reservation quotas, fee concessions, and age relaxations.",
            "formats": "General, OBC, SC, ST, EWS.",
            "example": "GENERAL",
            "mistakes": "Selecting a category without having a valid official certificate.",
            "validation": "Must be a valid social category."
        },
        "hi": {
            "what": "आपकी सामाजिक जाति या आरक्षण श्रेणी की स्थिति।",
            "input_guidance": "अपनी आरक्षण श्रेणी चुनें या लिखें (जैसे General, OBC, SC, ST, EWS)।",
            "why": "आरक्षण कोटा, शुल्क रियायतें और आयु छूट लागू करने के लिए उपयोग किया जाता है।",
            "formats": "General, OBC, SC, ST, EWS।",
            "example": "GENERAL",
            "mistakes": "वैध आधिकारिक प्रमाण पत्र के बिना श्रेणी का चयन करना।",
            "validation": "एक वैध सामाजिक श्रेणी होनी चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराची सामाजिक जात किंवा आरक्षण प्रवर्ग.",
            "input_guidance": "तुमचा आरक्षित प्रवर्ग निवडा किंवा लिहा (उदा. General, OBC, SC, ST, EWS).",
            "why": "फी सवलत किंवा आरक्षित जागांच्या नियमांची अंमलबजावणी करण्यासाठी आवश्यक.",
            "formats": "General, OBC, SC, ST, EWS.",
            "example": "GENERAL",
            "mistakes": "अधिकृत जात प्रमाणपत्र नसतानाही आरक्षित प्रवर्गाची निवड करणे.",
            "validation": "प्रवर्ग वैध आणि अधिकृत यादीतील असावा."
        }
    },
    "religion": {
        "name": "Religion",
        "aliases": ["religion", "faith", "creed", "religious community"],
        "en": {
            "what": "Your religious faith or community affiliation.",
            "input_guidance": "Enter your religion (e.g. Hindu, Muslim, Christian, Sikh, Buddhist, Jain).",
            "why": "Required for demographic records, minority scholarships eligibility check.",
            "formats": "Text name.",
            "example": "HINDU",
            "mistakes": "Writing caste instead of religion details.",
            "validation": "Must be a recognized religion."
        },
        "hi": {
            "what": "आपका धार्मिक विश्वास या समुदाय संबद्धता।",
            "input_guidance": "अपना धर्म दर्ज करें (जैसे हिंदू, मुस्लिम, ईसाई, सिख, बौद्ध, जैन)।",
            "why": "जनसांख्यिकीय रिकॉर्ड, अल्पसंख्यक छात्रवृत्ति पात्रता जांच के लिए आवश्यक।",
            "formats": "पाठ का नाम।",
            "example": "HINDU",
            "mistakes": "धर्म के विवरण के बजाय जाति लिखना।",
            "validation": "एक मान्यता प्राप्त धर्म होना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराचा धर्म.",
            "input_guidance": "तुमचा धर्म लिहा (उदा. हिंदू, मुस्लिम, ख्रिश्चन, शीख, बौद्ध, जैन).",
            "why": "अल्पसंख्याक योजना किंवा सामाजिक नोंदींसाठी आवश्यक.",
            "formats": "धर्माचे नाव.",
            "example": "HINDU",
            "mistakes": "धर्माऐवजी जातीचे नाव लिहिणे.",
            "validation": "अधिकृत आणि योग्य नोंद असावी."
        }
    },

    # EDUCATION
    "school_name": {
        "name": "School Name",
        "aliases": ["school name", "school", "last school", "previous school", "school attended", "name of school"],
        "en": {
            "what": "The official registered name of your school.",
            "input_guidance": "Enter the complete, registered name of your school as shown on your certificates.",
            "why": "Needed to verify academic enrollment and validate your school credentials.",
            "formats": "Text institution name.",
            "example": "DELHI PUBLIC SCHOOL",
            "mistakes": "Entering local school abbreviations instead of the full official name.",
            "validation": "Must contain at least 3 characters."
        },
        "hi": {
            "what": "आपके स्कूल का आधिकारिक पंजीकृत नाम।",
            "input_guidance": "अपने प्रमाण पत्रों पर दिखाए अनुसार अपने स्कूल का पूरा पंजीकृत नाम दर्ज करें।",
            "why": "शैक्षणिक नामांकन को सत्यापित करने और आपके स्कूल क्रेडेंशियल्स को मान्य करने के लिए आवश्यक।",
            "formats": "पाठ संस्थान का नाम।",
            "example": "DELHI PUBLIC SCHOOL",
            "mistakes": "पूरे आधिकारिक नाम के बजाय स्थानीय स्कूल के संक्षिप्त रूपों को दर्ज करना।",
            "validation": "कम से कम 3 वर्ण होने चाहिए।"
        },
        "mr": {
            "what": "तुमच्या शाळेचे अधिकृत नोंदणीकृत नाव.",
            "input_guidance": "गुणपत्रकावर असल्याप्रमाणे तुमच्या शाळेचे पूर्ण नाव लिहा.",
            "why": "तुमची शैक्षणिक पार्श्वभूमी तपासण्यासाठी आवश्यक.",
            "formats": "शाळेचे नाव.",
            "example": "DELHI PUBLIC SCHOOL",
            "mistakes": "शाळेच्या अधिकृत नावाऐवजी स्थानिक संक्षिप्त नाव लिहिणे.",
            "validation": "किमान ३ अक्षरे असणे आवश्यक."
        }
    },
    "college_name": {
        "name": "College Name",
        "aliases": ["college name", "college", "previous college", "college attended", "name of college"],
        "en": {
            "what": "The registered name of your college or institute.",
            "input_guidance": "Enter the full legal name of your college/institute as printed on marksheets.",
            "why": "Used to verify higher education details and institutional records.",
            "formats": "Text institution name.",
            "example": "ST. XAVIER'S COLLEGE",
            "mistakes": "Using informal college codes or department nicknames.",
            "validation": "Must contain at least 3 characters."
        },
        "hi": {
            "what": "आपके कॉलेज या संस्थान का पंजीकृत नाम।",
            "input_guidance": "अंकपत्रों पर मुद्रित अपने कॉलेज/संस्थान का पूरा कानूनी नाम दर्ज करें।",
            "why": "उच्च शिक्षा विवरण और संस्थागत रिकॉर्ड को सत्यापित करने के लिए उपयोग किया जाता है।",
            "formats": "पाठ संस्थान का नाम।",
            "example": "ST. XAVIER'S COLLEGE",
            "mistakes": "अनौपचारिक कॉलेज कोड या विभाग के उपनामों का उपयोग करना।",
            "validation": "कम से कम 3 वर्ण होने चाहिए।"
        },
        "mr": {
            "what": "तुमच्या कॉलेजचे अधिकृत नाव.",
            "input_guidance": "गुणपत्रकावर छापल्याप्रमाणे तुमच्या कॉलेजचे पूर्ण नाव लिहा.",
            "why": "उच्च शिक्षणाची शैक्षणिक पार्श्वभूमी तपासण्यासाठी आवश्यक.",
            "formats": "कॉलेजचे नाव.",
            "example": "ST. XAVIER'S COLLEGE",
            "mistakes": "कॉलेज कोड किंवा अनधिकृत संक्षेप वापरणे.",
            "validation": "किमान ३ अक्षरे असणे आवश्यक."
        }
    },
    "university": {
        "name": "University",
        "aliases": ["university", "board", "board/university", "board or university", "university name", "board name"],
        "en": {
            "what": "The affiliated university or board of education.",
            "input_guidance": "Enter the official name of the university or board of education (e.g. CBSE, Mumbai University).",
            "why": "Required to validate the authenticity of your educational degree/certificate.",
            "formats": "Text name.",
            "example": "MUMBAI UNIVERSITY or CBSE",
            "mistakes": "Writing college name here instead of the affiliating university/board.",
            "validation": "Must be a valid recognized educational board or university."
        },
        "hi": {
            "what": "संबद्ध विश्वविद्यालय या शिक्षा बोर्ड।",
            "input_guidance": "विश्वविद्यालय या शिक्षा बोर्ड का आधिकारिक नाम दर्ज करें (जैसे CBSE, मुंबई विश्वविद्यालय)।",
            "why": "आपकी शैक्षणिक डिग्री/प्रमाण पत्र की प्रामाणिकता को मान्य करने के लिए आवश्यक।",
            "formats": "पाठ का नाम।",
            "example": "MUMBAI UNIVERSITY or CBSE",
            "mistakes": "संबद्ध विश्वविद्यालय/बोर्ड के बजाय यहाँ कॉलेज का नाम लिखना।",
            "validation": "एक वैध मान्यता प्राप्त शिक्षा बोर्ड या विश्वविद्यालय होना चाहिए।"
        },
        "mr": {
            "what": "संबद्ध विद्यापीठ किंवा शैक्षणिक मंडळ (Board).",
            "input_guidance": "शैक्षणिक मंडळ किंवा विद्यापीठाचे नाव लिहा (उदा. CBSE, मुंबई विद्यापीठ).",
            "why": "तुमच्या शैक्षणिक पदवीची अधिकृतता तपासण्यासाठी आवश्यक.",
            "formats": "विद्यापीठ किंवा बोर्डाचे नाव.",
            "example": "MUMBAI UNIVERSITY or CBSE",
            "mistakes": "विद्यापीठाऐवजी स्वतःच्या कॉलेजचे नाव लिहिणे.",
            "validation": "मान्यताप्राप्त बोर्ड किंवा विद्यापीठाचे नाव असावे."
        }
    },
    "degree": {
        "name": "Degree",
        "aliases": ["degree", "qualification", "highest qualification", "course/degree", "educational qualification"],
        "en": {
            "what": "The educational qualification title attained or pursued.",
            "input_guidance": "Enter the title of the degree or diploma (e.g., Bachelor of Science, High School, Diploma).",
            "why": "Used to assess educational eligibility levels for admissions or job roles.",
            "formats": "Text credential name.",
            "example": "BACHELOR OF SCIENCE (B.SC)",
            "mistakes": "Writing course streams without specifying the degree type.",
            "validation": "Should match standard qualification levels."
        },
        "hi": {
            "what": "शैक्षणिक योग्यता शीर्षक जो प्राप्त किया गया है या जिसके लिए अध्ययन किया जा रहा है।",
            "input_guidance": "डिग्री या डिप्लोमा का शीर्षक दर्ज करें (जैसे, बैचलर ऑफ साइंस, हाई स्कूल, डिप्लोमा)।",
            "why": "प्रवेश या नौकरी की भूमिकाओं के लिए शैक्षणिक पात्रता स्तरों का आकलन करने के लिए उपयोग किया जाता है।",
            "formats": "पाठ क्रेडेंशियल का नाम।",
            "example": "BACHELOR OF SCIENCE (B.SC)",
            "mistakes": "डिग्री प्रकार निर्दिष्ट किए बिना पाठ्यक्रम स्ट्रीम लिखना।",
            "validation": "मानक योग्यता स्तरों से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "मिळालेली किंवा करत असलेली शैक्षणिक पदवी.",
            "input_guidance": "तुमच्या पदवीचे नाव लिहा (उदा. Bachelor of Science, Diploma).",
            "why": "नोकरी किंवा प्रवेशासाठी पात्रता तपासण्यासाठी आवश्यक.",
            "formats": "पदवीचे नाव.",
            "example": "BACHELOR OF SCIENCE (B.SC)",
            "mistakes": "पदवीचा प्रकार न लिहिता फक्त विषयाचे नाव लिहिणे.",
            "validation": "योग्य शैक्षणिक पदवीचे नाव असावे."
        }
    },
    "course": {
        "name": "Course",
        "aliases": ["course", "branch", "stream", "specialization", "program", "programme", "subject"],
        "en": {
            "what": "Your specific stream, course branch, or field of study.",
            "input_guidance": "Enter the name of your course or study branch (e.g., Computer Science, Mechanical Engineering, Commerce).",
            "why": "Determines branch/stream eligibility and department assignments.",
            "formats": "Alphabets text.",
            "example": "COMPUTER SCIENCE",
            "mistakes": "Confusing it with degree or college code.",
            "validation": "Must be a valid study course or branch."
        },
        "hi": {
            "what": "आपकी विशिष्ट शाखा, पाठ्यक्रम शाखा, या अध्ययन का क्षेत्र।",
            "input_guidance": "अपने पाठ्यक्रम या अध्ययन शाखा का नाम दर्ज करें (जैसे, कंप्यूटर साइंस, मैकेनिकल इंजीनियरिंग, कॉमर्स)।",
            "why": "शाखा/स्ट्रीम पात्रता और विभाग असाइनमेंट निर्धारित करता है।",
            "formats": "अक्षर पाठ।",
            "example": "COMPUTER SCIENCE",
            "mistakes": "इसे डिग्री या कॉलेज कोड के साथ भ्रमित करना।",
            "validation": "एक वैध अध्ययन पाठ्यक्रम या शाखा होनी चाहिए।"
        },
        "mr": {
            "what": "तुमची विशिष्ट शैक्षणिक शाखा किंवा अभ्यासक्रम.",
            "input_guidance": "तुमच्या अभ्यासक्रमाचे नाव लिहा (उदा. Computer Science, Commerce).",
            "why": "अभ्यासक्रमाच्या पात्रतेनुसार प्रवेश देण्यासाठी आवश्यक.",
            "formats": "अभ्यासक्रमाचे नाव.",
            "example": "COMPUTER SCIENCE",
            "mistakes": "पदवीचे नाव आणि अभ्यासक्रमाचे नाव यात गोंधळ करणे.",
            "validation": "योग्य अभ्यासक्रम किंवा शाखेचे नाव असावे."
        }
    },
    "percentage": {
        "name": "Percentage",
        "aliases": ["percentage", "marks %", "percent", "percentage of marks", "aggregate marks"],
        "en": {
            "what": "Your overall academic marks percentage.",
            "input_guidance": "Enter your final percentage score out of 100. Decimal fractions are allowed.",
            "why": "Used to evaluate academic rankings, eligibility cut-offs, or merit admissions.",
            "formats": "Decimal score between 0.0 and 100.0.",
            "example": "85.5",
            "mistakes": "Adding % symbol, or converting CGPA to percentage incorrectly.",
            "validation": "Must be between 0.0 and 100.0."
        },
        "hi": {
            "what": "आपका कुल शैक्षणिक अंक प्रतिशत।",
            "input_guidance": "100 में से अपना अंतिम प्रतिशत स्कोर दर्ज करें। दशमलव अंशों की अनुमति है।",
            "why": "शैक्षणिक रैंकिंग, पात्रता कट-ऑफ या मेरिट प्रवेश का मूल्यांकन करने के लिए उपयोग किया जाता है।",
            "formats": "0.0 और 100.0 के बीच दशमलव स्कोर।",
            "example": "85.5",
            "mistakes": "% प्रतीक जोड़ना, या सीजीपीए को गलत तरीके से प्रतिशत में बदलना।",
            "validation": "0.0 और 100.0 के बीच होना चाहिए।"
        },
        "mr": {
            "what": "शैक्षणिक परीक्षेत मिळालेली गुणांची टक्केवारी.",
            "input_guidance": "१०० पैकी मिळालेले एकूण टक्के लिहा. टक्केवारीचे चिन्ह वापरू नका.",
            "why": "गुणवत्ता यादी किंवा प्रवेश निकषांची पडताळणी करण्यासाठी आवश्यक.",
            "formats": "०.० ते १००.० च्या दरम्यान संख्या.",
            "example": "85.5",
            "mistakes": "टक्केवारीचे (%) चिन्ह जोडणे, किंवा सीजीपीएचे टक्केवारीमध्ये चुकीचे रूपांतर करणे.",
            "validation": "०.० ते १००.० च्या दरम्यान असावी."
        }
    },
    "cgpa": {
        "name": "CGPA",
        "aliases": ["cgpa", "gpa", "cumulative grade point average", "sgpa", "grades"],
        "en": {
            "what": "Your cumulative grade point average academic score.",
            "input_guidance": "Enter your CGPA score out of the maximum grade scale (usually 10).",
            "why": "Required to check grade-point averages on standard grade charts.",
            "formats": "Decimal number (e.g. 0.0 to 10.0).",
            "example": "8.65",
            "mistakes": "Confusing SGPA with CGPA, or writing CGPA without decimal points.",
            "validation": "Must be between 0.0 and 10.0 (or matching scale limit)."
        },
        "hi": {
            "what": "आपका संचयी ग्रेड पॉइंट औसत शैक्षणिक स्कोर।",
            "input_guidance": "अधिकतम ग्रेड स्केल (आमतौर पर 10) में से अपना सीजीपीए स्कोर दर्ज करें।",
            "why": "मानक ग्रेड चार्ट पर ग्रेड-पॉइंट औसत की जांच करने के लिए आवश्यक।",
            "formats": "दशमलव संख्या (जैसे 0.0 से 10.0)।",
            "example": "8.65",
            "mistakes": "एसजीपीए को सीजीपीए के साथ भ्रमित करना, या बिना दशमलव बिंदु के सीजीपीए लिखना।",
            "validation": "0.0 और 10.0 के बीच होना चाहिए।"
        },
        "mr": {
            "what": "शैक्षणिक परीक्षेतील सीजीपीए (Cumulative Grade Point Average).",
            "input_guidance": "१० पैकी किंवा कमाल ग्रेड स्केल पैकी मिळालेला सीजीपीए लिहा.",
            "why": "गुणवत्ता पडताळणीसाठी आवश्यक.",
            "formats": "दशांश संख्या (०.० ते १०.०).",
            "example": "8.65",
            "mistakes": "एसजीपीए आणि सीजीपीए यात गफलत करणे, किंवा या रकान्यात दशांश चिन्ह न लावणे.",
            "validation": "०.० ते १०.० च्या दरम्यान असावा."
        }
    },
    "passing_year": {
        "name": "Passing Year",
        "aliases": ["passing year", "year of passing", "year of graduation", "graduation year", "year of completion", "year"],
        "en": {
            "what": "The calendar year you completed your education program.",
            "input_guidance": "Enter the 4-digit calendar year when you passed the examination.",
            "why": "Used to assess educational gaps and check timeline eligibility limits.",
            "formats": "4-digit year format (YYYY).",
            "example": "2024",
            "mistakes": "Entering the date of result declaration instead of the year, or using 2 digits.",
            "validation": "Must be a valid 4-digit year not in the future."
        },
        "hi": {
            "what": "वह कैलेंडर वर्ष जब आपने अपना शिक्षा कार्यक्रम पूरा किया।",
            "input_guidance": "4-अंकीय कैलेंडर वर्ष दर्ज करें जब आपने परीक्षा उत्तीर्ण की थी।",
            "why": "शैक्षणिक अंतराल का आकलन करने और समयरेखा पात्रता सीमाओं की जांच करने के लिए उपयोग किया जाता है।",
            "formats": "4-अंकीय वर्ष प्रारूप (YYYY)।",
            "example": "2024",
            "mistakes": "वर्ष के बजाय परिणाम घोषित होने की तिथि दर्ज करना, या 2 अंकों का उपयोग करना।",
            "validation": "एक वैध 4-अंकीय वर्ष होना चाहिए जो भविष्य में न हो।"
        },
        "mr": {
            "what": "परीक्षा किंवा शिक्षण उत्तीर्ण झाल्याचे वर्ष.",
            "input_guidance": "परीक्षा उत्तीर्ण झाल्याचे ४-अंकीय वर्ष लिहा.",
            "why": "शिक्षणातील अंतर (academic gap) तपासण्यासाठी आवश्यक.",
            "formats": "४-अंकीय वर्ष (YYYY).",
            "example": "2024",
            "mistakes": "कमाल वर्ष किंवा २-अंकीय वर्ष लिहिणे.",
            "validation": "वैध ४-अंकीय वर्ष असावे जे भविष्यातील नसेल."
        }
    },
    "roll_number": {
        "name": "Roll Number",
        "aliases": ["roll number", "roll no", "seat number", "seat no", "examination roll no", "class roll no"],
        "en": {
            "what": "Your unique academic identification roll or seat code.",
            "input_guidance": "Write your roll or seat number exactly as printed on your admit card or marksheet.",
            "why": "Required to query database records, verify examination enrollment, and check mark sheets.",
            "formats": "Alphanumeric text.",
            "example": "42 or EXAM-9988",
            "mistakes": "Writing class section or incorrect exam branch codes.",
            "validation": "Should match board/university registration formats."
        },
        "hi": {
            "what": "आपका अद्वितीय शैक्षणिक पहचान रोल या सीट कोड।",
            "input_guidance": "अपना रोल या सीट नंबर बिल्कुल वैसे ही लिखें जैसे आपके एडमिट कार्ड या अंकपत्र पर मुद्रित है।",
            "why": "डेटाबेस रिकॉर्ड्स को क्वेरी करने, परीक्षा नामांकन को सत्यापित करने और अंक तालिकाओं की जांच करने के लिए आवश्यक।",
            "formats": "अल्फ़ान्यूमेरिक पाठ।",
            "example": "42 or EXAM-9988",
            "mistakes": "कक्षा अनुभाग या गलत परीक्षा शाखा कोड लिखना।",
            "validation": "बोर्ड/विश्वविद्यालय पंजीकरण प्रारूपों से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "शैक्षणिक ओळख सांगणारा रोल नंबर किंवा सीट नंबर.",
            "input_guidance": "तुमच्या प्रवेशपत्रावर (Admit Card) किंवा गुणपत्रकावर छापलेला रोल नंबर अचूक लिहा.",
            "why": "परीक्षा नोंदी आणि निकालांची पडताळणी करण्यासाठी आवश्यक.",
            "formats": "संख्या किंवा अक्षरे.",
            "example": "42 or EXAM-9988",
            "mistakes": "घरी असलेला वर्ग नंबर लिहिणे किंवा परीक्षा क्रमांक चुकीचा टाकणे.",
            "validation": "अधिकृत परीक्षा क्रमांकाशी जुळणारे असावे."
        }
    },
    "registration_number": {
        "name": "Registration Number",
        "aliases": ["registration number", "registration no", "reg no", "enrollment number", "enrollment no", "enrolment number", "enrolment no", "admission number", "admission no"],
        "en": {
            "what": "Your official student registration or enrollment ID.",
            "input_guidance": "Write the unique enrollment or registration number given by your board/university.",
            "why": "Uniquely maps you in the board or university database across multiple courses.",
            "formats": "Alphanumeric identity code.",
            "example": "2024/ED/0101",
            "mistakes": "Confusing registration number with temporary admission roll number.",
            "validation": "Must be filled accurately according to certificates."
        },
        "hi": {
            "what": "आपका आधिकारिक छात्र पंजीकरण या नामांकन आईडी।",
            "input_guidance": "अपने बोर्ड/विश्वविद्यालय द्वारा दिए गए अद्वितीय नामांकन या पंजीकरण संख्या को लिखें।",
            "why": "विश्वविद्यालय या बोर्ड डेटाबेस में आपको कई पाठ्यक्रमों में विशिष्ट रूप से मानचित्रित करता है।",
            "formats": "अल्फ़ान्यूमेरिक पहचान कोड।",
            "example": "2024/ED/0101",
            "mistakes": "पंजीकरण संख्या को अस्थायी प्रवेश रोल नंबर के साथ भ्रमित करना।",
            "validation": "प्रमाण पत्रों के अनुसार सटीक रूप से भरा जाना चाहिए।"
        },
        "mr": {
            "what": "विद्यापीठ किंवा शैक्षणिक मंडळाने दिलेला नोंदणी (Registration) किंवा प्रवेश क्रमांक.",
            "input_guidance": "तुमचा अधिकृत नोंदणी किंवा एनरॉलमेंट क्रमांक लिहा.",
            "why": "शैक्षणिक रेकॉर्डमध्ये विद्यार्थ्याची पडताळणी करण्यासाठी आवश्यक.",
            "formats": "अक्षरे आणि संख्या.",
            "example": "2024/ED/0101",
            "mistakes": "अस्थायी वर्ग क्रमांक आणि नोंदणी क्रमांक यात गोंधळ करणे.",
            "validation": "अधिकृत प्रमाणपत्रांनुसार अचूक असणे आवश्यक."
        }
    },

    # EMPLOYMENT
    "employee_id": {
        "name": "Employee ID",
        "aliases": ["employee id", "emp id", "employee code", "staff id", "staff code"],
        "en": {
            "what": "Your unique staff identification number.",
            "input_guidance": "Enter your official company employee code.",
            "why": "Used to pull your profile, process payroll, and log workspace parameters.",
            "formats": "Alphanumeric code.",
            "example": "EMP10123",
            "mistakes": "Typing wrong numbers or leaving it blank.",
            "validation": "Must match company employee ID structure."
        },
        "hi": {
            "what": "आपका अद्वितीय कर्मचारी पहचान नंबर।",
            "input_guidance": "अपना आधिकारिक कंपनी कर्मचारी कोड दर्ज करें।",
            "why": "आपकी प्रोफ़ाइल प्राप्त करने, पेरोल संसाधित करने और कार्यस्थान मापदंडों को लॉग करने के लिए उपयोग किया जाता है।",
            "formats": "अल्फ़ान्यूमेरिक कोड।",
            "example": "EMP10123",
            "mistakes": "गलत नंबर टाइप करना या इसे खाली छोड़ना।",
            "validation": "कंपनी कर्मचारी आईडी संरचना से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "कंपनी किंवा संस्थेने दिलेला तुमचा कर्मचारी ओळख (Employee ID) क्रमांक.",
            "input_guidance": "तुमचा अधिकृत एम्प्लॉई कोड लिहा.",
            "why": "पेरोल, कर्मचारी पडताळणी आणि प्रशासकीय नोंदींसाठी आवश्यक.",
            "formats": "अक्षरे आणि संख्या.",
            "example": "EMP10123",
            "mistakes": "चुकीचा कोड टाकणे किंवा रकाना मोकळा सोडणे.",
            "validation": "अधिकृत आयडीनुसार जुळणारे असावे."
        }
    },
    "designation": {
        "name": "Designation",
        "aliases": ["designation", "job title", "role", "position"],
        "en": {
            "what": "Your official job title or position in the company.",
            "input_guidance": "Enter your official corporate title (e.g. Senior Manager, Executive Officer).",
            "why": "Determines job hierarchical levels and authorization levels.",
            "formats": "Text title.",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "Writing casual roles instead of official corporate designations.",
            "validation": "Should match employment records."
        },
        "hi": {
            "what": "कंपनी में आपका आधिकारिक नौकरी शीर्षक या पद।",
            "input_guidance": "अपना आधिकारिक कॉर्पोरेट शीर्षक दर्ज करें (जैसे वरिष्ठ प्रबंधक, कार्यकारी अधिकारी)।",
            "why": "नौकरी के पदानुक्रमित स्तरों और प्राधिकरण स्तरों को निर्धारित करता है।",
            "formats": "पाठ शीर्षक।",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "आधिकारिक कॉर्पोरेट पदनामों के बजाय आकस्मिक भूमिकाएँ लिखना।",
            "validation": "रोजगार रिकॉर्ड से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "कंपनी किंवा संस्थेतील तुमचे अधिकृत पद (Designation).",
            "input_guidance": "तुमचे अधिकृत पद लिहा (उदा. Senior Manager, Software Engineer).",
            "why": "पदाची श्रेणी आणि कार्य अधिकार निश्चित करण्यासाठी आवश्यक.",
            "formats": "पदाचे नाव.",
            "example": "SOFTWARE ENGINEER",
            "mistakes": "अनधिकृत किंवा घरगुती कामाचे स्वरूप लिहिणे.",
            "validation": "अधिकृत नियुक्ती पत्रावरील पदाशी जुळले पाहिजे."
        }
    },
    "department": {
        "name": "Department",
        "aliases": ["department", "dept", "department name"],
        "en": {
            "what": "The internal organizational division you work in.",
            "input_guidance": "Enter your functional department (e.g., Human Resources, Finance, IT).",
            "why": "Determines team grouping, budget routing, and task assignments.",
            "formats": "Text name.",
            "example": "INFORMATION TECHNOLOGY",
            "mistakes": "Confusing department with general company role.",
            "validation": "Must be a valid department name."
        },
        "hi": {
            "what": "आंतरिक संगठनात्मक प्रभाग जिसमें आप काम करते हैं।",
            "input_guidance": "अपने कार्यात्मक विभाग का नाम दर्ज करें (जैसे, मानव संसाधन, वित्त, आईटी)।",
            "why": "टीम समूहीकरण, बजट रूटिंग और कार्य असाइनमेंट निर्धारित करता है।",
            "formats": "पाठ का नाम।",
            "example": "INFORMATION TECHNOLOGY",
            "mistakes": "विभाग को सामान्य कंपनी भूमिका के साथ भ्रमित करना।",
            "validation": "एक वैध विभाग नाम होना चाहिए।"
        },
        "mr": {
            "what": "कंपनी किंवा संस्थेतील तुमचा विभाग (Department).",
            "input_guidance": "तुमच्या विभागाचे नाव लिहा (उदा. HR, Finance, IT).",
            "why": "कामाचे वर्गीकरण आणि कार्यालयीन रचनेसाठी आवश्यक.",
            "formats": "विभागाचे नाव.",
            "example": "INFORMATION TECHNOLOGY",
            "mistakes": "विभागाऐवजी कामाचे स्वरूप लिहिणे.",
            "validation": "विभागाचे नाव वैध असावे."
        }
    },
    "company_name": {
        "name": "Company Name",
        "aliases": ["company name", "organization name", "employer name", "employer", "company"],
        "en": {
            "what": "The registered legal name of your employer or firm.",
            "input_guidance": "Enter the complete registered name of your company or business entity.",
            "why": "Required to check employment credentials or business tax structures.",
            "formats": "Organization name text.",
            "example": "GLOBAL TECH INDUSTRIES INC.",
            "mistakes": "Writing department names instead of the registered company group name.",
            "validation": "Must match company registration records."
        },
        "hi": {
            "what": "आपके नियोक्ता या फर्म का पंजीकृत कानूनी नाम।",
            "input_guidance": "अपनी कंपनी या व्यावसायिक इकाई का पूरा पंजीकृत नाम दर्ज करें।",
            "why": "रोजगार क्रेडेंशियल या व्यावसायिक कर संरचनाओं की जांच करने के लिए आवश्यक।",
            "formats": "संगठन का नाम पाठ।",
            "example": "GLOBAL TECH INDUSTRIES INC.",
            "mistakes": "पंजीकरण कंपनी समूह के नाम के बजाय विभाग का नाम लिखना।",
            "validation": "company पंजीकरण रिकॉर्ड से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "तुमच्या नियोक्ता कंपनीचे किंवा फर्मचे नोंदणीकृत नाव.",
            "input_guidance": "कंपनी किंवा संस्थेचे अधिकृत नोंदणीकृत नाव लिहा.",
            "why": "रोजगार पडताळणी किंवा कर दस्तऐवजांसाठी आवश्यक.",
            "formats": "कंपनीचे नाव.",
            "example": "GLOBAL TECH INDUSTRIES INC.",
            "mistakes": "शाखेच्या नावाऐवजी स्थानिक विभागाचे नाव लिहिणे.",
            "validation": "नोंदणीकृत कंपनीच्या नावाशी जुळले पाहिजे."
        }
    },
    "experience": {
        "name": "Experience",
        "aliases": ["experience", "years of experience", "total experience", "work experience", "exp"],
        "en": {
            "what": "Your total employment tenure in years/months.",
            "input_guidance": "Enter your work tenure in years. Decimal fractions are allowed.",
            "why": "Used to check senior eligibility levels and process candidate selections.",
            "formats": "Decimal number or positive integer.",
            "example": "5.5",
            "mistakes": "Entering past non-relevant jobs tenure.",
            "validation": "Must be a positive value."
        },
        "hi": {
            "what": "वर्षों/महीनों में आपका कुल रोजगार कार्यकाल।",
            "input_guidance": "वर्षों में अपना कार्य कार्यकाल दर्ज करें। दशमलव अंशों की अनुमति है।",
            "why": "वरिष्ठ पात्रता स्तरों की जांच करने और उम्मीदवार चयन को संसाधित करने के लिए उपयोग किया जाता है।",
            "formats": "दशमलव संख्या या सकारात्मक पूर्णांक।",
            "example": "5.5",
            "mistakes": "विगत अप्रासंगिक नौकरियों के कार्यकाल को दर्ज करना।",
            "validation": "एक सकारात्मक मान होना चाहिए।"
        },
        "mr": {
            "what": "तुमचा एकूण कामाचा अनुभव (वर्षे किंवा महिन्यांत).",
            "input_guidance": "तुमच्या अनुभवाचा कालावधी फक्त संख्या स्वरूपात लिहा.",
            "why": "वरिष्ठता, पात्रता आणि वेतनश्रेणी ठरवण्यासाठी आवश्यक.",
            "formats": "दशांश संख्या किंवा पूर्णांक.",
            "example": "5.5",
            "mistakes": "असंबंधित कामाचा कालावधी समाविष्ट करणे.",
            "validation": "अनुभव संख्या सकारात्मक असावी."
        }
    },
    "salary": {
        "name": "Salary",
        "aliases": ["salary", "basic salary", "ctc", "monthly salary", "package", "net salary"],
        "en": {
            "what": "Your official compensation value.",
            "input_guidance": "Enter your salary in digits. Specify whether it is monthly or annual.",
            "why": "Used to calculate taxes, check financial capacity, or determine insurance limits.",
            "formats": "Numeric value.",
            "example": "75000",
            "mistakes": "Adding currency signs or comma characters.",
            "validation": "Must contain numeric values only."
        },
        "hi": {
            "what": "आपका आधिकारिक मुआवजा मान।",
            "input_guidance": "अंकों में अपना वेतन दर्ज करें। निर्दिष्ट करें कि यह मासिक है या वार्षिक।",
            "why": "करों की गणना करने, वित्तीय क्षमता की जांच करने या बीमा सीमा निर्धारित करने के लिए उपयोग किया जाता है।",
            "formats": "संख्यात्मक मान।",
            "example": "75000",
            "mistakes": "मुद्रा चिह्न या अल्पविराम वर्ण जोड़ना।",
            "validation": "केवल संख्यात्मक मान होने चाहिए।"
        },
        "mr": {
            "what": "मिळणारे मासिक किंवा वार्षिक वेतन (Salary).",
            "input_guidance": "वेतन केवळ अंकांमध्ये लिहा. चलनाचे चिन्ह किंवा स्वल्पविराम वापरू नका.",
            "why": "कर आकारणी किंवा आर्थिक पडताळणीसाठी आवश्यक.",
            "formats": "संख्या.",
            "example": "75000",
            "mistakes": "₹ चिन्ह लावणे किंवा चुकीची रक्कम लिहिणे.",
            "validation": "संख्या स्वरूपात असावे."
        }
    },

    # HEALTHCARE
    "mrn_number": {
        "name": "MRN Number",
        "aliases": ["mrn number", "mrn", "medical record number", "patient id", "case number", "mrn no", "patient code"],
        "en": {
            "what": "Your unique hospital medical record number.",
            "input_guidance": "Write your 6-12 digit MRN as printed on your hospital patient card.",
            "why": "Used to pull your past medical records and history in the hospital network database.",
            "formats": "Alphanumeric code.",
            "example": "MRN-554422",
            "mistakes": "Typing local bed numbers instead of MRN code.",
            "validation": "Must match hospital MRN formatting guidelines."
        },
        "hi": {
            "what": "आपका अद्वितीय अस्पताल चिकित्सा रिकॉर्ड नंबर।",
            "input_guidance": "अस्पताल के मरीज कार्ड पर मुद्रित अपना 6-12 अंकीय एमआरएन लिखें।",
            "why": "अस्पताल नेटवर्क डेटाबेस में आपके पिछले चिकित्सा रिकॉर्ड और इतिहास को प्राप्त करने के लिए उपयोग किया जाता है।",
            "formats": "अल्फ़ान्यूमेरिक कोड।",
            "example": "MRN-554422",
            "mistakes": "एमआरएन कोड के बजाय स्थानीय बिस्तर संख्या टाइप करना।",
            "validation": "अस्पताल के एमआरएन स्वरूपण दिशानिर्देशों से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "रुग्णालयाचा वैद्यकीय रेकॉर्ड क्रमांक (MRN).",
            "input_guidance": "रुग्ण ओळखपत्रावर छापलेला ६ ते १२ अंकी एमआरएन कोड लिहा.",
            "why": "रुग्णालयाच्या डेटाबेसमधून मागील वैद्यकीय नोंदी मिळवण्यासाठी आवश्यक.",
            "formats": "अक्षरे आणि संख्या.",
            "example": "MRN-554422",
            "mistakes": "खाट क्रमांकाशी गोंधळ करणे किंवा चुकीचा कोड टाकणे.",
            "validation": "अधिकृत एमआरएन स्वरूपाशी जुळणारे असावे."
        }
    },
    "insurance_provider": {
        "name": "Insurance Provider",
        "aliases": ["insurance provider", "insurance company", "carrier", "health insurance provider", "insurer", "tpa name"],
        "en": {
            "what": "The corporate company providing your medical insurance.",
            "input_guidance": "Enter the name of your health insurance company.",
            "why": "Required to settle hospital bills directly via cashless treatment claims.",
            "formats": "Company text name.",
            "example": "STAR HEALTH INSURANCE",
            "mistakes": "Writing policy agent name instead of the insurance company name.",
            "validation": "Must represent a valid corporate insurance company."
        },
        "hi": {
            "what": "आपके चिकित्सा बीमा प्रदान करने वाली कॉर्पोरेट कंपनी।",
            "input_guidance": "अपनी स्वास्थ्य बीमा कंपनी का नाम दर्ज करें।",
            "why": "कैशलेस उपचार दावों के माध्यम से सीधे अस्पताल के बिलों का निपटान करने के लिए आवश्यक।",
            "formats": "कंपनी का नाम पाठ।",
            "example": "STAR HEALTH INSURANCE",
            "mistakes": "बीमा कंपनी के नाम के बजाय बीमा एजेंट का नाम लिखना।",
            "validation": "एक वैध बीमा कंपनी का प्रतिनिधित्व होना चाहिए।"
        },
        "mr": {
            "what": "आरोग्य विमा देणारी कंपनी (Insurance Provider).",
            "input_guidance": "विма पॉलिसी देणाऱ्या अधिकृत विमा कंपनीचे नाव लिहा.",
            "why": "रुग्णालयाच्या बिलिंग प्रक्रियेत थेट दाव्यांचे सेटलमेंट करण्यासाठी आवश्यक.",
            "formats": "कंपनीचे नाव.",
            "example": "STAR HEALTH INSURANCE",
            "mistakes": "विमा एजंटचे नाव विमा कंपनी म्हणून लिहिणे.",
            "validation": "अधिकृत विमा कंपनीचे नाव असावे."
        }
    },
    "insurance_number": {
        "name": "Insurance Number",
        "aliases": ["insurance number", "insurance policy number", "policy number", "member id", "insurance id", "policy no", "health insurance id"],
        "en": {
            "what": "Your unique medical insurance policy number.",
            "input_guidance": "Enter the policy or health card number exactly as printed on your insurance card.",
            "why": "Used to query insurance portals for coverage confirmations and cashless approvals.",
            "formats": "Alphanumeric identity code.",
            "example": "POL-12345678",
            "mistakes": "Entering the card serial number instead of the policy number.",
            "validation": "Must match valid alphanumeric policy structures."
        },
        "hi": {
            "what": "आपका अद्वितीय चिकित्सा बीमा पॉलिसी नंबर।",
            "input_guidance": "बीमा कार्ड पर मुद्रित पॉलिसी या स्वास्थ्य कार्ड नंबर बिल्कुल वैसे ही दर्ज करें।",
            "why": "कवरेज पुष्टि और कैशलेस अनुमोदन के लिए बीमा पोर्टल पर पूछताछ करने के लिए उपयोग किया जाता है।",
            "formats": "अल्फ़ान्यूमेरिक पहचान कोड।",
            "example": "POL-12345678",
            "mistakes": "पॉलिसी नंबर के बजाय कार्ड सीरियल नंबर दर्ज करना।",
            "validation": "वैध अल्फ़ान्यूमेरिक पॉलिसी संरचनाओं से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "आरोग्य विमा पॉलिसीचा क्रमांक.",
            "input_guidance": "विमा ओळखपत्रावर छापलेला पॉलिसी किंवा मेंबर आयडी क्रमांक लिहा.",
            "why": "विमा कंपन्यांकडे थेट बिलांना मंजुरी मिळवण्यासाठी आवश्यक.",
            "formats": "विमा पॉलिसी क्रमांक.",
            "example": "POL-12345678",
            "mistakes": "कार्डवरील इतर क्रमांक पॉलिसी क्रमांक समजून लिहिणे.",
            "validation": "अधिकृत पॉलिसी क्रमांकाशी जुळले पाहिजे."
        }
    },
    "allergies": {
        "name": "Allergies",
        "aliases": ["allergies", "allergy", "known allergies", "drug allergies", "medical allergy"],
        "en": {
            "what": "Your medical allergies or adverse drug reactions.",
            "input_guidance": "Enter all known medical, food, or chemical allergies. Write 'NIL' or 'NONE' if you have none.",
            "why": "Extremely critical to prevent administration of unsafe medicines during hospital care.",
            "formats": "Text details.",
            "example": "PENICILLIN, PEANUTS or NONE",
            "mistakes": "Leaving it blank when you actually have known drug reactions.",
            "validation": "Must describe either the specific allergens or explicitly mention NONE."
        },
        "hi": {
            "what": "आपकी चिकित्सा एलर्जी या प्रतिकूल दवा प्रतिक्रियाएं।",
            "input_guidance": "सभी ज्ञात चिकित्सा, भोजन या रासायनिक एलर्जी दर्ज करें। यदि कोई नहीं है तो 'NIL' या 'NONE' लिखें।",
            "why": "अस्पताल में देखभाल के दौरान असुरक्षित दवाओं के प्रशासन को रोकने के लिए अत्यंत महत्वपूर्ण।",
            "formats": "पाठ विवरण।",
            "example": "PENICILLIN, PEANUTS or NONE",
            "mistakes": "ज्ञात दवा प्रतिक्रियाएं होने पर भी इसे खाली छोड़ना।",
            "validation": "या तो विशिष्ट एलर्जी का वर्णन होना चाहिए या स्पष्ट रूप से NONE का उल्लेख होना चाहिए।"
        },
        "mr": {
            "what": "रुग्णाला असलेली औषधे, अन्न किंवा इतर घटकांची ऍलर्जी.",
            "input_guidance": "तुम्हाला माहित असलेल्या सर्व ऍलर्जींची माहिती लिहा. ऍलर्जी नसल्यास 'NIL' किंवा 'NONE' लिहा.",
            "why": "उपचारादरम्यान अयोग्य औषधोपचार टाळण्यासाठी अत्यंत आवश्यक माहिती.",
            "formats": "ऍलर्जी तपशील.",
            "example": "PENICILLIN, PEANUTS or NONE",
            "mistakes": "ऍलर्जी असतानाही रकाना कोरा सोडणे.",
            "validation": "ऍलर्जीचे नाव लिहावे किंवा स्पष्टपणे 'NONE' लिहावे."
        }
    },
    "current_medications": {
        "name": "Current Medications",
        "aliases": ["current medications", "medications", "meds", "current treatment", "prescribed drugs", "ongoing medications"],
        "en": {
            "what": "All prescription or over-the-counter drugs you currently take.",
            "input_guidance": "List the names of all medicines you are taking regularly. Write 'NONE' if not applicable.",
            "why": "Needed to prevent dangerous drug-to-drug interactions during new treatment setups.",
            "formats": "Medicine names list.",
            "example": "METFORMIN 500MG ONCE DAILY or NONE",
            "mistakes": "Omitting daily pills or diabetic drugs, leading to medical errors.",
            "validation": "Should list drug names or explicitly state NONE."
        },
        "hi": {
            "what": "सभी नुस्खे या ओवर-द-काउंटर दवाएं जो आप वर्तमान में लेते हैं।",
            "input_guidance": "उन सभी दवाओं के नाम सूचीबद्ध करें जिन्हें आप नियमित रूप से ले रहे हैं। यदि लागू न हो तो 'NONE' लिखें।",
            "why": "नए उपचार सेटअप के दौरान खतरनाक दवा-से-दवा परस्पर क्रिया को रोकने के लिए आवश्यक।",
            "formats": "दवाओं के नाम की सूची।",
            "example": "METFORMIN 500MG ONCE DAILY or NONE",
            "mistakes": "दैनिक गोलियों या मधुमेह की दवाओं को छोड़ना, जिससे चिकित्सीय त्रुटियाँ हो सकती हैं।",
            "validation": "दवा के नामों को सूचीबद्ध करना चाहिए या स्पष्ट रूप से NONE लिखना चाहिए।"
        },
        "mr": {
            "what": "रुग्ण सध्या घेत असलेली इतर आजारांवरील नियमित औषधे.",
            "input_guidance": "सध्या चालू असलेल्या सर्व औषधांची नावे लिहा. औषधे चालू नसल्यास 'NONE' लिहा.",
            "why": "नवीन औषधोपचार सुरू करताना औषधांचे दुष्परिणाम किंवा रासायनिक संकर टाळण्यासाठी आवश्यक.",
            "formats": "औषधांची नावे.",
            "example": "METFORMIN 500MG ONCE DAILY or NONE",
            "mistakes": "नियमित गोळ्यांचे नाव लिहायला विसरणे.",
            "validation": "औषध नावे किंवा स्पष्टपणे 'NONE' लिहावे."
        }
    },
    "emergency_contact": {
        "name": "Emergency Contact",
        "aliases": ["emergency contact", "emergency contact name", "emergency name", "contact person in emergency", "emergency contact no", "emergency contact phone"],
        "en": {
            "what": "The contact details of your emergency representative.",
            "input_guidance": "Enter the name and phone number of a close family member or friend to contact in emergency.",
            "why": "Required to seek clinical consent or notify relatives during medical crises.",
            "formats": "Name and phone number string.",
            "example": "RAMESH SHARMA (+91 9876543210)",
            "mistakes": "Entering your own name or phone number as emergency contact.",
            "validation": "Must contain a valid name and phone number different from the applicant."
        },
        "hi": {
            "what": "आपके आपातकालीन प्रतिनिधि का संपर्क विवरण।",
            "input_guidance": "आपातकाल में संपर्क करने के लिए किसी करीबी परिवार के सदस्य या मित्र का नाम और फोन नंबर दर्ज करें।",
            "why": "चिकित्सीय संकट के दौरान नैदानिक सहमति लेने या रिश्तेदारों को सूचित करने के लिए आवश्यक।",
            "formats": "नाम और फोन नंबर स्ट्रिंग।",
            "example": "RAMESH SHARMA (+91 9876543210)",
            "mistakes": "आपातकालीन संपर्क के रूप में अपना नाम या फोन नंबर दर्ज करना।",
            "validation": "आवेदक से भिन्न एक वैध नाम और फोन नंबर होना चाहिए।"
        },
        "mr": {
            "what": "आणीबाणीच्या प्रसंगी संपर्क साधायच्या जवळच्या नातेवाईकाचा किंवा मित्राचा तपशील.",
            "input_guidance": "आणीबाणीच्या प्रसंगी संपर्क साधण्यासाठी जवळच्या व्यक्तीचे नाव आणि मोबाईल नंबर लिहा.",
            "why": "वैद्यकीय आणीबाणीच्या वेळी संमती घेण्यासाठी किंवा कुटुंबीयांना संपर्क साधण्यासाठी आवश्यक.",
            "formats": "नाव आणि मोबाईल नंबर.",
            "example": "RAMESH SHARMA (+91 9876543210)",
            "mistakes": "स्वतःचाच मोबाईल क्रमांक आणीबाणीच्या संपर्कासाठी देणे.",
            "validation": "अर्जदारापेक्षा वेगळ्या व्यक्तीचे नाव आणि नंबर असावा."
        }
    },

    # GOVERNMENT / KYC
    "aadhaar": {
        "name": "Aadhaar Number",
        "aliases": ["aadhaar number", "aadhaar no", "aadhaar card", "aadhar card", "aadhar no", "aadhar number", "aadhar", "आधार क्रमांक", "आधार"],
        "en": {
            "what": "Your unique 12-digit biometric identity card number issued by UIDAI.",
            "input_guidance": "Enter your 12-digit Aadhaar number carefully. Avoid spaces or hyphens.",
            "why": "Serves as primary identity validation, address verification, and subsidy benefits tracking.",
            "formats": "12-digit numeric code.",
            "example": "1234 5678 9012",
            "mistakes": "Typing wrong numbers or failing Verhoeff checksum digit check.",
            "validation": "Must pass UIDAI Aadhaar Verhoeff checksum algorithm check."
        },
        "hi": {
            "what": "यूआईडीएआई द्वारा जारी आपका 12-अंकीय विशिष्ट बायोमेट्रिक पहचान पत्र संख्या।",
            "input_guidance": "अपना 12-अंकीय आधार नंबर ध्यान से दर्ज करें। स्पेस या हाइफ़न से बचें।",
            "why": "प्राथमिक पहचान सत्यापन, पता सत्यापन और सब्सिडी लाभ ट्रैकिंग के रूप में कार्य करता है।",
            "formats": "12-अंकीय संख्यात्मक कोड।",
            "example": "1234 5678 9012",
            "mistakes": "गलत नंबर टाइप करना या वेरहॉफ़ चेकसम डिजिट जांच में विफल होना।",
            "validation": "यूआईडीएआई आधार वेरहॉफ़ चेकसम एल्गोरिथम जांच को पास करना चाहिए।"
        },
        "mr": {
            "what": "UIDAI द्वारे जारी केलेला तुमचा १२-अंकीय अद्वितीय आधार क्रमांक.",
            "input_guidance": "आधार कार्डवरील १२-अंकीय क्रमांक काळजीपूर्वक लिहा. स्पेस देणे टाळा.",
            "why": "अधिकृत ओळख पडताळणी, थेट शासकीय लाभ आणि पत्याच्या पुराव्यासाठी आवश्यक.",
            "formats": "१२-अंकीय आधार क्रमांक.",
            "example": "1234 5678 9012",
            "mistakes": "चुकीचे अंक लिहिणे किंवा वेरहॉफ चेकसम पडताळणीत अयशस्वी होणे.",
            "validation": "वेरहॉफ चेकसम अल्गोरिदमनुसार वैध आधार क्रमांक असावा."
        }
    },
    "pan": {
        "name": "PAN Number",
        "aliases": ["pan number", "pan no", "pan card", "pan", "पॅन क्रमांक", "पॅन"],
        "en": {
            "what": "Your 10-digit alphanumeric Permanent Account Number issued by the Income Tax Department.",
            "input_guidance": "Enter your 10-digit PAN string. Write in capital letters only.",
            "why": "Required for tracking financial transactions, processing tax filings, and bank KYC confirmation.",
            "formats": "10-digit alphanumeric PAN card sequence.",
            "example": "ABCDE1234F",
            "mistakes": "Confusing character 'O' with digit '0' or typing small letters.",
            "validation": "Must match valid alphanumeric PAN structures (5 letters, 4 digits, 1 letter)."
        },
        "hi": {
            "what": "आयकर विभाग द्वारा जारी आपका 10-अंकीय अल्फ़ान्यूमेरिक स्थायी खाता संख्या (PAN)।",
            "input_guidance": "अपना 10-अंकीय पैन नंबर दर्ज करें। केवल बड़े अक्षरों में लिखें।",
            "why": "वित्तीय लेनदेन को ट्रैक करने, टैक्स फाइलिंग को संसाधित करने और बैंक केवाईसी की पुष्टि के लिए आवश्यक।",
            "formats": "10-अंकीय अल्फ़ान्यूमेरिक पैन कार्ड अनुक्रम।",
            "example": "ABCDE1234F",
            "mistakes": "वर्ण 'O' को अंक '0' के साथ भ्रमित करना या छोटे अक्षर लिखना।",
            "validation": "वैध अल्फ़ान्यूमेरिक पैन संरचनाओं से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "आयकर विभागाने जारी केलेला तुमचा १०-अंकीय पॅन कार्ड क्रमांक.",
            "input_guidance": "तुमचा १०-अंकीय पॅन क्रमांक लिहा. इंग्रजी मोठ्या अक्षरातच लिहा.",
            "why": "कर पडताळणी, वित्तीय व्यवहार आणि बँक केवायसीसाठी आवश्यक.",
            "formats": "१०-अंकीय पॅन स्वरूप.",
            "example": "ABCDE1234F",
            "mistakes": "इंग्रजी अक्षर 'O' आणि अंक '0' यांच्यात गफलत करणे.",
            "validation": "१०-अंकीय अधिकृत पॅन कार्ड संरचनेशी जुळले पाहिजे."
        }
    },
    "passport": {
        "name": "Passport Number",
        "aliases": ["passport number", "passport no", "passport", "पारपत्र"],
        "en": {
            "what": "Your official international travel identity document number.",
            "input_guidance": "Enter your 8-character passport number as printed on your passport book.",
            "why": "Needed for travel visa processes, border checks, and international identity validations.",
            "formats": "8-digit alphanumeric passport ID.",
            "example": "A1234567",
            "mistakes": "Entering expired passport numbers or typing invalid characters.",
            "validation": "Must be a valid unexpired passport number."
        },
        "hi": {
            "what": "आपका आधिकारिक अंतर्राष्ट्रीय यात्रा पहचान दस्तावेज नंबर।",
            "input_guidance": "अपनी पासपोर्ट पुस्तिका पर मुद्रित अपना 8-अंकीय पासपोर्ट नंबर दर्ज करें।",
            "why": "यात्रा वीज़ा प्रक्रियाओं, सीमा जाँच और अंतर्राष्ट्रीय पहचान सत्यापन के लिए आवश्यक।",
            "formats": "8-अंकीय अल्फ़ान्यूमेरिक पासपोर्ट आईडी।",
            "example": "A1234567",
            "mistakes": "समाप्त हो चुके पासपोर्ट नंबर दर्ज करना या अमान्य वर्ण टाइप करना।",
            "validation": "एक वैध और सक्रिय पासपोर्ट नंबर होना चाहिए।"
        },
        "mr": {
            "what": "तुमचा आंतरराष्ट्रीय प्रवास दस्तऐवज (पासपोर्ट) क्रमांक.",
            "input_guidance": "पासपोर्टवर छापलेला ८-अंकीय क्रमांक अचूक लिहा.",
            "why": "परदेशी प्रवासासाठी व्हिसा पडताळणी आणि आंतरराष्ट्रीय ओळखीसाठी आवश्यक.",
            "formats": "८-अंकीय पासपोर्ट स्वरूप.",
            "example": "A1234567",
            "mistakes": "मुदत संपलेला किंवा चुकीचा पासपोर्ट नंबर लिहिणे.",
            "validation": "सध्या वैध असलेला पासपोर्ट क्रमांक असावा."
        }
    },
    "driving_license": {
        "name": "Driving License Number",
        "aliases": ["driving license number", "driving license no", "dl number", "dl no", "license number", "driving licence"],
        "en": {
            "what": "Your official vehicle operating license number.",
            "input_guidance": "Enter your 15-character driving license number as shown on your DL card.",
            "why": "Used to verify your authorization to drive and serves as secondary identity/address proof.",
            "formats": "Standard DL alphanumeric string.",
            "example": "MH12 20240101234",
            "mistakes": "Omitting spaces or state code prefixes.",
            "validation": "Must match DL database records."
        },
        "hi": {
            "what": "आपका आधिकारिक वाहन संचालन लाइसेंस नंबर।",
            "input_guidance": "अपने डीएल कार्ड पर दिखाए अनुसार अपना 15-अंकीय ड्राइविंग लाइसेंस नंबर दर्ज करें।",
            "why": "वाहन चलाने के आपके अधिकार को सत्यापित करने के लिए उपयोग किया जाता है और द्वितीयक पहचान/पते के प्रमाण के रूप में कार्य करता है।",
            "formats": "मानक डीएल अल्फ़ान्यूमेरिक स्ट्रिंग।",
            "example": "MH12 20240101234",
            "mistakes": "स्पेस या राज्य कोड उपसर्गों को छोड़ना।",
            "validation": "ड्राइविंग लाइसेंस डेटाबेस रिकॉर्ड से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "तुमचा ड्रायव्हिंग लायसन्स क्रमांक.",
            "input_guidance": "लायसन्स कार्डवर छापलेला १५-अंकीय डीएल क्रमांक लिहा.",
            "why": "वाहन चालवण्याचा परवाना तपासण्यासाठी आणि ओळख पुरावा म्हणून आवश्यक.",
            "formats": "ड्रायव्हिंग लायसन्स स्वरूप.",
            "example": "MH12 20240101234",
            "mistakes": "राज्याचा कोड किंवा स्पेस लिहायला विसरणे.",
            "validation": "डीएल क्रमांकाच्या रचनेशी जुळणारे असावे."
        }
    },
    "voter_id": {
        "name": "Voter ID",
        "aliases": ["voter id", "voter card", "epic number", "epic no", "voter id card", "voter card no"],
        "en": {
            "what": "Your Election Commission electoral identity card number.",
            "input_guidance": "Enter the alphanumeric EPIC number printed on your Voter ID card.",
            "why": "Used to confirm citizenship, verify voting status, and serve as address proof.",
            "formats": "10-character alphanumeric EPIC format.",
            "example": "XYZ1234567",
            "mistakes": "Confusing characters like 'O' and '0'.",
            "validation": "Must represent a valid alphanumeric EPIC number."
        },
        "hi": {
            "what": "आपका चुनाव आयोग मतदाता पहचान पत्र नंबर।",
            "input_guidance": "अपने मतदाता पहचान पत्र पर मुद्रित अल्फ़ान्यूमेरिक ईपीआईसी नंबर दर्ज करें।",
            "why": "नागरिकता की पुष्टि करने, मतदान की स्थिति को सत्यापित करने और पते के प्रमाण के रूप में उपयोग करने के लिए।",
            "formats": "10-अंकीय अल्फ़ान्यूमेरिक ईपीआईसी प्रारूप।",
            "example": "XYZ1234567",
            "mistakes": "'O' और '0' जैसे वर्णों को भ्रमित करना।",
            "validation": "एक वैध अल्फ़ान्यूमेरिक ईपीआईसी नंबर का प्रतिनिधित्व होना चाहिए।"
        },
        "mr": {
            "what": "निवडणूक आयोगाने दिलेला मतदार ओळखपत्र क्रमांक.",
            "input_guidance": "मतदार कार्डवरील १०-अंकीय EPIC क्रमांक लिहा.",
            "why": "भारतीय नागरिकत्व आणि रहिवासी पुराव्याची पडताळणी करण्यासाठी आवश्यक.",
            "formats": "१०-अंकीय EPIC स्वरूप.",
            "example": "XYZ1234567",
            "mistakes": "अक्षरे लिहिताना गफलत करणे.",
            "validation": "वैध मतदार कार्ड क्रमांकाशी जुळले पाहिजे."
        }
    },

    # BANKING
    "bank_name": {
        "name": "Bank Name",
        "aliases": ["bank name", "bank", "name of bank", "bank_name"],
        "en": {
            "what": "The registered corporate bank entity name.",
            "input_guidance": "Enter the complete name of the bank where you hold the account.",
            "why": "Required to settle financial transfers and confirm financial routing.",
            "formats": "Bank name text.",
            "example": "STATE BANK OF INDIA",
            "mistakes": "Writing college or business name here instead of the banking group.",
            "validation": "Must be a valid recognized financial institution."
        },
        "hi": {
            "what": "पंजीकृत कॉर्पोरेट बैंक इकाई का नाम।",
            "input_guidance": "उस बैंक का पूरा नाम दर्ज करें जिसमें आपका खाता है।",
            "why": "वित्तीय स्थानान्तरण को निपटाने और वित्तीय मार्ग की पुष्टि करने के लिए आवश्यक।",
            "formats": "बैंक का नाम पाठ।",
            "example": "STATE BANK OF INDIA",
            "mistakes": "बैंकिंग समूह के बजाय यहाँ कॉलेज या व्यवसाय का नाम लिखना।",
            "validation": "एक वैध मान्यता प्राप्त वित्तीय संस्थान होना चाहिए।"
        },
        "mr": {
            "what": "तुमचे खाते असलेल्या बँकेचे नाव.",
            "input_guidance": "बँकेचे संपूर्ण नाव लिहा.",
            "why": "पैसे खात्यात जमा करण्यासाठी बँकेची नोंद ठेवणे आवश्यक.",
            "formats": "बँकेचे नाव.",
            "example": "STATE BANK OF INDIA",
            "mistakes": "बँकेच्या अधिकृत नावाऐवजी इतर संक्षिप्त नाव लिहिणे.",
            "validation": "मान्यताप्राप्त बँकेचे नाव असावे."
        }
    },
    "account_number": {
        "name": "Account Number",
        "aliases": ["account number", "account no", "bank a/c no", "bank account number", "bank account no", "bank account", "bank account number (savings/current)", "bank_a_c_no"],
        "en": {
            "what": "Your unique savings/current bank account identification number.",
            "input_guidance": "Enter your complete savings or current bank account number as printed on your passbook.",
            "why": "Used for transferring subsidy funds, credit settlements, or verification of holdings.",
            "formats": "9 to 18 digit account number.",
            "example": "123456789012",
            "mistakes": "Omitting digits, typing credit card numbers, or writing incorrect sequences.",
            "validation": "Must contain numeric values only."
        },
        "hi": {
            "what": "आपकी विशिष्ट बचत/चालू बैंक खाता पहचान संख्या।",
            "input_guidance": "पासबुक पर मुद्रित अपना पूरा बचत या चालू बैंक खाता संख्या दर्ज करें।",
            "why": "सब्सिडी फंड ट्रांसफर करने, क्रेडिट सेटलमेंट या होल्डिंग्स के सत्यापन के लिए उपयोग किया जाता है।",
            "formats": "9 से 18 अंकों का खाता नंबर।",
            "example": "123456789012",
            "mistakes": "अंक छोड़ना, क्रेडिट कार्ड नंबर टाइप करना, या गलत क्रम लिखना।",
            "validation": "केवल संख्यात्मक मान होने चाहिए।"
        },
        "mr": {
            "what": "तुमचा बचत किंवा चालू बँक खाते क्रमांक.",
            "input_guidance": "पासबुकवर असल्याप्रमाणे तुमचा संपूर्ण बँक खाते क्रमांक लिहा.",
            "why": "शासकीय रक्कम किंवा थेट पैसे खात्यात जमा करण्यासाठी आवश्यक.",
            "formats": "९ ते १८ अंकी बँक खाते क्रमांक.",
            "example": "123456789012",
            "mistakes": "अंक लिहायला विसरणे किंवा अंकांचे स्थान बदलणे.",
            "validation": "फक्त संख्या स्वरूपात असावर."
        }
    },
    "ifsc": {
        "name": "IFSC Code",
        "aliases": ["ifsc code", "ifsc", "ifsc/rtgs code", "ifsc_code", "bank ifsc"],
        "en": {
            "what": "The 11-character Indian Financial System Code identifying your branch.",
            "input_guidance": "Enter the 11-character alphanumeric code printed on your cheque leaf or passbook.",
            "why": "Needed to route electronic bank transfers (NEFT, IMPS, RTGS) directly to your branch.",
            "formats": "11-character bank branch IFSC format.",
            "example": "SBIN0001234",
            "mistakes": "Confusing 5th character (which is always zero) with capital letter 'O'.",
            "validation": "Must be exactly 11 characters, fifth character must be zero '0'."
        },
        "hi": {
            "what": "आपके शाखा की पहचान करने वाला 11-अंकीय भारतीय वित्तीय प्रणाली कोड (IFSC)।",
            "input_guidance": "अपने चेक लीफ या पासबुक पर मुद्रित 11-अंकीय अल्फ़ान्यूमेरिक कोड दर्ज करें।",
            "why": "इलेक्ट्रॉनिक बैंक ट्रांसफर को सीधे आपकी शाखा में भेजने के लिए आवश्यक।",
            "formats": "11-अंकीय बैंक शाखा आईएफएससी प्रारूप।",
            "example": "SBIN0001234",
            "mistakes": "5वें वर्ण को बड़े अक्षर 'O' के साथ भ्रमित करना।",
            "validation": "ठीक 11 वर्ण होने चाहिए, 5वां वर्ण शून्य '0' होना चाहिए।"
        },
        "mr": {
            "what": "बँक शाखेचा ११-अंकीय भारतीय वित्तीय प्रणाली कोड (IFSC).",
            "input_guidance": "पासबुकवर किंवा चेकबुकवर छापलेला ११-अंकीय अल्फान्यूमेरिक कोड लिहा.",
            "why": "इलेक्ट्रॉनिक बँक ट्रान्सफर थेट तुमच्या शाखेत पाठवण्यासाठी आवश्यक.",
            "formats": "११-अंकीय आयएफएससी स्वरूप.",
            "example": "SBIN0001234",
            "mistakes": "पाचव्या स्थानावरील शून्य ला इंग्रजी अक्षर 'O' समजणे.",
            "validation": "अचूक ११ अक्षरे असावीत, पाचवे अक्षर शून्य असणे बंधनकारक."
        }
    },
    "branch_name": {
        "name": "Branch Name",
        "aliases": ["branch name", "branch", "bank branch", "branch address", "name of branch"],
        "en": {
            "what": "The specific branch location of your bank.",
            "input_guidance": "Enter the name of your bank's branch (e.g. Nagpur Main Branch).",
            "why": "Helps double check payment routing details and resolve database errors.",
            "formats": "Branch location text.",
            "example": "NAGPUR MAIN BRANCH",
            "mistakes": "Writing the main bank headquarters name instead of the local branch.",
            "validation": "Should match branch records."
        },
        "hi": {
            "what": "आपके बैंक का विशिष्ट शाखा स्थान।",
            "input_guidance": "अपने बैंक की शाखा का नाम दर्ज करें (जैसे नागपुर मुख्य शाखा)।",
            "why": "भुगतान मार्ग विवरण की दोबारा जांच करने और डेटाबेस त्रुटियों को हल करने में मदद करता है।",
            "formats": "शाखा स्थान पाठ।",
            "example": "NAGPUR MAIN BRANCH",
            "mistakes": "स्थानीय शाखा के बजाय मुख्य बैंक मुख्यालय का नाम लिखना।",
            "validation": "शाखा रिकॉर्ड से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "तुमच्या बँक शाखेचे नाव.",
            "input_guidance": "शाखेचे ठिकाण लिहा (उदा. नागपूर मुख्य शाखा).",
            "why": "बँक खात्याची पडताळणी करण्यासाठी आवश्यक जोड माहिती.",
            "formats": "शाखेचे नाव.",
            "example": "NAGPUR MAIN BRANCH",
            "mistakes": "बँकेच्या मुख्य कार्यालयाचे नाव लिहिणे.",
            "validation": "शाखेचे नाव योग्य असावे."
        }
    },

    # DOCUMENTS
    "signature": {
        "name": "Signature",
        "aliases": ["signature", "applicant signature", "sign here", "signature of applicant", "signature of candidate", "sign", "signature specimen"],
        "en": {
            "what": "Your handwritten signature or digital consent indicator.",
            "input_guidance": "Sign clearly inside the designated boundary box using black or blue ink.",
            "why": "Acts as legally binding validation and confirmation of declarations in the form.",
            "formats": "Handwritten signature or digital authorization mark.",
            "example": "[Handwritten signature inside the box]",
            "mistakes": "Signing outside the designated box boundary or scribbling illegibly.",
            "validation": "Must be contained within the signature box boundaries."
        },
        "hi": {
            "what": "आपका हस्तलिखित हस्ताक्षर या डिजिटल सहमति सूचक।",
            "input_guidance": "काली या नीली स्याही का उपयोग करके निर्धारित सीमा बॉक्स के अंदर स्पष्ट रूप से हस्ताक्षर करें।",
            "why": "फॉर्म में घोषणाओं के कानूनी रूप से बाध्यकारी सत्यापन और पुष्टि के रूप में कार्य करता है।",
            "formats": "हस्तलिखित हस्ताक्षर या डिजिटल प्राधिकरण चिह्न।",
            "example": "[निर्धारित बॉक्स के अंदर हस्तलिखित हस्ताक्षर]",
            "mistakes": "निर्धारित बॉक्स सीमा के बाहर हस्ताक्षर करना या अस्पष्ट रूप से लिखना।",
            "validation": "हस्ताक्षर बॉक्स की सीमाओं के भीतर होना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराची स्वाक्षरी किंवा डिजिटल खूण.",
            "input_guidance": "दिलेल्या चौकटीच्या आत काळ्या किंवा निळ्या शाईने स्पष्ट स्वाक्षरी करा.",
            "why": "अर्जातील घोषणापत्राला कायदेशीर मान्यता आणि मान्यता देण्यासाठी आवश्यक.",
            "formats": "हस्तलिखित स्वाक्षरी.",
            "example": "[चौकटीच्या आत केलेली सही]",
            "mistakes": "चौकटीबाहेर सही करणे किंवा अस्पष्ट रेघोट्या मारणे.",
            "validation": "स्वाक्षरी दिलेल्या चौकटीच्या मर्यादेतच असावी."
        }
    },
    "photograph": {
        "name": "Photograph",
        "aliases": ["photograph", "photo", "passport size photo", "passport size photograph", "candidate photograph"],
        "en": {
            "what": "Your recent passport size colored photograph.",
            "input_guidance": "Affix or upload your recent colored photo with a clear light background.",
            "why": "Used for face verification and printing on official badges/certificates.",
            "formats": "Recent passport size image.",
            "example": "[Upload colored passport photo file]",
            "mistakes": "Uploading selfies, casual photos, or using dark sunglasses.",
            "validation": "Must be clear and fit within the designated photo dimensions."
        },
        "hi": {
            "what": "आपकी हालिया पासपोर्ट आकार की रंगीन तस्वीर।",
            "input_guidance": "स्पष्ट हल्के पृष्ठभूमि वाली अपनी हालिया रंगीन फोटो चिपकाएं या अपलोड करें।",
            "why": "चेहरा सत्यापन और आधिकारिक बैज/प्रमाण पत्रों पर छपाई के लिए उपयोग किया जाता है।",
            "formats": "हालिया पासपोर्ट आकार की छवि।",
            "example": "[रंगीन पासपोर्ट फोटो फाइल अपलोड करें]",
            "mistakes": "सेल्फी, आकस्मिक तस्वीरें अपलोड करना, या गहरे धूप का चश्मा पहनना।",
            "validation": "स्पष्ट होना चाहिए और निर्दिष्ट फोटो आयामों के भीतर फिट होना चाहिए।"
        },
        "mr": {
            "what": "अर्जदाराचे अलीकडील रंगीत पासपोर्ट आकाराचे छायाचित्र.",
            "input_guidance": "फिकट पांढऱ्या पार्श्वभूमीवर काढलेला अलीकडील फोटो लावा किंवा अपलोड करा.",
            "why": "चेहरा पडताळणी आणि ओळखपत्रावर फोटो छापण्यासाठी आवश्यक.",
            "formats": "पासपोर्ट आकाराचा फोटो.",
            "example": "[पासपोर्ट फोटो फाईल अपलोड करा]",
            "mistakes": "सेल्फी किंवा चष्मा घातलेला अनधिकृत फोटो वापरणे.",
            "validation": "फोटो स्पष्ट असावा आणि दिलेल्या जागेत बसणारा असावा."
        }
    },
    "upload_document": {
        "name": "Upload Document",
        "aliases": ["upload document", "upload", "attach document", "upload file", "document upload"],
        "en": {
            "what": "An option to upload a supporting file/document.",
            "input_guidance": "Upload clear scanned copy of the requested document in PDF or JPEG format.",
            "why": "Acts as official validation proof for details typed in the form.",
            "formats": "PDF, JPEG, or PNG formats.",
            "example": "[Upload self-attested document scan]",
            "mistakes": "Uploading blurred files, password-locked PDFs, or wrong files.",
            "validation": "File size must be within limit (e.g. < 2MB) and legible."
        },
        "hi": {
            "what": "एक सहायक फ़ाइल/दस्तावेज़ अपलोड करने का विकल्प।",
            "input_guidance": "अनुरोधित दस्तावेज़ की स्पष्ट स्कैन की गई प्रति पीडीएफ या जेपीईजी प्रारूप में अपलोड करें।",
            "why": "फॉर्म में टाइप किए गए विवरण के लिए आधिकारिक सत्यापन प्रमाण के रूप में कार्य करता है।",
            "formats": "पीडीएफ, जेपीईजी, या पीएनजी प्रारूप।",
            "example": "[स्व-सत्यापित दस्तावेज़ स्कैन अपलोड करें]",
            "mistakes": "धंधली फाइलें, पासवर्ड-लॉक किए गए पीडीएफ, या गलत फाइलें अपलोड करना।",
            "validation": "फ़ाइल का आकार सीमा के भीतर होना चाहिए और सुपाठ्य होना चाहिए।"
        },
        "mr": {
            "what": "आवश्यक कागदपत्रे अपलोड करण्याचा पर्याय.",
            "input_guidance": "मागितलेल्या कागदपत्राची स्पष्ट स्कॅन केलेली प्रत PDF किंवा JPEG स्वरूपात अपलोड करा.",
            "why": "अर्जात भरलेल्या माहितीच्या अधिकृत पडताळणीसाठी आवश्यक पुरावा.",
            "formats": "PDF, JPEG किंवा PNG फाईल.",
            "example": "[स्वाक्षरी केलेले कागदपत्र अपलोड करा]",
            "mistakes": "अस्पष्ट, पासवर्ड लॉक असलेली किंवा चुकीची फाईल अपलोड करणे.",
            "validation": "फाईल साईझ मर्यादित असावी आणि वाचता येण्याजोगी असावी."
        }
    },
    "id_proof_type": {
        "name": "ID Proof Type",
        "aliases": ["id proof type", "identity proof type", "id type", "type of id", "type of id proof"],
        "en": {
            "what": "The selected category of government identity card.",
            "input_guidance": "Select the government ID card you will upload (e.g., Aadhaar Card, PAN Card, Passport).",
            "why": "Used to index which ID card is processed for verification checks.",
            "formats": "Aadhaar Card, PAN Card, Passport, Voter ID, Driving License.",
            "example": "AADHAAR CARD",
            "mistakes": "Selecting one ID type but uploading a different card.",
            "validation": "Must be a valid recognized identity proof option."
        },
        "hi": {
            "what": "सरकारी पहचान पत्र की चयनित श्रेणी।",
            "input_guidance": "उस सरकारी आईडी कार्ड का चयन करें जिसे आप अपलोड करेंगे (जैसे, आधार कार्ड, पैन कार्ड, पासपोर्ट)।",
            "why": "यह अनुक्रमित करने के लिए उपयोग किया जाता है कि सत्यापन जांच के लिए किस आईडी कार्ड को संसाधित किया गया है।",
            "formats": "आधार कार्ड, पैन कार्ड, पासपोर्ट, वोटर आईडी, ड्राइविंग लाइसेंस।",
            "example": "AADHAAR CARD",
            "mistakes": "एक आईडी प्रकार का चयन करना लेकिन एक अलग कार्ड अपलोड करना।",
            "validation": "एक वैध मान्यता प्राप्त पहचान प्रमाण विकल्प होना चाहिए।"
        },
        "mr": {
            "what": "ओळख पुराव्यासाठी वापरलेला ओळखपत्राचा प्रकार.",
            "input_guidance": "तुम्ही ओळख पडताळणीसाठी वापरत असलेल्या अधिकृत ओळखपत्राचा प्रकार निवडा.",
            "why": "ओळख पडताळणी प्रक्रियेत दस्तऐवजाचे वर्गीकरण करण्यासाठी आवश्यक.",
            "formats": "आधार कार्ड, पॅन कार्ड, पासपोर्ट, मतदार ओळखपत्र, ड्रायव्हिंग लायसन्स.",
            "example": "AADHAAR CARD",
            "mistakes": "निवडलेला ओळखपत्र प्रकार आणि अपलोड केलेले ओळखपत्र वेगळे असणे.",
            "validation": "मान्य ओळखपत्रांच्या यादीतील पर्याय निवडावा."
        }
    },
    "id_proof_number": {
        "name": "ID Proof Number",
        "aliases": ["id proof number", "identity proof number", "id number", "id proof no", "identity card no"],
        "en": {
            "what": "The identification code printed on your selected ID card.",
            "input_guidance": "Enter the alphanumeric number of the selected identity card carefully.",
            "why": "Used to query government databases to confirm profile legitimacy.",
            "formats": "Alphanumeric identity code.",
            "example": "1234 5678 9012 or ABCDE1234F",
            "mistakes": "Entering wrong digits or confusing characters.",
            "validation": "Must match the valid numbering format of the selected ID type."
        },
        "hi": {
            "what": "आपके चयनित आईडी कार्ड पर मुद्रित पहचान कोड।",
            "input_guidance": "चयनित पहचान पत्र का अल्फ़ान्यूमेरिक नंबर ध्यान से दर्ज करें।",
            "why": "प्रोफ़ाइल की वैधता की पुष्टि करने के लिए सरकारी डेटाबेस से पूछताछ करने के लिए उपयोग किया जाता है।",
            "formats": "अल्फ़ान्यूमेरिक पहचान कोड।",
            "example": "1234 5678 9012 or ABCDE1234F",
            "mistakes": "गलत अंक दर्ज करना या अक्षरों को भ्रमित करना।",
            "validation": "चयनित आईडी प्रकार के वैध नंबरिंग प्रारूप से मेल खाना चाहिए।"
        },
        "mr": {
            "what": "निवडलेल्या ओळखपत्राचा क्रमांक.",
            "input_guidance": "निवडलेल्या ओळखपत्रावरील अधिकृत ओळख क्रमांक लिहा.",
            "why": "सरकारी नोंदी आणि ओळखपत्राची सत्यता तपासण्यासाठी आवश्यक.",
            "formats": "अक्षरे आणि संख्या.",
            "example": "1234 5678 9012 or ABCDE1234F",
            "mistakes": "ओळखपत्र क्रमांक चुकीचा लिहिणे.",
            "validation": "निवडलेल्या ओळखपत्राच्या अधिकृत क्रमांकाशी जुळले पाहिजे."
        }
    }
}

EXCLUSION_WORDS = ["scholarship", "hostel", "pension", "farmer", "pf", "room", "cultivator"]

SYNONYM_DICT = {
    "registration_number": [
        "application number", "application no", "registration number", "registration no",
        "enrollment number", "enrollment no", "enrolment number", "enrolment no",
        "form number", "reference number"
    ],
    "email": [
        "email", "email id", "e-mail", "mail id", "email address", "email_id"
    ],
    "phone_number": [
        "phone number", "phone no", "mobile number", "mobile no", "contact number",
        "contact no", "telephone no", "telephone number", "cell number", "mobile"
    ],
    "aadhaar": [
        "aadhaar", "aadhaar card", "aadhaar number", "aadhar", "aadhar card", "aadhar number",
        "aadhaar no", "aadhar no"
    ],
    "pan": [
        "pan", "pan card", "pan number", "pan no"
    ]
}

APP_NUM_SYNONYMS = set(SYNONYM_DICT["registration_number"])
EMAIL_SYNONYMS = set(SYNONYM_DICT["email"])
PHONE_SYNONYMS = set(SYNONYM_DICT["phone_number"])
AADHAAR_SYNONYMS = set(SYNONYM_DICT["aadhaar"])
PAN_SYNONYMS = set(SYNONYM_DICT["pan"])

def is_forbidden_mapping(label_clean, template_key):
    # Check if label represents Application Number
    if any(s in label_clean for s in APP_NUM_SYNONYMS) or "application" in label_clean or "enrollment" in label_clean:
        if template_key in ["full_name", "first_name", "last_name", "fathers_name", "mothers_name", "guardian_name"]:
            return True
    # Check if label represents Email
    if any(s in label_clean for s in EMAIL_SYNONYMS):
        if template_key in ["address", "alternate_number", "phone_number"]:
            return True
    # Check if label represents Aadhaar
    if any(s in label_clean for s in AADHAAR_SYNONYMS):
        if template_key in ["phone_number", "alternate_number"]:
            return True
    # Check if label represents PAN
    if any(s in label_clean for s in PAN_SYNONYMS):
        if template_key == "aadhaar":
            return True
    return False

def match_field_to_template(label, section_title=None, form_category=None):
    if not label:
        return None, 0.0
        
    # Standard clean up
    label_clean = re.sub(r'[\s\:\-\?\(\)]+', ' ', label).strip().lower()
    
    def log_match_attempt(best_template, best_score):
        try:
            import os
            import json
            log_path = os.path.join(os.path.dirname(__file__), 'unknown_fields.log')
            log_entry = {
                "field_label": label,
                "matched_template": best_template if best_template else "N/A",
                "confidence_score": f"{int(best_score * 100)}%"
            }
            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(log_entry) + "\n")
        except Exception as log_err:
            pass

    # A. Exact Label Match
    for key, info in TEMPLATES.items():
        name_clean = info["name"].lower()
        aliases_clean = [a.lower() for a in info.get("aliases", [])]
        if label_clean == name_clean or label_clean in aliases_clean:
            if not is_forbidden_mapping(label_clean, key):
                best_template, best_score = key, 1.0
                if any(ew in label_clean for ew in EXCLUSION_WORDS):
                    best_score = 0.65
                log_match_attempt(best_template, best_score)
                return best_template, best_score
                
    # B. Synonym Match
    # Exact synonym match first
    for key, synonyms in SYNONYM_DICT.items():
        if label_clean in synonyms:
            if not is_forbidden_mapping(label_clean, key):
                best_template, best_score = key, 1.0
                if any(ew in label_clean for ew in EXCLUSION_WORDS):
                    best_score = 0.65
                log_match_attempt(best_template, best_score)
                return best_template, best_score
                
    # Substring word boundary synonym match
    for key, synonyms in SYNONYM_DICT.items():
        for syn in synonyms:
            if re.search(r'\b' + re.escape(syn) + r'\b', label_clean):
                if not is_forbidden_mapping(label_clean, key):
                    best_template, best_score = key, 1.0
                    if any(ew in label_clean for ew in EXCLUSION_WORDS):
                        best_score = 0.65
                    log_match_attempt(best_template, best_score)
                    return best_template, best_score

    # C. Section Context Match
    SECTION_KEYWORDS = {
        "identity": ["full_name", "first_name", "last_name", "fathers_name", "mothers_name", "guardian_name", "gender", "marital_status", "nationality", "signature", "photograph", "aadhaar", "pan", "passport", "driving_license", "voter_id"],
        "personal": ["dob", "age", "blood_group", "occupation", "annual_income", "category", "religion"],
        "contact": ["phone_number", "alternate_number", "email", "address", "city", "state", "district", "country", "pin_code", "emergency_contact"],
        "academic": ["school_name", "college_name", "university", "degree", "course", "percentage", "cgpa", "passing_year", "roll_number", "registration_number"],
        "education": ["school_name", "college_name", "university", "degree", "course", "percentage", "cgpa", "passing_year", "roll_number", "registration_number"],
        "employment": ["employee_id", "designation", "department", "company_name", "experience", "salary"],
        "work": ["employee_id", "designation", "department", "company_name", "experience", "salary"],
        "health": ["mrn_number", "insurance_provider", "insurance_number", "allergies", "current_medications"],
        "medical": ["mrn_number", "insurance_provider", "insurance_number", "allergies", "current_medications"],
        "banking": ["bank_name", "account_number", "ifsc", "branch_name"],
        "finance": ["bank_name", "account_number", "ifsc", "branch_name", "annual_income", "salary"],
        "kyc": ["aadhaar", "pan", "passport", "driving_license", "voter_id", "id_proof_type", "id_proof_number"]
    }
    if section_title:
        sect_clean = section_title.lower()
        preferred_keys = []
        for sect_key, t_keys in SECTION_KEYWORDS.items():
            if sect_key in sect_clean:
                preferred_keys.extend(t_keys)
        if preferred_keys:
            for key in preferred_keys:
                info = TEMPLATES.get(key)
                if not info:
                    continue
                name_clean = info["name"].lower()
                score = SequenceMatcher(None, label_clean, name_clean).ratio()
                is_word_match = re.search(r'\b' + re.escape(label_clean) + r'\b', name_clean) or re.search(r'\b' + re.escape(name_clean) + r'\b', label_clean)
                for alias in info.get("aliases", []):
                    alias_clean = alias.lower()
                    score = max(score, SequenceMatcher(None, label_clean, alias_clean).ratio())
                    if re.search(r'\b' + re.escape(label_clean) + r'\b', alias_clean) or re.search(r'\b' + re.escape(alias_clean) + r'\b', label_clean):
                        is_word_match = True
                if score >= 0.70 or is_word_match:
                    if not is_forbidden_mapping(label_clean, key):
                        best_template, best_score = key, 0.95
                        if any(ew in label_clean for ew in EXCLUSION_WORDS):
                            best_score = 0.65
                        log_match_attempt(best_template, best_score)
                        return best_template, best_score

    # D. Form Category Match
    CATEGORY_KEYWORDS = {
        "healthcare": ["mrn_number", "insurance_provider", "insurance_number", "allergies", "current_medications", "patient_name", "hospital"],
        "medical": ["mrn_number", "insurance_provider", "insurance_number", "allergies", "current_medications"],
        "education": ["school_name", "college_name", "university", "degree", "course", "percentage", "cgpa", "passing_year", "roll_number", "registration_number"],
        "scholarship": ["school_name", "college_name", "university", "degree", "course", "percentage", "cgpa", "passing_year", "roll_number", "registration_number"],
        "admission": ["school_name", "college_name", "university", "degree", "course", "percentage", "cgpa", "passing_year", "roll_number", "registration_number"],
        "banking": ["bank_name", "account_number", "ifsc", "branch_name", "annual_income", "salary"],
        "finance": ["bank_name", "account_number", "ifsc", "branch_name", "annual_income", "salary"],
        "insurance": ["insurance_provider", "insurance_number"],
        "employment": ["employee_id", "designation", "department", "company_name", "experience", "salary"],
        "kyc": ["aadhaar", "pan", "passport", "driving_license", "voter_id", "id_proof_type", "id_proof_number"],
        "passport": ["passport", "nationality", "country"],
        "government": ["aadhaar", "pan", "passport", "driving_license", "voter_id", "nationality"]
    }
    if form_category:
        cat_clean = form_category.lower()
        preferred_keys = []
        for cat_key, t_keys in CATEGORY_KEYWORDS.items():
            if cat_key in cat_clean:
                preferred_keys.extend(t_keys)
        if preferred_keys:
            for key in preferred_keys:
                info = TEMPLATES.get(key)
                if not info:
                    continue
                name_clean = info["name"].lower()
                score = SequenceMatcher(None, label_clean, name_clean).ratio()
                is_word_match = re.search(r'\b' + re.escape(label_clean) + r'\b', name_clean) or re.search(r'\b' + re.escape(name_clean) + r'\b', label_clean)
                for alias in info.get("aliases", []):
                    alias_clean = alias.lower()
                    score = max(score, SequenceMatcher(None, label_clean, alias_clean).ratio())
                    if re.search(r'\b' + re.escape(label_clean) + r'\b', alias_clean) or re.search(r'\b' + re.escape(alias_clean) + r'\b', label_clean):
                        is_word_match = True
                if score >= 0.70 or is_word_match:
                    if not is_forbidden_mapping(label_clean, key):
                        best_template, best_score = key, 0.92
                        if any(ew in label_clean for ew in EXCLUSION_WORDS):
                            best_score = 0.65
                        log_match_attempt(best_template, best_score)
                        return best_template, best_score

    # E. Semantic Similarity Match
    best_template = None
    best_score = 0.0
    for key, info in TEMPLATES.items():
        name_clean = info["name"].lower()
        score = SequenceMatcher(None, label_clean, name_clean).ratio()
        
        # Word boundary containment check with aliases
        for alias in info.get("aliases", []):
            alias_clean = alias.lower()
            if re.search(r'\b' + re.escape(alias_clean) + r'\b', label_clean):
                sub_score = 0.85 + (len(alias_clean) / len(label_clean)) * 0.13
                score = max(score, min(0.98, sub_score))
            else:
                score = max(score, SequenceMatcher(None, label_clean, alias_clean).ratio())
                
        if score > best_score:
            if not is_forbidden_mapping(label_clean, key):
                best_score = score
                best_template = key
            
    # Apply Future-Proof Exclusion Filter
    if best_score >= 0.70:
        if any(ew in label_clean for ew in EXCLUSION_WORDS):
            best_score = 0.65
            
    log_match_attempt(best_template, best_score)
    return best_template, best_score
