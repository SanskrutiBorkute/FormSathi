import os
import json

class AIProvider:
    def explain_field(self, field_type, label, language='en'):
        raise NotImplementedError
        
    def summarize_form(self, form_type, fields, language='en'):
        raise NotImplementedError
        
    def answer_assistant_query(self, query, form_context, language='en'):
        raise NotImplementedError

# -------------------------------------------------------------
# LOCAL AI PROVIDER IMPLEMENTATION
# -------------------------------------------------------------
class LocalAIProvider(AIProvider):
    def explain_field(self, field_type, label, language='en', nearby_text='', form_category='', section_title=''):
        import guidance_templates
        
        lang = language.lower()
        if lang not in ['en', 'hi', 'mr']:
            lang = 'en'
            
        # Match using semantic template matcher
        template_key, score = guidance_templates.match_field_to_template(label, section_title=section_title, form_category=form_category)
        
        # Check confidence threshold
        if score >= 0.90 and template_key in guidance_templates.TEMPLATES:
            # We have a valid match! Get translation details
            tmpl = guidance_templates.TEMPLATES[template_key]
            details = tmpl.get(lang, tmpl['en'])
            
            return {
                "what": details.get("what", ""),
                "input_guidance": details.get("input_guidance", ""),
                "why": details.get("why", ""),
                "formats": details.get("formats", ""),
                "example": details.get("example", ""),
                "mistakes": details.get("mistakes", ""),
                "validation": details.get("validation", ""),
                "matched_template": tmpl["name"],
                "confidence_score": f"{int(score * 100)}%"
            }
        else:
            # Low confidence or unknown template: Generate dynamic guidance locally
            # 1. Clean label for usage
            clean_lbl = label.rstrip(': -–—?').strip()
            
            # 2. Local dynamic translations based on language
            if lang == 'hi':
                fmt = "सामान्य पाठ प्रारूप"
                val = "निर्देशों के अनुसार भरा जाना चाहिए"
                ex_val = f"एक उपयुक्त '{clean_lbl}' दर्ज करें"
                
                label_lower = clean_lbl.lower()
                if "date" in label_lower or "दिनांक" in label_lower or "तारीख" in label_lower or "वर्ष" in label_lower:
                    fmt = "DD/MM/YYYY या YYYY-MM-DD"
                    ex_val = "15/06/2026 या 2026"
                elif "number" in label_lower or "no" in label_lower or "संख्या" in label_lower or "क्रमांक" in label_lower or "कोड" in label_lower or "code" in label_lower or "id" in label_lower:
                    fmt = "अल्फ़ान्यूमेरिक पहचान कोड"
                    ex_val = "NUM12345"
                elif "amount" in label_lower or "fee" in label_lower or "salary" in label_lower or "income" in label_lower or "वेतन" in label_lower or "आय" in label_lower or "रकम" in label_lower:
                    fmt = "केवल संख्यात्मक मान"
                    ex_val = "50000"
                    val = "केवल अंक होने चाहिए, मुद्रा चिह्न या अल्पविराम नहीं।"
                
                res = {
                    "what": f"यह फ़ील्ड {form_category or 'फॉर्म'} के {section_title or 'विवरण'} अनुभाग में आवेदक के '{clean_lbl}' को दर्शाता है।",
                    "input_guidance": f"कृपया खाली फ़ील्ड में अपने आधिकारिक विवरण के अनुसार '{clean_lbl}' दर्ज करें।",
                    "why": f"यह जानकारी फॉर्म जारीकर्ता द्वारा आपके प्रोफाइल विवरण को सत्यापित करने और '{clean_lbl}' की पुष्टि के लिए आवश्यक है।",
                    "formats": fmt,
                    "example": ex_val,
                    "mistakes": f"गलत जानकारी भरना, वर्तनी की गलतियाँ करना, या अनिवार्य होने पर इसे खाली छोड़ना।",
                    "validation": val,
                    "matched_template": "N/A",
                    "confidence_score": f"{int(score * 100)}%"
                }
            elif lang == 'mr':
                fmt = "सामान्य मजकूर स्वरूप"
                val = "सूचनांनुसार अचूक भरावे"
                ex_val = f"एक योग्य '{clean_lbl}' लिहा"
                
                label_lower = clean_lbl.lower()
                if "date" in label_lower or "तारीख" in label_lower or "वर्ष" in label_lower or "दिनांक" in label_lower:
                    fmt = "DD/MM/YYYY किंवा YYYY-MM-DD"
                    ex_val = "१५/०६/२०२६ किंवा २०२६"
                elif "number" in label_lower or "no" in label_lower or "क्रमांक" in label_lower or "कोड" in label_lower or "code" in label_lower or "id" in label_lower:
                    fmt = "अल्फान्यूमेरिक ओळख कोड"
                    ex_val = "NUM12345"
                elif "amount" in label_lower or "fee" in label_lower or "salary" in label_lower or "income" in label_lower or "उत्पन्न" in label_lower or "वेतन" in label_lower or "रक्कम" in label_lower:
                    fmt = "केवळ संख्यात्मक अंक"
                    ex_val = "50000"
                    val = "केवळ अंक असावेत, स्वल्पविराम किंवा चलनाचे चिन्ह नसावे."
                
                res = {
                    "what": f"हे फ़ील्ड {form_category or 'अर्ज'} मधील {section_title or 'सामान्य'} विभागांतर्गत तुमचे '{clean_lbl}' दर्शवते.",
                    "input_guidance": f"दिलेल्या चौकटीत तुमचे अधिकृत कागदपत्रांनुसार अचूक '{clean_lbl}' लिहा.",
                    "why": f"सदर माहिती फॉर्म जारीकर्त्याकडून तुमच्या अर्जाची सत्यता पडताळण्यासाठी आणि पडताळणी करण्यासाठी आवश्यक आहे.",
                    "formats": fmt,
                    "example": ex_val,
                    "mistakes": f"स्पेलिंगच्या चुका करणे, चुकीची माहिती देणे किंवा रिकामे सोडणे.",
                    "validation": val,
                    "matched_template": "N/A",
                    "confidence_score": f"{int(score * 100)}%"
                }
            else: # en
                fmt = "Standard text format"
                val = "Should be filled according to instructions"
                ex_val = f"Enter a valid {clean_lbl} value"
                
                label_lower = clean_lbl.lower()
                if "date" in label_lower or "year" in label_lower or "dob" in label_lower or "birth" in label_lower:
                    fmt = "DD/MM/YYYY or YYYY-MM-DD"
                    ex_val = "15/06/2026 or 2026"
                elif "number" in label_lower or "no" in label_lower or "code" in label_lower or "id" in label_lower:
                    fmt = "Alphanumeric identity code"
                    ex_val = "NUM12345"
                elif "amount" in label_lower or "fee" in label_lower or "salary" in label_lower or "income" in label_lower or "ctc" in label_lower:
                    fmt = "Numeric value only"
                    ex_val = "50000"
                    val = "Must contain numeric digits only, no currency signs or commas."
                
                res = {
                    "what": f"This field captures the '{clean_lbl}' under the '{section_title or 'General'}' section of this {form_category or 'form'}.",
                    "input_guidance": f"Please enter your official '{clean_lbl}' accurately in the designated field.",
                    "why": f"This is requested by the form issuer to verify your credentials and validate your application record.",
                    "formats": fmt,
                    "example": ex_val,
                    "mistakes": f"Providing incorrect details, introducing typos, or leaving blank.",
                    "validation": val,
                    "matched_template": "N/A",
                    "confidence_score": f"{int(score * 100)}%"
                }
            return res


    def summarize_form(self, form_type, fields, language='en'):
        lang = language.lower()
        if lang not in ['en', 'hi', 'mr']:
            lang = 'en'
            
        summaries = {
            "Government Forms": {
                "en": {
                    "purpose": "Official application or filing with public administration and municipal bodies.",
                    "who": "Residents or citizens eligible for services or registration updates.",
                    "est_time": "Requires about 15-30 minutes to complete details.",
                    "warnings": "Ensure names and details match your government photo ID to prevent processing delays.",
                    "instructions": "Use block letters, sign the declaration, and verify all mandatory files."
                },
                "hi": {
                    "purpose": "सार्वजनिक प्रशासन और नगरपालिका निकायों के साथ आधिकारिक आवेदन या फाइलिंग।",
                    "who": "सेवाओं या पंजीकरण अपडेट के लिए पात्र निवासी या नागरिक।",
                    "est_time": "विवरण पूरा करने के लिए लगभग 15-30 मिनट की आवश्यकता होती है।",
                    "warnings": "प्रसंस्करण में देरी को रोकने के लिए सुनिश्चित करें कि नाम और विवरण आपके सरकारी फोटो आईडी से मेल खाते हैं।",
                    "instructions": "ब्लॉक अक्षरों का उपयोग करें, घोषणा पर हस्ताक्षर करें, और सभी अनिवार्य फाइलों को सत्यापित करें।"
                },
                "mr": {
                    "purpose": "सार्वजनिक प्रशासन आणि महानगरपालिका संस्थांकडे अधिकृत अर्ज किंवा नोंदणी.",
                    "who": "नागरी सेवा किंवा नोंदणी अद्यतनांसाठी पात्र रहिवासी किंवा नागरिक.",
                    "est_time": "माहिती पूर्ण करण्यासाठी साधारण १५ ते ३० मिनिटे लागतात.",
                    "warnings": "प्रक्रियेत उशीर होऊ नये म्हणून नाव आणि माहिती सरकारी ओळखपत्राशी जुळत असल्याची खात्री करा.",
                    "instructions": "इंग्रजीतील मोठ्या अक्षरात अर्ज भरा, घोषणापत्रावर सही करा आणि सर्व आवश्यक कागदपत्रे तपासा."
                }
            },
            "Banking Forms": {
                "en": {
                    "purpose": "Financial account opening, KYC verification, or service authorization.",
                    "who": "Account holders, bank nominees, or authorized financial signees.",
                    "est_time": "Usually completed within 10-15 minutes.",
                    "warnings": "Verify your tax details and bank branch details are correct.",
                    "instructions": "Keep original identity proofs and branch details on hand."
                },
                "hi": {
                    "purpose": "वित्तीय खाता खोलना, केवाईसी (KYC) सत्यापन, या सेवा प्राधिकरण।",
                    "who": "खाताधारक, बैंक नामांकित व्यक्ति, या अधिकृत वित्तीय हस्ताक्षरकर्ता।",
                    "est_time": "आमतौर पर 10-15 मिनट के भीतर पूरा हो जाता है।",
                    "warnings": "सत्यापित करें कि आपके टैक्स विवरण और बैंक शाखा विवरण सही हैं।",
                    "instructions": "मूल पहचान प्रमाण और शाखा विवरण अपने पास रखें।"
                },
                "mr": {
                    "purpose": "नवीन बँक खाते उघडणे, केवायसी (KYC) पडताळणी किंवा इतर आर्थिक सेवा.",
                    "who": "बँक खातेदार, वारसदार (nominee) किंवा अधिकृत आर्थिक स्वाक्षरीकर्ते.",
                    "est_time": "साधारणपणे १० ते १५ मिनिटांत पूर्ण होते.",
                    "warnings": "तुमचे पॅन कार्ड आणि बँक शाखा तपशील बरोबर असल्याची खात्री करा.",
                    "instructions": "मूळ ओळखपत्रे आणि बँक शाखेची माहिती सोबत ठेवा."
                }
            },
            "Education Forms": {
                "en": {
                    "purpose": "Admission applications, scholarship requests, or academic registrations.",
                    "who": "Students seeking enrollment, financial aid, or graduation credits.",
                    "est_time": "Takes approximately 15-20 minutes.",
                    "warnings": "Academic grades and income limits are strictly audited during verification.",
                    "instructions": "Upload certified marksheets, fee receipts, and school/college ID cards."
                },
                "hi": {
                    "purpose": "प्रवेश आवेदन, छात्रवृत्ति अनुरोध, या शैक्षणिक पंजीकरण।",
                    "who": "नामांकन, वित्तीय सहायता, या शैक्षणिक क्रेडिट चाहने वाले छात्र।",
                    "est_time": "लगभग 15-20 मिनट लगते हैं।",
                    "warnings": "सत्यापन के दौरान शैक्षणिक ग्रेड और पारिवारिक आय सीमाओं का कड़ाई से ऑडिट किया जाता है।",
                    "instructions": "प्रमाणित अंकतालिकाएं, शुल्क रसीदें और स्कूल/कॉलेज आईडी कार्ड अपलोड करें।"
                },
                "mr": {
                    "purpose": "शाळा / कॉलेज प्रवेश अर्ज, शिष्यवृत्ती किंवा शैक्षणिक नोंदणी.",
                    "who": "प्रवेश, आर्थिक मदत किंवा शैक्षणिक श्रेय मिळवू इच्छिणारे विद्यार्थी.",
                    "est_time": "साधारण १५ ते २० मिनिटे लागतात.",
                    "warnings": "पडताळणी दरम्यान शैक्षणिक गुण आणि उत्पन्नाच्या मर्यादेची काटेकोरपणे तपासणी केली जाते.",
                    "instructions": "प्रमाणित गुणपत्रिका, शुल्क भरलेली पावती आणि ओळखपत्र अपलोड करा."
                }
            },
            "Healthcare Forms": {
                "en": {
                    "purpose": "Patient intake, medical records updating, or clinical consent.",
                    "who": "Patients seeking treatment, guardians, or hospital administrators.",
                    "est_time": "Needs about 10 minutes.",
                    "warnings": "Provide precise health history details to prevent critical medical errors.",
                    "instructions": "Attach doctor prescriptions, insurance card details, and clinical reports."
                },
                "hi": {
                    "purpose": "रोगी भर्ती, चिकित्सा रिकॉर्ड अपडेट करना, या नैदानिक सहमति।",
                    "who": "उपचार चाहने वाले रोगी, अभिभावक, या अस्पताल के प्रशासक।",
                    "est_time": "लगभग 10 मिनट की आवश्यकता होती है।",
                    "warnings": "गंभीर चिकित्सा त्रुटियों को रोकने के लिए सटीक स्वास्थ्य इतिहास विवरण प्रदान करें।",
                    "instructions": "डॉक्टर के नुस्खे, बीमा कार्ड विवरण और नैदानिक रिपोर्ट संलग्न करें।"
                },
                "mr": {
                    "purpose": "रुग्णाची माहिती नोंदवणे, वैद्यकीय रेकॉर्ड अद्ययावत करणे किंवा संमती अर्ज.",
                    "who": "उपचार घेणारे रुग्ण, पालक किंवा रुग्णालय व्यवस्थापक.",
                    "est_time": "साधारण १० मिनिटे लागतात.",
                    "warnings": "वैद्यकीय चुका टाळण्यासाठी आरोग्याचा अचूक इतिहास आणि आजारांची माहिती द्या.",
                    "instructions": "डॉक्टरांचे प्रिस्क्रिप्शन, विमा कार्ड आणि इतर वैद्यकीय अहवाल सोबत जोडा."
                }
            },
            "Employment Forms": {
                "en": {
                    "purpose": "Job applications, employee onboarding, or pension/insurance enrollment.",
                    "who": "Job applicants, newly hired employees, or corporate workers.",
                    "est_time": "Takes 15-25 minutes to complete profiles.",
                    "warnings": "Discrepancy in experience history or tax documents can block background checks.",
                    "instructions": "Have your past relieving letters, tax numbers, and academic degrees ready."
                },
                "hi": {
                    "purpose": "नौकरी के आवेदन, कर्मचारी ऑनबोर्डिंग, या पेंशन/बीमा नामांकन।",
                    "who": "नौकरी के आवेदक, नए काम पर रखे गए कर्मचारी, या कॉर्पोरेट कार्यकर्ता।",
                    "est_time": "प्रोफाइल पूरा करने में 15-25 मिनट लगते हैं।",
                    "warnings": "कार्य अनुभव या कर दस्तावेजों में विसंगति पृष्ठभूमि की जांच को रोक सकती है।",
                    "instructions": "अपने पिछले रिलीविंग लेटर, टैक्स नंबर और शैक्षणिक डिग्री तैयार रखें।"
                },
                "mr": {
                    "purpose": "नोकरीचा अर्ज, कर्मचारी ऑनबोर्डिंग किंवा पेन्शन / विमा नोंदणी.",
                    "who": "नोकरीसाठी अर्ज करणारे उमेदवार, नवीन रुजू झालेले कर्मचारी किंवा कामगार.",
                    "est_time": "साधारण १५ ते २५ मिनिटे लागतात.",
                    "warnings": "अनुभव किंवा कर दस्तऐवजांमध्ये तफावत आढळल्यास पार्श्वभूमी पडताळणी (background check) थांबवली जाऊ शकते.",
                    "instructions": "मागील कंपनीचे अनुभव प्रमाणपत्र, कर ओळख क्रमांक आणि शैक्षणिक पदव्या तयार ठेवा."
                }
            },
            "Legal Forms": {
                "en": {
                    "purpose": "Leasing deeds, power of attorney, stamp agreements, or affidavits.",
                    "who": "Tenants, landlords, deponents, or legally authorized contracting parties.",
                    "est_time": "Takes about 15-20 minutes.",
                    "warnings": "Agreements must be notarized and stamped according to local laws to be valid.",
                    "instructions": "Prepare stamp paper, verify lease values, and arrange for witness signatures."
                },
                "hi": {
                    "purpose": "पट्टा विलेख (Leasing deeds), मुख्तारनामा, स्टांप समझौते, या हलफनामा।",
                    "who": "किरायेदार, मकान मालिक, साक्ष्यदाता, या कानूनी रूप से अधिकृत अनुबंधित पक्ष।",
                    "est_time": "लगभग 15-20 मिनट लगते हैं।",
                    "warnings": "वैध होने के लिए समझौतों को स्थानीय कानूनों के अनुसार नोटरीकृत और स्टांप किया जाना चाहिए।",
                    "instructions": "स्टांप पेपर तैयार करें, पट्टा मूल्यों को सत्यापित करें, और गवाहों के हस्ताक्षरों की व्यवस्था करें।"
                },
                "mr": {
                    "purpose": "भाडे करारनामा, कुलमुखत्यारपत्र (POA), मुद्रांक करार किंवा प्रतिज्ञापत्र.",
                    "who": "भाडेकरू, घरमालक, साक्षीदार किंवा कायदेशीर करार करणारे पक्ष.",
                    "est_time": "साधारण १५ ते २० मिनिटे लागतात.",
                    "warnings": "कराराची वैधता सिद्ध करण्यासाठी स्थानिक नियमांनुसार नोटरी करणे आणि मुद्रांक शुल्क भरणे आवश्यक आहे.",
                    "instructions": "योग्य मूल्याचा मुद्रांक कागद तयार ठेवा आणि साक्षीदारांच्या सह्यांची सोय करा."
                }
            },
            "Business Forms": {
                "en": {
                    "purpose": "Vendor registrations, tax invoice generation, or company registrations.",
                    "who": "Business owners, vendors, corporate directors, or accounts managers.",
                    "est_time": "Takes 15-20 minutes.",
                    "warnings": "Corporate entity identifiers and tax profiles are validated with registration registers.",
                    "instructions": "Have GST numbers, company registration cards, and director details handy."
                },
                "hi": {
                    "purpose": "विक्रेता पंजीकरण, टैक्स इनवॉइस जनरेशन, या कंपनी पंजीकरण।",
                    "who": "व्यवसाय के मालिक, विक्रेता, कॉर्पोरेट निदेशक, या खाता प्रबंधक।",
                    "est_time": "15-20 मिनट लगते हैं।",
                    "warnings": "कॉर्पोरेट इकाई पहचानकर्ताओं और टैक्स प्रोफाइल को पंजीकरण रजिस्टरों के साथ सत्यापित किया जाता है।",
                    "instructions": "जीएसटी नंबर, कंपनी पंजीकरण कार्ड और निदेशक विवरण अपने पास रखें।"
                },
                "mr": {
                    "purpose": "विक्रेता (vendor) नोंदणी, कर बीजक (invoice) किंवा कंपनी नोंदणी.",
                    "who": "व्यवसाय मालक, विक्रेते, कॉर्पोरेट संचालक किंवा आर्थिक व्यवस्थापक.",
                    "est_time": "साधारण १५ ते २० मिनिटे लागतात.",
                    "warnings": "व्यवसाय नोंदणी आणि कर संबंधित प्रोफाइल अधिकृत सरकारी रेकॉर्डसह पडताळले जातात.",
                    "instructions": "GST क्रमांक, कंपनी नोंदणी प्रमाणपत्र आणि संचालकांची माहिती तयार ठेवा."
                }
            },
            "Insurance Forms": {
                "en": {
                    "purpose": "Policy claims, asset coverage requests, or beneficiary updates.",
                    "who": "Policy holders, beneficiaries, or insurance underwriters.",
                    "est_time": "Takes 10-15 minutes.",
                    "warnings": "Incorrect incident date, policy limits, or nominee details can delay payout approvals.",
                    "instructions": "Review sum assured details, incident reports, and attach identity cards."
                },
                "hi": {
                    "purpose": "पॉलिसी दावे, संपत्ति कवरेज अनुरोध, या लाभार्थी अपडेट।",
                    "who": "पॉलिसी धारक, लाभार्थी, या बीमा अंडरराइटर।",
                    "est_time": "10-15 मिनट लगते हैं।",
                    "warnings": "गलत घटना तिथि, पॉलिसी सीमा, या नामांकित व्यक्ति के विवरण भुगतान की मंजूरी में देरी कर सकते हैं।",
                    "instructions": "बीमा राशि के विवरण, घटना रिपोर्ट की समीक्षा करें और पहचान पत्र संलग्न करें।"
                },
                "mr": {
                    "purpose": "विमा दावा (claim), मालमत्ता विमा संरक्षण किंवा वारसदार अपडेट.",
                    "who": "विमाधारक, लाभार्थी किंवा विमा सल्लागार.",
                    "est_time": "साधारण १० ते १५ मिनिटे लागतात.",
                    "warnings": "चुकीचे पॉलिसी मर्यादा किंवा वारसदार तपशील दिल्यास दावा मंजूर होण्यास विलंब जाऊ शकतो.",
                    "instructions": "विमा रक्कम, अपघाताचे अहवाल तपासा आणि ओळखपत्र जोडा."
                }
            },
            "Travel Forms": {
                "en": {
                    "purpose": "Visa applications, immigration clearance, or travel declarations.",
                    "who": "Passengers, tourists, or expatriates travelling across borders.",
                    "est_time": "Takes 10-15 minutes.",
                    "warnings": "Passport validity and travel dates must align exactly with flight bookings.",
                    "instructions": "Upload passport scans, travel itineraries, and accommodation confirmations."
                },
                "hi": {
                    "purpose": "वीजा आवेदन, आप्रवासन निकासी, या यात्रा घोषणाएं।",
                    "who": "यात्री, पर्यटक, या सीमा पार यात्रा करने वाले प्रवासी।",
                    "est_time": "10-15 मिनट लगते हैं।",
                    "warnings": "पासपोर्ट की वैधता और यात्रा की तारीखें उड़ान बुकिंग के साथ बिल्कुल मेल खानी चाहिए।",
                    "instructions": "पासपोर्ट स्कैन, यात्रा कार्यक्रम और आवास पुष्टिकरण अपलोड करें।"
                },
                "mr": {
                    "purpose": "व्हिसा अर्ज, इमिग्रेशन पडताळणी किंवा प्रवास घोषणापत्र.",
                    "who": "प्रवासी, पर्यटक किंवा इतर देशांत प्रवास करणारे नागरिक.",
                    "est_time": "साधारण १० ते १५ मिनिटे लागतात.",
                    "warnings": "पासपोर्टची मुदत आणि प्रवासाच्या तारखा विमानाचे तिकीट आणि हॉटेल बुकिंगशी जुळणे आवश्यक आहे.",
                    "instructions": "पासपोर्ट स्कॅन, प्रवासाचे वेळापत्रक आणि हॉटेल बुकिंगची माहिती अपलोड करा."
                }
            },
            "Membership Forms": {
                "en": {
                    "purpose": "Access enrollments, club associations, or subscriber plans.",
                    "who": "Subscribers, gym goers, library members, or professional members.",
                    "est_time": "Takes about 5-10 minutes.",
                    "warnings": "Ensure billing cycle limits and fee deductions match your chosen subscription package.",
                    "instructions": "Confirm package tier and authorize direct fee debit options if desired."
                },
                "hi": {
                    "purpose": "पहुंच नामांकन, क्लब एसोसिएशन, या ग्राहक योजनाएं।",
                    "who": "ग्राहक, जिम जाने वाले, पुस्तकालय के सदस्य, या पेशेवर सदस्य।",
                    "est_time": "लगभग 5-10 मिनट लगते हैं।",
                    "warnings": "सुनिश्चित करें कि बिलिंग चक्र सीमा और शुल्क कटौती आपके चुने हुए सदस्यता पैकेज से मेल खाती है।",
                    "instructions": "पैकेज स्तर की पुष्टि करें और यदि वांछित हो तो सीधे शुल्क डेबिट विकल्पों को अधिकृत करें।"
                },
                "mr": {
                    "purpose": "क्लब सदस्यत्व, जिम किंवा वाचनालय प्रवेश किंवा इतर ग्राहक योजना.",
                    "who": "ग्राहक, जिम किंवा लायब्ररीचे सभासद किंवा व्यावसायिक सदस्य.",
                    "est_time": "साधारण ५ ते १० मिनिटे लागतात.",
                    "warnings": "निवडलेले सदस्यत्व शुल्क आणि बिलिंग सायकलचे नियम नीट तपासा.",
                    "instructions": "योजनेचे स्वरूप तपासा आणि बँक खात्यातून रक्कम वजा करण्याचा पर्याय (auto-debit) काळजीपूर्वक निवडा."
                }
            },
            "Custom Form": {
                "en": {
                    "purpose": "General transaction or application captured in this form configuration.",
                    "who": "Applicants or entities registering details under this structure.",
                    "est_time": "Usually completed within 10-15 minutes.",
                    "warnings": "Check all required details for accurate validation formats.",
                    "instructions": "Complete all blank mandatory fields and review before submitting."
                },
                "hi": {
                    "purpose": "इस फॉर्म कॉन्फ़िगरेशन में कैप्चर किया गया सामान्य लेनदेन या आवेदन।",
                    "who": "इस संरचना के तहत विवरण दर्ज करने वाले आवेदक या संस्थाएं।",
                    "est_time": "आमतौर पर 10-15 मिनट के भीतर पूरा हो जाता है।",
                    "warnings": "सटीक सत्यापन प्रारूपों के लिए सभी आवश्यक विवरणों की जांच करें।",
                    "instructions": "सभी रिक्त अनिवार्य फ़ील्ड्स को पूरा करें और सबमिट करने से पहले समीक्षा करें।"
                },
                "mr": {
                    "purpose": "या अर्जामध्ये गोळा केली जाणारी सर्वसाधारण माहिती किंवा व्यवहार अर्ज.",
                    "who": "या स्वरूपांतर्गत नोंदणी करणारे अर्जदार किंवा व्यावसायिक संस्था.",
                    "est_time": "साधारण १० ते १५ मिनिटांत पूर्ण होते.",
                    "warnings": "अचूक पडताळणीसाठी सर्व आवश्यक चौकटी व्यवस्थित भरल्या आहेत की नाही ते तपासा.",
                    "instructions": "सर्व रिक्त आवश्यक चौकटी पूर्ण करा आणि सादर करण्यापूर्वी पुनरावलोकन करा."
                }
            }
        }
        
        category_key = form_type if form_type in summaries else "Custom Form"
        return summaries[category_key][lang]

    def answer_assistant_query(self, query, form_context, language='en'):
        lang = language.lower()
        q_lower = query.lower()
        
        responses = {
            "en": {
                "hello": "Hello! I am FormSaathi, your universal AI form intelligence assistant. Ask me questions about this form structure.",
                "document": "Based on this form, you will need to prepare: " + ", ".join([d.get('name') for d in form_context.get('predicted_documents', [])]) + ".",
                "error": "Please look at the fields marked in red. They contain formatting errors that need correction.",
                "help": "Click on any form field in the center screen to see what it means, why it is requested, and how to write it correctly.",
                "default": "I analyzed the form fields. Make sure to validate formatting rules for dates, contacts, and emails. Let me know if you need translation support!"
            },
            "hi": {
                "hello": "नमस्ते! मैं फॉर्मसाथी हूं, आपका सार्वभौमिक एआई फॉर्म सहायक। इस फॉर्म के बारे में मुझसे प्रश्न पूछें।",
                "document": "इस फॉर्म के आधार पर, आपको तैयार करना होगा: " + ", ".join([d.get('name') for d in form_context.get('predicted_documents', [])]) + "।",
                "error": "कृपया लाल रंग से चिह्नित फ़ील्ड्स को देखें। उनमें प्रारूप की त्रुटियां हैं जिन्हें सुधारना आवश्यक है।",
                "help": "इसके अर्थ, आवश्यकता और सही लिखने के तरीके को जानने के लिए मध्य स्क्रीन पर किसी भी फ़ील्ड पर क्लिक करें।",
                "default": "मैंने फॉर्म का विश्लेषण किया है। तिथियों, संपर्कों और ईमेल के प्रारूप नियमों को सत्यापित करना सुनिश्चित करें। अनुवाद में मदद के लिए बताएं!"
            },
            "mr": {
                "hello": "नमस्कार! मी फॉर्मसाथी आहे, तुमचा युनिव्हर्सल AI अर्ज सहाय्यक. या अर्जाबद्दल मला काहीही विचारा.",
                "document": "या अर्जाच्या आधारे, तुम्हाला ही कागदपत्रे तयार ठेवावी लागतील: " + ", ".join([d.get('name') for d in form_context.get('predicted_documents', [])]) + ".",
                "error": "कृपया लाल रंगाने दर्शविलेल्या चौकटी पहा. त्यामध्ये काही चुका आहेत ज्या दुरुस्त करणे आवश्यक आहे.",
                "help": "मध्यावरील कोणत्याहीं फील्डवर क्लिक करून त्याचा अर्थ, आवश्यकता आणि तो बरोबर लिहिण्याची पद्धत समजून घ्या.",
                "default": "मी अर्जाचे विश्लेषण केले आहे. जन्मतारीख, मोबाईल क्रमांक आणि ईमेलचे स्वरूप बरोबर असल्याची खात्री करा. भाषा बदलण्यासाठी वरील भाषा बटनांचा वापर करा!"
            }
        }
        
        current_res = responses.get(lang, responses['en'])
        
        if 'hello' in q_lower or 'hi' in q_lower or 'hey' in q_lower or 'नमस्ते' in q_lower or 'नमस्कार' in q_lower:
            return current_res['hello']
        elif 'document' in q_lower or 'paper' in q_lower or 'dastavez' in q_lower or 'कागद' in q_lower or 'प्रमाणपत्र' in q_lower:
            return current_res['document']
        elif 'error' in q_lower or 'mistake' in q_lower or 'chk' in q_lower or 'चुकी' in q_lower or 'दुरुस्त' in q_lower:
            return current_res['error']
        elif 'help' in q_lower or 'explain' in q_lower or 'understand' in q_lower or 'मदत' in q_lower:
            return current_res['help']
            
        return current_res['default']

