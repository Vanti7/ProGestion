import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { setToken } from '../lib/auth'

export default function OAuthCallback() {
	const [params] = useSearchParams()
	const navigate = useNavigate()

	useEffect(() => {
		const token = params.get('token')
		if (token) {
			setToken(token)
			navigate('/')
		} else {
			navigate('/')
		}
	}, [params, navigate])

	return <div className="p-6">Traitement de l’authentification…</div>
}

