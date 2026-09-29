from typing import Dict, Any, List

# ---------------------------------------------------------------------------
# Multi-language static disease knowledge base (EN, TA, HI)
# Fixed, pre-written human expert content — NO LLM hallucination.
# ---------------------------------------------------------------------------
STATIC_DISEASE_INFO: Dict[str, Dict[str, Dict[str, str]]] = {
    "bud_rot": {
        "en": {
            "display_name": "Bud Rot",
            "description": "Lethal fungal pathogen (Phytophthora palmivora) attacking the central spear leaf. If untreated, it causes total destruction of the bud tissue.",
            "treatment": "Cut away rotted tissue completely and apply Bordeaux Paste (10%). Drench canopy with Metalaxyl + Mancozeb (2g/L water)."
        },
        "ta": {
            "display_name": "மொட்டு அழுகல் நோய் (Bud Rot)",
            "description": "மத்திய குருத்து இலையைத் தாக்கும் கொடிய பூஞ்சை நோய். சிகிச்சை அளிக்கப்படாவிட்டால் மொட்டு திசு முற்றிலும் அழிந்துவிடும்.",
            "treatment": "அழுகிய திசுக்களை அகற்றி 10% போர்டோ பேஸ்ட் தடவவும். மெட்டாலாக்ஸில் + மேன்கோசெப் (லிட்டருக்கு 2 கிராம்) தெளிக்கவும்."
        },
        "hi": {
            "display_name": "बड रॉट (Bud Rot)",
            "description": "केंद्रीय नई पत्ती पर हमला करने वाला घातक फंगल रोग। यदि इलाज न किया जाए तो पूरा बड नष्ट हो जाता है।",
            "treatment": "सड़े हुए ऊतकों को काटकर 10% बोर्दो पेस्ट लगाएं। मेटालेक्सिल + मैंकोजेब (2 ग्राम/लीटर) का छिड़काव करें।"
        }
    },
    "leaf_blight": {
        "en": {
            "display_name": "Leaf Blight",
            "description": "Fungal infection causing reddish-brown necrotic spots, dry lower fronds, and severe foliage damage.",
            "treatment": "Prune and burn infected fronds immediately. Spray Copper Oxychloride (0.3%) or Mancozeb (0.2%) thoroughly on the canopy."
        },
        "ta": {
            "display_name": "இலை கருகல் நோய் (Leaf Blight)",
            "description": "சிவப்பு-பழுப்பு காய்ந்த புள்ளிகள் மற்றும் கீழ் மட்டைகள் காய்ந்துபோகச் செய்யும் பூஞ்சை நோய்.",
            "treatment": "பாதிக்கப்பட்ட மட்டைகளை வெட்டி எரிக்கவும். காப்பர் ஆக்சிகுளோரைடு (0.3%) அல்லது மேன்கோசெப் (0.2%) தெளிக்கவும்."
        },
        "hi": {
            "display_name": "लीफ ब्लाइट (Leaf Blight)",
            "description": "फंगल संक्रमण जो पत्तियों पर लाल-भूरे रंग के धब्बे बनाता है और निचली पत्तियों को सुखा देता है।",
            "treatment": "संक्रमित पत्तियों को काटकर जला दें। कॉपर ऑक्सीक्लोराइड (0.3%) या मैंकोजेब (0.2%) का छिड़काव करें।"
        }
    },
    "leaf_spot": {
        "en": {
            "display_name": "Leaf Spot / Bipolaris",
            "description": "Fungal spots with brown borders and pale centers causing premature leaf drying.",
            "treatment": "Remove severely affected pinnae. Spray Carbendazim (0.1%) or Chlorothalonil (0.2%) at 14-day intervals."
        },
        "ta": {
            "display_name": "இலைப்புள்ளி நோய் (Leaf Spot)",
            "description": "இலைகளில் பழுப்பு நிற புள்ளிகளை உருவாக்கி இலைகளை உலர வைக்கும் பூஞ்சை நோய்.",
            "treatment": "பாதிக்கப்பட்ட இலைகளை அகற்றி, கார்பெண்டாசிம் (0.1%) அல்லது குளோரோதலோனில் (0.2%) தெளிக்கவும்."
        },
        "hi": {
            "display_name": "लीफ स्पॉट (Leaf Spot)",
            "description": "पत्तियों पर भूरे घेरे वाले धब्बे जो पत्तियों को समय से पहले सुखा देते हैं।",
            "treatment": "प्रभावित पत्तियों को हटाएं। कार्बेंडाजिम (0.1%) या क्लोरोथालोनिल (0.2%) का छिड़काव करें।"
        }
    },
    "stem_bleeding": {
        "en": {
            "display_name": "Stem Bleeding",
            "description": "Fungal infection causing dark reddish-brown sap exudation from trunk cracks, weakening internal vascular bundles.",
            "treatment": "Chisel out infected bark tissue down to clean wood. Apply Coal Tar or Calixin (5ml/L) over chiseled surface."
        },
        "ta": {
            "display_name": "தண்டு வடித்தல் நோய் (Stem Bleeding)",
            "description": "மரத்தின் தண்டில் உள்ள பிளவுகளிலிருந்து அடர் சிவப்பு-பழுப்பு நிற சாறு வடியும் பூஞ்சை நோய்.",
            "treatment": "பாதிக்கப்பட்ட பட்டையைச் செதுக்கி எடுத்துவிட்டு, தார் அல்லது காலிக்சின் (லிட்டருக்கு 5 மி.லி) தடவவும்."
        },
        "hi": {
            "display_name": "स्टेम ब्लीडिंग (Stem Bleeding)",
            "description": "तने की दरारों से गहरे लाल-भूरे रंग का रस निकलने वाला फंगल संक्रमण।",
            "treatment": "संक्रमित छाल को छीलकर साफ करें। उस स्थान पर कोल तार या कैलिक्सिन (5ml/L) लगाएं।"
        }
    },
    "lethal_yellowing": {
        "en": {
            "display_name": "Lethal Yellowing / Deficiency",
            "description": "Chlorosis and severe yellowing of fronds caused by phytoplasma infection or severe soil nutrient imbalance.",
            "treatment": "Apply balanced NPK fertilizer with Potash (K) and Magnesium. Inject Oxytetracycline for phytoplasma."
        },
        "ta": {
            "display_name": "மஞ்சள் நோய் / குறைபாடு (Lethal Yellowing)",
            "description": "மட்டைகள் மஞ்சள் நிறமாக மாறுதல் மற்றும் ஊட்டச்சத்து குறைபாட்டால் ஏற்படும் பலவீனம்.",
            "treatment": "பொட்டாசியம் மற்றும் மெக்னீசியம் கொண்ட சீரான NPK உரங்களைப் பயன்படுத்தவும்."
        },
        "hi": {
            "display_name": "लीथल येलोइंग / पोषक तत्व कमी",
            "description": "पत्तियों का पीला पड़ना जो पोषक तत्वों की कमी या फाइटोप्लाज्मा संक्रमण से होता है।",
            "treatment": "पोटाश और मैग्नीशियम युक्त संतुलित NPK उर्वरक डालें।"
        }
    },
    "caterpillar": {
        "en": {
            "display_name": "Black-Headed Caterpillar",
            "description": "Pest infestation feeding on leaf epidermis under silken galleries, scorching lower canopies.",
            "treatment": "Release larval parasitoids (Bracon hebetor) at 20-30 per palm. Spray Neem seed kernel extract (NSKE 5%)."
        },
        "ta": {
            "display_name": "கருந்தலை புழு (Caterpillar)",
            "description": "இலைகளைச் சுருட்டித் தின்று மரத்தைக் காயவைக்கும் புழுத் தாக்குதல்.",
            "treatment": "வேப்பங் கொட்டை சாறு (5%) தெளிக்கவும் அல்லது பிராகான் ஒட்டுண்ணிகளை வெளியிடவும்."
        },
        "hi": {
            "display_name": "ब्लैक हेडेड कैटरपिलर",
            "description": "पत्तियों को खाकर उन्हें सुखाने वाला कीड़ा।",
            "treatment": "नीम बीज अर्क (5%) का छिड़काव करें या परजीवी ततैया (Bracon hebetor) छोड़ें।"
        }
    },
    "healthy": {
        "en": {
            "display_name": "Healthy Coconut Palm",
            "description": "Vibrant green foliage, strong canopy structure, and robust pinnae showing no pathogenic infection.",
            "treatment": "Maintain regular weeding, balanced bi-annual organic fertilization, and adequate monsoon drainage."
        },
        "ta": {
            "display_name": "ஆரோக்கியமான தென்னை மரம் (Healthy)",
            "description": "பசுமையான இலைகள் மற்றும் நல்ல ஆரோக்கியத்துடன் கூடிய தென்னை மரம்.",
            "treatment": "வழக்கமான உரமிடுதல் மற்றும் நீர் மேலாண்மையைத் தொடர்ந்து பராமரிக்கவும்."
        },
        "hi": {
            "display_name": "स्वस्थ नारियल का पेड़ (Healthy)",
            "description": "गहरे हरे रंग की पत्तियों और स्वस्थ विकास वाला नारियल का पेड़।",
            "treatment": "नियमित खाद और जल प्रबंधन बनाए रखें।"
        }
    },
    "uncertain": {
        "en": {
            "display_name": "Uncertain / Unclear Leaf Condition",
            "description": "Detection confidence is below threshold or foliage visual features are inconclusive.",
            "treatment": "Take a clearer close-up photograph of the affected leaf in good lighting and re-scan."
        },
        "ta": {
            "display_name": "தெளிவற்ற நிலை (Uncertain)",
            "description": "படத்தின் மூலம் நோய் கண்டறிதல் தெளிவில்லாமல் உள்ளது.",
            "treatment": "நல்ல வெளிச்சத்தில் இலைப்பகுதியை மீண்டும் தெளிவாக படம் பிடித்து ஸ்கேன் செய்யவும்."
        },
        "hi": {
            "display_name": "अनिश्चित स्थिति (Uncertain)",
            "description": "तस्वीर से रोग की पहचान स्पष्ट नहीं हो सकी है।",
            "treatment": "अच्छी रोशनी में पत्ती की साफ तस्वीर लेकर फिर से स्कैन करें।"
        }
    }
}

