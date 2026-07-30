import React from "react";
import ReactDOM from "react-dom/client";
import { PopupPage } from "./PopupPage";
import { ErrorBoundary } from "../utils/errorBoundary";
import "../styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <PopupPage />
    </ErrorBoundary>
  </React.StrictMode>
);
