// static_site/track.js
fetch("https://automatic-journey-xx7xvp79qrpfpr5p-8000.app.github.dev/track", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    url: window.location.href,
    userAgent: navigator.userAgent,
    time: new Date().toISOString()
  })
})
.then(res => res.json())
.then(data => console.log("Tracking sent", data))
.catch(err => console.error("Tracking error", err));
  