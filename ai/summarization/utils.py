import spacy

try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

def summarize_text(text):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return ' '.join(sentences[:2])