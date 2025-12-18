import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Form, Button, Spinner, Alert } from 'react-bootstrap';

import { useAuthStore } from "@src/scripts/state";
import { login } from "@src/scripts/api";


function LoginPage() {
	const navigate = useNavigate();
	const { setAuth } = useAuthStore();
	const [email, setEmail] = React.useState('');
	const [password, setPassword] = React.useState('');
	const [error, setError] = React.useState('');
	const [loading, setLoading] = React.useState(false);


	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');
		setLoading(true);

		try {
			const data = await login({ email, password });
			setAuth(data.token, data.user);
			navigate('/schedulings');
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	
	return (
		<Container className="mt-5" style={{ maxWidth: '400px' }}>
			<h2 className="mb-4">Login</h2>
			{error && <Alert variant="danger">{error}</Alert>}
			<Form onSubmit={handleSubmit}>
				<Form.Group className="mb-3">
					<Form.Label>Email</Form.Label>
					<Form.Control
						type="email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						required
					/>
				</Form.Group>
				<Form.Group className="mb-3">
					<Form.Label>Password</Form.Label>
					<Form.Control
						type="password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
				</Form.Group>
				<Button variant="primary" type="submit" className="w-100" disabled={loading}>
					{loading ? <Spinner size="sm" animation="border" /> : 'Log in'}
				</Button>
			</Form>
			<p className="mt-3 text-center">
				Don't have an account yet?{' '}
				<a href="/register" onClick={(e) => { e.preventDefault(); navigate('/register'); }}>
					Register
				</a>
			</p>
		</Container>
	);
}


export { LoginPage };