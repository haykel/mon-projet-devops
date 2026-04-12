import { BrowserRouter, Routes, Route } from "react-router-dom";
import KeycloakProvider from "./components/KeycloakProvider";
import Home from "./pages/Home";
import Stock from "./pages/Stock";

function App() {
  return (
    <KeycloakProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/stock/:ticker" element={<Stock />} />
        </Routes>
      </BrowserRouter>
    </KeycloakProvider>
  );
}

export default App;
