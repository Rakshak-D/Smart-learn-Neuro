function startSTT() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.start();
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const responseText = document.getElementById('response_text');
        responseText.value = transcript;
        responseText.focus();
    };
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };
}