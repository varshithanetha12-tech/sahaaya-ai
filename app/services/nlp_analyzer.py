import re
from typing import Dict, Any, List, Tuple, Optional
from app.models.schemas import NLPMetrics, EmotionMetrics

# Multilingual keywords dictionary covering 10 Indian languages & English
# Covers Atrocity, Threats, Coercion, Boycott, Displacement, Violence, Fear, Hopelessness, Emergency
LANGUAGE_LEXICON = {
    "threat": [
        # English
        "kill", "attack", "burn", "threat", "destroy", "violence", "beat", "weapon", "harm", "assault", "boycott",
        # Telugu (Native + Transliterated)
        "చంపుతాం", "కొట్టారు", "దాడి", "భయపెడుతున్నారు", "చంపేస్తామని", "బెదిరిస్తున్నారు", "బహిష్కరణ",
        "champutham", "kottaru", "daadi", "bediristunnaru", "bahishkarana", "bhayapeditunnaru",
        # Hindi
        "मार", "धमकी", "हमला", "जला", "बहिष्कार", "जान से मारना", "डरा रहे हैं",
        "maar", "dhamki", "hamla", "jala", "bahishkar", "dara rahe hain",
        # Tamil
        "கொலை", "தாக்குதல்", "மிரட்டல்", "எரித்து", "பயமுறுத்துகிறார்கள்",
        "kolai", "thaakkuthal", "mirattal", "bayamuruthugiraargal",
        # Kannada
        "ಕೊಲೆ", "ದಾಳಿ", "ಬೆದರಿಕೆ", "ಹೊಡೆದರು", "ಬಹಿಷ್ಕಾರ",
        "kole", "daali", "bedarike", "hodedaru",
        # Malayalam
        "കൊല്ലും", "ആക്രമണം", "ഭീഷണി", "ബഹിഷ്കരണം",
        "kollum", "aakramanam", "bheeshani",
        # Marathi
        "मारहाण", "धमकी", "हल्ला", "जीव मारण्याची", "बहिष्कार",
        "marhaan", "dhamki", "halla", "bahishkar",
        # Bengali
        "হত্যা", "আক্রমণ", "হুমকি", "মারধর", "বয়কট",
        "hotya", "aakromon", "humki", "mardhor",
        # Gujarati
        "જાનથી મારી", "હુમલો", "ધમકી", "બહિષ્કાર",
        "dhamki", "humlo", "bahishkar",
        # Odia
        "ହତ୍ୟା", "ଆକ୍ରମଣ", "ଧମକ", "ବହିଷ୍କାର",
        "hatya", "aakramana", "dhamaka"
    ],
    "fear_anxiety": [
        # English
        "terrified", "afraid", "scared", "fear", "trembling", "panic", "shivering", "nowhere to go", "crying",
        # Telugu
        "భయంగా", "వణుకు", "ఆందోళన", "దిక్కులేదు", "ఏడుపు", "భయం",
        "bhayanga", "vanuku", "aandolana", "dikkuledu", "bhayam",
        # Hindi
        "डर", "खौफ", "कांप", "घबराहट", "रोना", "कोई रास्ता नहीं",
        "dar", "khauf", "ghabrahat", "kaamp", "rona",
        # Tamil
        "பயம்", "நடுக்கம்", "கவலை", "அழுகை",
        "bayam", "nadukkam", "kavalai",
        # Kannada
        "ಭಯ", "ಆತಂಕ", "ನಡುಕ", "ಅಳು",
        "bhaya", "aatanka", "naduka",
        # Malayalam
        "ഭയം", "വിറയൽ", "ആശങ്ക", "കരച്ചിൽ",
        "bhayam", "ashanka", "karachil",
        # Marathi
        "भीती", "घाबरलो", "थरथर", "चिंता",
        "bheeti", "ghabharlo", "chinta",
        # Bengali
        "ভয়", "আতঙ্ক", "কাঁপুনি", "কান্না",
        "bhay", "aatanko", "kanna",
        # Gujarati
        "ડર", "ભય", "ધ્રૂજારી", "ચિંતા",
        "dar", "bhay", "chinta",
        # Odia
        "ଭୟ", "ଡର", "କାନ୍ଦ", "ଚିନ୍ତା",
        "bhaya", "dara", "chinta"
    ],
    "isolation_hopelessness": [
        # English
        "isolated", "alone", "no help", "no one", "abandoned", "hopeless", "no hope", "helpless", "boycotted", "thrown out",
        # Telugu
        "ఒంటరి", "ఎవరూ లేరు", "సహాయం లేదు", "ఊరి నుంచి వెలివేశారు", "ఆశ లేదు",
        "ontari", "evaru leru", "sahayam ledu", "oori nunchi velivesharu", "aasha ledu",
        # Hindi
        "अकेला", "कोई नहीं", "मदद नहीं", "गांव से निकाला", "निराश", "बेबस",
        "akela", "koi nahi", "madad nahi", "gaon se nikala", "nirash", "bebas",
        # Tamil
        "தனியாக", "உதவி இல்லை", "ஒதுக்கி வைத்தனர்", "நம்பிக்கையற்ற",
        "thaniyaga", "udavi illai",
        # Kannada
        "ಒಂಟಿ", "ಯಾರೂ ಇಲ್ಲ", "ಸಹಾಯವಿಲ್ಲ", "ಊರಿಂದ ಬಹಿಷ್ಕಾರ",
        "onti", "yaaru illa",
        # Malayalam
        "ഒറ്റയ്ക്ക്", "സഹായമില്ല", "നാട്ടിൽ നിന്ന് പുറത്താക്കി",
        "ottaykku", "sahayamilla",
        # Marathi
        "एकटा", "कोणी नाही", "मदत नाही", "गावातून बहिष्कृत", "लाचार",
        "ekta", "koni nahi", "madat nahi",
        # Bengali
        "একাকী", "কেউ নেই", "সাহায্য নেই", "গ্রাম থেকে বিতাড়িত",
        "ekaki", "keu nei", "sahajjo nei",
        # Gujarati
        "એકલા", "કોઈ નથી", "મદદ નથી", "ગામમાંથી કાઢી મૂક્યા",
        "ekla", "koi nathi", "madad nathi",
        # Odia
        "ଏକା", "କେହି ନାହାନ୍ତି", "ସାହାଯ୍ୟ ନାହିଁ", "ଗାଁରୁ ବାସନ୍ଦ",
        "eka", "kehi nahanti"
    ],
    "immediate_danger_self_harm": [
        # English
        "suicide", "kill myself", "end my life", "die", "poison", "they are coming now", "outside my house", "they will kill us tonight", "emergency", "save us now",
        # Telugu
        "చనిపోతాను", "ఆత్మహత్య", "ఇంటి ముందు ఉన్నారు", "ఇప్పుడే చంపేస్తారు", "కాపాడండి",
        "chanipothanu", "aathmahathya", "inti mundu unnaru", "ippude champestharu", "kaapadandi",
        # Hindi
        "जान दे दूंगा", "आत्महत्या", "घर के बाहर खड़े हैं", "बचाओ", "अभी मार देंगे",
        "jaan de doonga", "aatmhatya", "ghar ke bahar khade hain", "bachao", "abhi maar denge",
        # Tamil
        "தற்கொலை", "உயிரை விடுவேன்", "வீட்டுக்கு வெளியே உள்ளனர்", "காப்பாற்றுங்கள்",
        "tharkolai", "kaappaatrrungal",
        # Kannada
        "ಆತ್ಮಹತ್ಯೆ", "ಸಾಯುತ್ತೇನೆ", "ಮನೆ ಮುಂದೆ ಇದ್ದಾರೆ", "ಕಾಪಾಡಿ",
        "aathmahatye", "sayuttene", "kaapaadi",
        # Malayalam
        "ആത്മഹത്യ", "മരിക്കും", "വീടിനു പുറത്തുണ്ട്", "രക്ഷിക്കൂ",
        "aathmahatya", "rakshikku",
        # Marathi
        "आत्महत्या", "जीव देईन", "घराबाहेर उभे आहेत", "वाचवा",
        "aatmhatya", "jeev deen", "vachva",
        # Bengali
        "আত্মহত্যা", "বাঁচাও", "মরে যাব", "ঘরের বাইরে দাঁড়িয়ে আছে",
        "aatmohotya", "baanchao", "more jaabo",
        # Gujarati
        "આત્મહત્યા", "બચાવો", "ઘરની બહાર ઊભા છે",
        "aatmhatya", "bachavo",
        # Odia
        "ଆତ୍ମହତ୍ୟା", "ବଞ୍ଚାଅ", "ଘର ବାହାରେ ଠିଆ ହୋଇଛନ୍ତି",
        "aatmahatya", "bancha"
    ]
}

