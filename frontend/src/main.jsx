// ============================================================
// FILE: frontend/src/main.jsx
// PURPOSE: Entry point — mounts the React app into index.html
// ============================================================

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
// No separate index.css — all styles are in App.css (imported by App.js)

// Find the <div id="root"> in index.html and mount React into it
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {/* StrictMode helps catch bugs during development — no effect in production */}
    <App />
  </React.StrictMode>
);