DISEASE_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "leaf blight": {
        "display_name": "Leaf Blight",
        "scientific_name": "Pestalotiopsis palmarum",
        "severity": "High",
        "severity_color": "#d90429",
        "description": "Leaf Blight is a destructive fungal disease affecting coconut palm foliage.",
        "symptoms": ["Yellowish-brown specs expanding into reddish-brown spots", "Drying of lower fronds"],
        "causes": ["High humidity", "Potassium deficiency"],
        "recommended_action": ["Prune infected fronds", "Apply Copper Oxychloride (0.3%)"],
        "prevention": ["Maintain optimal spacing", "Bi-annual organic neem cake"]
    },
    "bud rot": {
        "display_name": "Bud Rot",
        "scientific_name": "Phytophthora palmivora",
        "severity": "High",
        "severity_color": "#d90429",
        "description": "Lethal pathogen attacking central spear leaf.",
        "symptoms": ["Wilting central spear leaf", "Foul odor emitting from rotting core"],
        "causes": ["Monsoon rains", "Poor drainage"],
        "recommended_action": ["Remove rotted tissue", "Apply Bordeaux Paste (10%)"],
        "prevention": ["Prophylactic 1% Bordeaux spray prior to monsoon"]
    },
    "stem bleeding": {
        "display_name": "Stem Bleeding",
        "scientific_name": "Thielaviopsis paradoxa",
        "severity": "Medium",
        "severity_color": "#f77f00",
        "description": "Dark reddish-brown liquid exudation from cracks on the trunk.",
        "symptoms": ["Exudation of dark sap", "Yellowing of fronds"],
        "causes": ["Growth of Thielaviopsis fungus"],
        "recommended_action": ["Chisel out infected bark tissue", "Apply Coal Tar"],
        "prevention": ["Avoid trunk injuries"]
    },
    "healthy": {
        "display_name": "Healthy Coconut Palm",
        "scientific_name": "Cocos nucifera",
        "severity": "Low",
        "severity_color": "#2a9d8f",
        "description": "Vibrant green color, strong crown symmetry, and no infection.",
        "symptoms": ["Vibrant deep green fronds"],
        "causes": ["Optimal soil nutrients"],
        "recommended_action": ["Continue routine agronomic maintenance"],
        "prevention": ["Keep palm basin free of weeds"]
    }
}


