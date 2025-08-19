import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { isAuthenticated } from '../lib/auth'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
	const location = useLocation()
	if (!isAuthenticated()) {
		return <Navigate to="/" state={{ from: location }} replace />
	}
	return <>{children}</>
}

