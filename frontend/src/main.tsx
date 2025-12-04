import React from "react";
import { createRoot } from "react-dom/client";
import App from "./app/App";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import "./styles/styles.css";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#3b82f6" },
    background: { default: "#0b0f14", paper: "#11161d" },
    text: { primary: "#e5e7eb", secondary: "#9ca3af" },
    divider: "#1f2937",
  },
  shape: { borderRadius: 12 },
  typography: {
    fontFamily:
      "Inter, system-ui, -apple-system, Segoe UI, Arial, sans-serif",
  },
});

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
