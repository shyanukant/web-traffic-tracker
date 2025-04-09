// window.addEventListener("DOMContentLoaded", () => {
//   fetch("http://127.0.0.1:8000/track", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({
//       userAgent: navigator.userAgent,
//       screen: `${window.screen.width}x${window.screen.height}`,
//       url: window.location.href,
//       referrer: document.referrer,
//       time: new Date().toISOString(),
//       site: window.location.hostname  // auto detect site,
//     }),
//   })
//     .then((res) => res.json())
//     .then((data) => console.log("Tracked ✅", data))
//     .catch((err) => console.error("Tracking failed ❌", err));
// });

window.addEventListener("DOMContentLoaded", () => {
  const payload = {
    site: window.location.hostname, // must match what you used in /register
    userAgent: navigator.userAgent,
    url: window.location.href,
    referrer: document.referrer,
    screen: `${window.screen.width}x${window.screen.height}`
  };

  console.log("📡 Sending tracking data", payload);

  fetch("http://127.0.0.1:8000/track", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  .then((res) => res.json())
  .then((data) => console.log("✅ Tracked:", data))
  .catch((err) => console.error("❌ Error:", err));
});