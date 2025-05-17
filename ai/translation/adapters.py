from googletrans import Translator

def translate_text(text, target_lang='es'):
    """
    Translate text to the target language using googletrans.
    """
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to original text