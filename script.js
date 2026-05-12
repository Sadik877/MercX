function checkURL() {
  const url = document.getElementById("urlInput").value;

  const suspiciousWords = [
    "free-money",
    "verify-now",
    "crypto-fast",
    "login-free",
    "gift-card",
    "win-cash"
  ];

  let isSuspicious = false;

  suspiciousWords.forEach(word => {
    if (url.includes(word)) {
      isSuspicious = true;
    }
  });

  const result = document.getElementById("result");

  if (isSuspicious) {
    result.innerHTML = "⚠️ Suspicious Link Detected";
    result.style.color = "red";
  } else {
    result.innerHTML = "✅ Link Appears Safe";
    result.style.color = "lightgreen";
  }
}