function addGoogleTranslateScript() {
    var googleTranslateScript = document.createElement('script');
    googleTranslateScript.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    googleTranslateScript.type = 'text/javascript';
    document.head.appendChild(googleTranslateScript);
}

// Call the function to load Google Translate script asynchronously
addGoogleTranslateScript();