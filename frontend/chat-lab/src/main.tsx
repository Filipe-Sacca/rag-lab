import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.tsx'
import AnalyticsDashboard from './pages/AnalyticsDashboard.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/analytics" element={<AnalyticsDashboard />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