# -------------------------------------------------------------
# DYNAMIC LLM AI PROVIDER (FOR GEMINI / OPENAI INTEGRATION)
# -------------------------------------------------------------
class LLMAIProvider(AIProvider):
    """
    Online provider that interfaces with Gemini or OpenAI
    if API keys are active. Falls back to LocalAIProvider.
    """
    def __init__(self, provider_type='local', api_key=None):
        self.provider_type = provider_type
        self.api_key = api_key
        self.local_provider = LocalAIProvider()
        
    def _call_llm(self, prompt, system_instruction=None, response_mime_type=None):
        import urllib.request
        import urllib.error
        import urllib.parse
        import json

        # Check if we should use OpenAI or Gemini
        # Standard check for api key prefix or provider type config
        is_openai = "sk-" in str(self.api_key) or self.provider_type == 'openai'
        
        if is_openai:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.2
            }
            if response_mime_type == "application/json":
                data["response_format"] = {"type": "json_object"}
                
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                content = res_data['choices'][0]['message']['content']
                return content
        else:
            # Gemini API using v1beta
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            contents = {
                "parts": [{"text": prompt}]
            }
            data = {
                "contents": [contents],
                "generationConfig": {
                    "temperature": 0.2
                }
            }
            if system_instruction:
                data["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }
            if response_mime_type == "application/json":
                data["generationConfig"]["responseMimeType"] = "application/json"
                
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                content = res_data['candidates'][0]['content']['parts'][0]['text']
                return content

    def explain_field(self, field_type, label, language='en', nearby_text='', form_category='', section_title=''):
        import guidance_templates
        template_key, score = guidance_templates.match_field_to_template(label, section_title=section_title, form_category=form_category)
        
        if score >= 0.90:
            # High confidence: use standard template
            return self.local_provider.explain_field(field_type, label, language, nearby_text, form_category, section_title)
            
        if not self.api_key:
            return self.local_provider.explain_field(field_type, label, language, nearby_text, form_category, section_title)
            
        try:
            lang_name = "English"
            if language.lower() == 'hi':
                lang_name = "Hindi"
            elif language.lower() == 'mr':
                lang_name = "Marathi"
                
            system_instruction = (
                "You are FormSaathi, an intelligent assistant designed to help users fill out forms. "
                "You must return response in JSON format matching this exact schema:\n"
                "{\n"
                "  \"what\": \"Detailed definition of the field\",\n"
                "  \"input_guidance\": \"What exactly the user should enter in this field (plain-language instruction for a layman)\",\n"
                "  \"example\": \"An example value (e.g. format examples)\",\n"
                "  \"why\": \"Explanation of why this field is required by the form issuer/organization\",\n"
                "  \"formats\": \"Accepted format(s) for this field\",\n"
                "  \"mistakes\": \"Common mistakes to avoid when filling this field\",\n"
                "  \"validation\": \"Validation rules or check criteria for the field\"\n"
                "}\n"
                f"Generate all description text in {lang_name} language. Keep it very clear and descriptive."
            )
            
            prompt = (
                f"Explain the custom field '{label}' in the form.\n"
                f"Here is the context we detected:\n"
                f"- Form Category: {form_category}\n"
                f"- Section Title: {section_title}\n"
                f"- Nearby OCR Text context: {nearby_text}\n\n"
                f"Since this is a custom field with low template matching confidence, you must generate a highly accurate, custom guidance specific to this field and its context. Do not use generic explanations. "
                f"Ensure the explanations are in {lang_name}. Return only the JSON object."
            )
            
            res_content = self._call_llm(prompt, system_instruction, response_mime_type="application/json")
            import json
            res_json = json.loads(res_content.strip())
            
            # Ensure all keys exist, otherwise populate from local provider
            local_fallback = self.local_provider.explain_field(field_type, label, language, nearby_text, form_category, section_title)
            for k in ["what", "input_guidance", "example", "why", "formats", "mistakes", "validation"]:
                if k not in res_json or not res_json[k]:
                    res_json[k] = local_fallback.get(k, "")
            
            res_json["matched_template"] = "N/A"
            res_json["confidence_score"] = f"{int(score * 100)}%"
            return res_json
        except Exception as e:
            print(f"LLM explain_field error: {e}. Falling back to LocalAIProvider...")
            return self.local_provider.explain_field(field_type, label, language, nearby_text, form_category, section_title)

    def summarize_form(self, form_type, fields, language='en'):
        if not self.api_key:
            return self.local_provider.summarize_form(form_type, fields, language)
        try:
            lang_name = "English"
            if language.lower() == 'hi':
                lang_name = "Hindi"
            elif language.lower() == 'mr':
                lang_name = "Marathi"
                
            fields_summary = ", ".join([f.get('label', '') for f in fields[:15]])
            
            system_instruction = (
                "You are FormSaathi, an intelligent assistant designed to summarize forms. "
                "You must return response in JSON format matching this exact schema:\n"
                "{\n"
                "  \"purpose\": \"A short description of the form's purpose\",\n"
                "  \"who\": \"Who needs to fill out this form\",\n"
                "  \"est_time\": \"Estimated time to complete this form (e.g. '10-15 minutes')\",\n"
                "  \"warnings\": \"Critical warning messages or common pitfalls\",\n"
                "  \"instructions\": \"Step-by-step submission instructions\"\n"
                "}\n"
                f"Generate all description text in {lang_name} language."
            )
            
            prompt = (
                f"Provide a summary for a '{form_type}' form. "
                f"The form contains these fields: {fields_summary}. "
                f"Return only the JSON object."
            )
            
            res_content = self._call_llm(prompt, system_instruction, response_mime_type="application/json")
            import json
            res_json = json.loads(res_content.strip())
            local_fallback = self.local_provider.summarize_form(form_type, fields, language)
            for k in ["purpose", "who", "est_time", "warnings", "instructions"]:
                if k not in res_json or not res_json[k]:
                    res_json[k] = local_fallback.get(k, "")
            return res_json
        except Exception as e:
            print(f"LLM summarize_form error: {e}. Falling back to LocalAIProvider...")
            return self.local_provider.summarize_form(form_type, fields, language)

    def answer_assistant_query(self, query, form_context, language='en'):
        if not self.api_key:
            return self.local_provider.answer_assistant_query(query, form_context, language)
        try:
            lang_name = "English"
            if language.lower() == 'hi':
                lang_name = "Hindi"
            elif language.lower() == 'mr':
                lang_name = "Marathi"
                
            system_instruction = (
                "You are FormSaathi, an intelligent assistant designed to help users with their form filling query. "
                f"Provide your answer directly and naturally in the {lang_name} language. Do not return JSON. Just return the response text."
            )
            
            fields_str = "\n".join([f"{f['label']} ({f['detected_type']}): Value is '{f['current_value']}'" for f in form_context.get('fields', [])])
            prompt = (
                f"The user is filling a form of type '{form_context.get('form_type', 'Custom')}' and asks: '{query}'.\n"
                f"Current form context:\n"
                f"Fields:\n{fields_str}\n\n"
                f"Predicted Documents required: {', '.join([d.get('name') for d in form_context.get('predicted_documents', [])])}\n\n"
                f"Respond to their query clearly in {lang_name}."
            )
            
            res_content = self._call_llm(prompt, system_instruction)
            return res_content.strip()
        except Exception as e:
            print(f"LLM answer_assistant_query error: {e}. Falling back to LocalAIProvider...")
            return self.local_provider.answer_assistant_query(query, form_context, language)
