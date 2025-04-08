fetch("http://localhost:8000/track", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      page: window.location.pathname,
      referrer: document.referrer,
      userAgent: navigator.userAgent,
      screenWidth: screen.width,
      screenHeight: screen.height,
      timestamp: new Date().toISOString()
    })
  });
  