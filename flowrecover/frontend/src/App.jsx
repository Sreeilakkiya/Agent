import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Leaks from './pages/Leaks'
import Prevention from './pages/Prevention'
import Recovery from './pages/Recovery'
import Customers from './pages/Customers'
import CustomerDetail from './pages/CustomerDetail'
import Upload from './pages/Upload'
import Layout from './layouts/Layout'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="leaks" element={<Leaks />} />
          <Route path="prevention" element={<Prevention />} />
          <Route path="recovery" element={<Recovery />} />
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:id" element={<CustomerDetail />} />
          <Route path="upload" element={<Upload />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
