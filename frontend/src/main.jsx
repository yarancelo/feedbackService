import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Admin from './pages/Admin/index.jsx'
import FeedbackForm from './pages/FeedbackForm.jsx'
import Wall from './pages/Wall.jsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Wall />} />
        <Route path="/wall" element={<Wall />} />
        <Route path="/submit" element={<FeedbackForm />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
