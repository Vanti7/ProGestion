import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './pages/App'
import OAuthCallback from './pages/OAuthCallback'
import Dashboard from './pages/Dashboard'
import Ideation from './pages/Ideation'
import ProtectedRoute from './components/ProtectedRoute'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './styles.css'
import PublicPortfolio from './pages/PublicPortfolio'

const root = createRoot(document.getElementById('root')!)
root.render(
	<React.StrictMode>
		<BrowserRouter>
			<Routes>
				<Route path="/" element={<App />} />
				<Route path="/oauth/callback" element={<OAuthCallback />} />
				<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
				<Route path="/ideation" element={<ProtectedRoute><Ideation /></ProtectedRoute>} />
				<Route path="/user/:username" element={<PublicPortfolio />} />
			</Routes>
		</BrowserRouter>
	</React.StrictMode>
)

