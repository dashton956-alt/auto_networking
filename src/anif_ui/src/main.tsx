import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <a href="#main-content" className="skip-to-content">
        Skip to main content
      </a>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