def _normalize_key(class_name: str) -> str:
    """Map raw prediction class names to standardized keys."""
    k = class_name.lower().strip()
    if "blight" in k:
        return "leaf_blight"
    elif "bud" in k or "rot" in k and "leaf" not in k:
        return "bud_rot"
    elif "spot" in k or "bipolaris" in k:
        return "leaf_spot"
    elif "stem" in k or "bleed" in k:
        return "stem_bleeding"
    elif "yellow" in k or "deficiency" in k:
        return "lethal_yellowing"
    elif "caterpillar" in k or "pest" in k:
        return "caterpillar"
    elif "health" in k:
        return "healthy"
    return "uncertain"


def get_disease_info(class_name: str, language: str = "en") -> Dict[str, Any]:
    """
    Retrieve localized disease info dictionary for the given class_name and language code (en, ta, hi).
    Returns fixed pre-written description, recommended treatment, severity, and severity_color.
    """
    if language not in ("en", "ta", "hi"):
        language = "en"

    key = _normalize_key(class_name)
    info_dict = STATIC_DISEASE_INFO.get(key, STATIC_DISEASE_INFO["uncertain"])
    localized = info_dict.get(language, info_dict["en"])

    # Determine severity
    severity_map = {
        "bud_rot": ("High", "#d90429"),
        "leaf_blight": ("High", "#d90429"),
        "caterpillar": ("High", "#d90429"),
        "stem_bleeding": ("Medium", "#f77f00"),
        "leaf_spot": ("Medium", "#f77f00"),
        "lethal_yellowing": ("Medium", "#e9c46a"),
        "healthy": ("Low", "#2a9d8f"),
        "uncertain": ("Medium", "#e9c46a"),
    }
    sev, color = severity_map.get(key, ("Medium", "#f77f00"))

    # Rich base KB info if available
    kb_match = DISEASE_KNOWLEDGE_BASE.get(class_name.lower().strip(), {})
    scientific = kb_match.get("scientific_name", "Cocos nucifera Pathogen")

    return {
        "class_key": key,
        "display_name": localized.get("display_name", class_name.title()),
        "scientific_name": scientific,
        "severity": sev,
        "severity_color": color,
        "description": localized.get("description", ""),
        "treatment": localized.get("treatment", ""),
        "recommended_action": [localized.get("treatment", "")],
        "symptoms": kb_match.get("symptoms", [localized.get("description", "")]),
        "causes": kb_match.get("causes", ["Pathogenic or environmental factors."]),
        "prevention": kb_match.get("prevention", ["Maintain orchard sanitation and balanced fertilization."]),
    }
