// Function to initialize the reading aloud functionality
function initializeReadAloud() {
    document.addEventListener('mouseup', function(event) {
        var selectedText = getSelectedText();
        if (selectedText) {
            readText(selectedText);
        }
    });
}

// Function to get the selected text on the webpage
function getSelectedText() {
    var selectedText = '';
    if (window.getSelection) {
        selectedText = window.getSelection().toString();
    } else if (document.selection && document.selection.type != 'Control') {
        selectedText = document.selection.createRange().text;
    }
    return selectedText.trim();
}

// Function to read the given text aloud
function readText(text) {
    var speech = new SpeechSynthesisUtterance();
    speech.lang = 'en-US'; // Set the language
    speech.text = text; // Set the text to be read
    speech.volume = 1; // Set the volume (0 to 1)
    speech.rate = 1; // Set the rate (0.1 to 10)
    speech.pitch = 1; // Set the pitch (0 to 2)
    window.speechSynthesis.speak(speech); // Speak the text
}

// Call the initialization function when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeReadAloud();
});