LANGUAGE_DETECT_MAP = {
    "తెలుగు": "Telugu",
    "చంపు": "Telugu",
    "భయం": "Telugu",
    "హిందీ": "Hindi",
    "मार": "Hindi",
    "धमकी": "Hindi",
    "தமிழ்": "Tamil",
    "மிரட்டல்": "Tamil",
    "ಕನ್ನಡ": "Kannada",
    "ದಾಳಿ": "Kannada",
    "മലയാളം": "Malayalam",
    "ഭീഷണി": "Malayalam",
    "मराठी": "Marathi",
    "हल्ला": "Marathi",
    "বাংলা": "Bengali",
    "হুমকি": "Bengali",
    "ગુજરાતી": "Gujarati",
    "ધમકી": "Gujarati",
    "ଓଡ଼ିଆ": "Odia",
    "ଧମକ": "Odia",
}

class NLPAnalyzerService:
    """
    Multilingual NLP Assessment Service.
    Detects semantic indicators of trauma, fear, threat, intimidation, and isolation.
    """

    @classmethod
    def detect_language(cls, text: str, fallback_lang: str = "Telugu") -> str:
        """
        Lightweight script & keyword-based language detection for Indian languages.
        """
        if not text:
            return fallback_lang
            
        # Check script ranges
        for char in text:
            code = ord(char)
            if 0x0C00 <= code <= 0x0C7F:
                return "Telugu"
            elif 0x0900 <= code <= 0x097F:
                # Could be Hindi or Marathi, check specific Marathi markers or default Hindi
                if any(m in text for m in ["आहे", "होता", "नाही", "मारहाण", "घाबरलो"]):
                    return "Marathi"
                return "Hindi"
            elif 0x0B80 <= code <= 0x0BFF:
                return "Tamil"
            elif 0x0C80 <= code <= 0x0CFF:
                return "Kannada"
            elif 0x0D00 <= code <= 0x0D7F:
                return "Malayalam"
            elif 0x0980 <= code <= 0x09FF:
                return "Bengali"
            elif 0x0A80 <= code <= 0x0AFF:
                return "Gujarati"
            elif 0x0B00 <= code <= 0x0B7F:
                return "Odia"

        # Check transliterated/phonetic cues
        lower_t = text.lower()
        if any(w in lower_t for w in ["champutham", "kottaru", "bediristunnaru", "bhayanga"]):
            return "Telugu"
        elif any(w in lower_t for w in ["dhamki", "hamla", "ghabrahat", "bachao"]):
            return "Hindi"
        elif any(w in lower_t for w in ["mirattal", "bayam", "kaappaatrrungal"]):
            return "Tamil"
        elif any(w in lower_t for w in ["bedarike", "aatanka", "hodedaru"]):
            return "Kannada"

        return fallback_lang or "English"

    @classmethod
    def analyze_text(cls, text: str, specified_language: Optional[str] = None) -> Tuple[NLPMetrics, EmotionMetrics]:
        """
        Analyzes narrative text across distress, threat, emotional, and safety dimensions.
        """
        cleaned_text = (text or "").strip()
        lang = specified_language if specified_language and specified_language != "Auto Detect Language" else cls.detect_language(cleaned_text)
        lower_text = cleaned_text.lower()

        matched_threat = []
        matched_fear = []
        matched_isolation = []
        matched_danger = []

        # Find matches
        for kw in LANGUAGE_LEXICON["threat"]:
            if kw in cleaned_text or kw in lower_text:
                matched_threat.append(kw)

        for kw in LANGUAGE_LEXICON["fear_anxiety"]:
            if kw in cleaned_text or kw in lower_text:
                matched_fear.append(kw)

        for kw in LANGUAGE_LEXICON["isolation_hopelessness"]:
            if kw in cleaned_text or kw in lower_text:
                matched_isolation.append(kw)

        for kw in LANGUAGE_LEXICON["immediate_danger_self_harm"]:
            if kw in cleaned_text or kw in lower_text:
                matched_danger.append(kw)

        # Calculate dimension scores (0 to 100)
        threat_score = min(100.0, len(matched_threat) * 28.0)
        fear_score = min(100.0, len(matched_fear) * 25.0)
        isolation_score = min(100.0, len(matched_isolation) * 30.0)
        anxiety_score = min(100.0, (fear_score * 0.7) + (threat_score * 0.3))
        distress_score = min(100.0, (fear_score * 0.4) + (threat_score * 0.4) + (isolation_score * 0.3))
        vulnerability_score = min(100.0, (isolation_score * 0.5) + (threat_score * 0.35) + (fear_score * 0.25))

        has_danger = len(matched_danger) > 0
        has_self_harm = any(term in lower_text or term in cleaned_text for term in ["suicide", "kill myself", "end my life", "ఆత్మహత్య", "आत्महत्या", "തற்கொலை"])

        if has_danger:
            threat_score = max(threat_score, 88.0)
            fear_score = max(fear_score, 85.0)
            distress_score = max(distress_score, 90.0)

        all_keywords = list(set(matched_threat + matched_fear + matched_isolation + matched_danger))

        nlp_metrics = NLPMetrics(
            detected_language=lang,
            fear_score=round(fear_score, 1),
            anxiety_score=round(anxiety_score, 1),
            threat_intimidation_score=round(threat_score, 1),
            severe_distress_score=round(distress_score, 1),
            hopelessness_score=round(isolation_score * 0.9, 1),
            social_isolation_score=round(isolation_score, 1),
            emotional_shock_score=round(min(100.0, distress_score * 0.85), 1),
            vulnerability_score=round(vulnerability_score, 1),
            self_harm_ideation=has_self_harm,
            immediate_danger_detected=has_danger,
            keywords_matched=all_keywords[:8]
        )

        # Emotion Analysis Model Simulation
        # Scales normalized from 0.0 to 1.0
        fear_norm = min(1.0, fear_score / 100.0)
        distress_norm = min(1.0, distress_score / 100.0)
        anger_norm = min(1.0, (threat_score * 0.4) / 100.0)
        sadness_norm = min(1.0, (isolation_score * 0.8) / 100.0)
        anxiety_norm = min(1.0, anxiety_score / 100.0)
        confusion_norm = 0.35 if len(cleaned_text) < 40 and fear_norm > 0.4 else 0.15
        calm_norm = max(0.05, 1.0 - max(fear_norm, distress_norm, anger_norm))
        neutral_norm = 0.6 if (fear_norm < 0.2 and distress_norm < 0.2) else 0.1

        emotions = {
            "Fear": fear_norm,
            "Distress": distress_norm,
            "Anxiety": anxiety_norm,
            "Sadness": sadness_norm,
            "Anger": anger_norm,
            "Confusion": confusion_norm,
            "Calm": calm_norm,
            "Neutral": neutral_norm
        }
        dominant_emotion = max(emotions, key=emotions.get)
        confidence = 0.88 if len(cleaned_text) > 50 else (0.68 if len(cleaned_text) < 20 else 0.78)

        emotion_metrics = EmotionMetrics(
            fear=round(fear_norm, 2),
            sadness=round(sadness_norm, 2),
            anger=round(anger_norm, 2),
            distress=round(distress_norm, 2),
            anxiety=round(anxiety_norm, 2),
            confusion=round(confusion_norm, 2),
            neutral=round(neutral_norm, 2),
            calm=round(calm_norm, 2),
            dominant_emotion=dominant_emotion,
            confidence=round(confidence, 2)
        )

        return nlp_metrics, emotion_metrics
