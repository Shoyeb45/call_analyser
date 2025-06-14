import logging.config
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO
from elevenlabs.client import ElevenLabs
import os
import logging
from app.utils.audio import tokenize_content, convert_to_wav, summarise_text, analyze_emotions, abusive_words_analyse

# Create and configure logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

text = "हैलो। यस। सर वेरी गुड मॉर्निंग। मैं हमसे दिव्या बात कर रही हूं पीएनबी से। अरे दिव्या, कैसी हैं आप? बहुत दिन बाद फोन किया। क्या हाल-चाल है? बढ़िया, सर आप बताइए। हम बहुत बढ़िया। लंच-वंच हुआ कि नहीं? सर इंग्वेस्टमेंट बैंक के रिगार्डिंग कॉल किया गया है। अबे छोड़ो, पहले बताओ लंच-वंच हुआ? पहले ये देखो पेट पूजा होनी चाहिए, पहले कुछ बढ़िया खाना-पीना होना चाहिए। काम नाम तो चलता रहेगा दिव्या। काम नाम तो जिंदगी भर-- अब एक बात सोचो कितने साल से काम कर रही हो? दो चार साल? चार साल। तो चार साल में काम खत्म हुआ? नहीं, अगले चालीस साल भी खत्म नहीं होगा यार। अबे छुट्टी लो, घर जाओ, भाई बहन परिवार के साथ मौज मस्ती करो। एक काम नाम जिंदगी उसके लिए थोड़े पैदा हुए हैं हम लोग, ठीक है? शादी हुई कि नहीं तुम्हारी? नहीं सर। अरे करो यार जिन चीजों में जिंदगी है उसको तुम लोग करते नहीं हो। खुद की भी जिंदगी फंसा रखी है, लोगों की भी जिंदगी फंसा के रखते हो। शादी ब्याह करो, कुछ घर बर बसाओ। मां बाप को खुशियां दो, सुख दो। ये कहां ये काम नाम, मतलब क्या? दिव्या मैं तो समझता था कि तुम थोड़ी समझदार हो। ओके सर, थैंक यू सो मच। मोस्ट वेलकम।"

text2 = "सर, अभी जस्ट आए हैं। डेमो से निकला ही था। साले इतना गांड फाड़ दूंगा न तेरी मैं। तेरे को अकल है काम करने की कि नहीं है? अकल है तेरे में? हाँ सर। तेरे को कितने बजे बोले थे मैंने कॉल करने के लिए मेरे को? सर उसके बाद से दो बैक टू बैक डेमो में था। अबे इतना मारूंगा न मैं सही बता रहा हूं मेरा दिमाग मत खराब कर साले! तू कितने बजे डेमो से निकला है? डेमो से निकलकर कॉल करेगा मेरे को कि नहीं करेगा? हां सर, हां सर। सिर! मैं कॉल करूंगा क्या तेरे को रेको थरे के अल्फा जेट? नहीं नहीं सर अभी करने ही वाला था मैं। बस खाना खाकर मतलब अभी... कहां पर खाना खा रखा था तूने भाई देख! चूल गया है क्या तू? सॉरी सर वो करने ही वाले थे... हेलो। कहां पर हो? सर अभी रूम पर ही हूं। कैब वगैरह कुछ नहीं हो रही थी। कौन से रूम पर हो? मैं यहां पर हूं सर पंचशील कॉलोनी। मतलब किसके रूम पे हो? अपने रूम पे हो? हां सर। तू भोसड़ी के जब बोला था ना ऑफिस आने के लिए डायरेक्ट ऑफिस क्यों नहीं आया? सर डायरेक्ट ऑफिस, सर वो फॉर्मल्स मेरे गंदे थे, मेरे पास कुछ नहीं था तो मैं वो भिगोने आया था कि मतलब भिगो दूंगा फिर... क्या भिगवाएगा भोसड़ी क्या तुम्हारी? समझ नहीं आ रहा तुम्हें? फॉर्मल भिगोने क्या क्या भेंचोद! नहीं सर मतलब कुछ खाया भी नहीं था वो खाने से पहले। मारे तो सूखा नहीं मेरे मुखे रेजम लगा दे। साले तेरा रेजिग्नेशन लेटर भी टाइप करके डालूंगा मैं। पेक कर देख ला सामने आते है। छठे वीक से जीरो बैठा है भेंचोद! साला जॉब आना चाय पीने जाता क्या? सुबह रेजिग्नेशन लेटर मैं टाइप करके भेज रहा हूं बेचारे..."

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET"])
# def index():
#     return render_template("index.html")

@app.route("/api/upload", methods=["GET", "POST"])
def analyse_audio():
    logging.info("Audio analyse function called")
    try:
        if 'audio_file' not in request.files:
            logging.error("Audio file not found")
            return jsonify({
                "success": False,
                'message': 'No file provided'
                }), 400
        
        audio_file = request.files["audio_file"]
        
        
        # get secure filename
        filename = secure_filename(audio_file.filename) # type: ignore
        
        # rename the file and temporarily save the file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(file_path)
        
        wav_path = file_path.rsplit(".", 1)[0] + ".wav"
        convert_to_wav(file_path, wav_path)
        
        with open(wav_path, "rb") as f:
            audio_bytes = BytesIO(f.read())
        
        elevenlabs = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )
        audio_data = audio_bytes.getvalue()
        
        logging.info("Converting audio into transcription.")
        transcription = elevenlabs.speech_to_text.convert(
            file=audio_data,
            model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=False, # Tag audio events like laughter, applause, etc.
            language_code="hi", # Language of the audio file. If set to None, the model will detect the language automatically.
            # diarize=True, # Whether to annotate who is speaking
        )
        
        text = transcription.text
        words = transcription.words

        summary, sentiment, abusive_words = summarise_text(text)

        abusive_words = abusive_words_analyse(abusive_words, words)
        
        return jsonify({    
            "transcription": text,
            "summary": summary,
            "sentiment": sentiment,
            "abusive_words": abusive_words,
            "success": True
        })
        
    except Exception as e:
        logging.error(f"Failed to analyse the video, error message: {str(e)}")
        return jsonify({
            "success" : False,
            "message": f"Error while analysing the audio, error: {str(e)}"
      
        })


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    # summarise_text(text2)
    app.run()