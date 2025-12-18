import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Spinner, Button, Alert, Table } from 'react-bootstrap';

import { CancelModal, DeleteModal } from '@src/components/GlobalModals';
import { useAuthStore, useModalStore } from "@src/scripts/state";
import { getSchedulings, deleteScheduling } from "@src/scripts/api";


function SchedulingsPage() {
	const navigate = useNavigate();
	const { token } = useAuthStore();
	const { showCancelModal, showDeleteModal, targetId } = useModalStore();
	
	const [schedulings, setSchedulings] = React.useState([]);
	const [loading, setLoading] = React.useState(true);
	const [error, setError] = React.useState('');


	const fetchSchedulings = async () => {
		setLoading(true);
		try {
			const data = await getSchedulings(token);
			setSchedulings(data);
			setError('');
		} catch (err) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchSchedulings();
	}, []);

	const handleCancel = async () => {
		try {
			await deleteScheduling(token, targetId);
			fetchSchedulings();
		} catch (err) {
			setError(err.message);
		}
	};

	const handleDelete = async () => {
		try {
			await deleteScheduling(token, targetId);
			fetchSchedulings();
		} catch (err) {
			setError(err.message);
		}
	};

	const getStatusBadge = (status) => {
		if (status === 'completed') return <span className="badge bg-success">Completed</span>;
		if (status === 'in_progress') return <span className="badge bg-primary">In Progress</span>;
		if (status === 'cancelled') return <span className="badge bg-secondary">Cancelled</span>;
		return <span className="badge bg-warning">Pending</span>;
	};

	
	return (
		<Container className="mt-4">
			<div className="d-flex justify-content-between align-items-center mb-4">
				<h2>My Schedulings</h2>
				<Button variant="primary" onClick={() => navigate('/schedulings/new')}>
					Start new scheduling
				</Button>
			</div>

			{error && <Alert variant="danger">{error}</Alert>}

			{loading ? (
				<div className="text-center">
					<Spinner animation="border" />
				</div>
			) : schedulings.length === 0 ? (
				<Alert variant="info">No schedulings yet. Start a new one!</Alert>
			) : (
				<Table striped bordered hover>
					<thead>
						<tr>
							<th>Name</th>
							<th>Status</th>
							<th>Created</th>
							<th>Actions</th>
						</tr>
					</thead>
					<tbody>
						{schedulings.map((sched) => (
							<tr key={sched.id}>
								<td>
									{sched.status === 'completed' ? (
										<a 
											href={`/schedulings/${sched.id}`} 
											onClick={(e) => { e.preventDefault(); navigate(`/schedulings/${sched.id}`); }}
											style={{ cursor: 'pointer', textDecoration: 'none' }}
										>
											{sched.name}
										</a>
									) : (
										sched.name
									)}
								</td>
								<td>{getStatusBadge(sched.status)}</td>
								<td>{new Date(sched.created_at).toLocaleString()}</td>
								<td>
									{sched.status === 'in_progress' && (
										<Button 
											variant="warning" 
											size="sm"
											onClick={() => showCancelModal(sched.id)}
										>
											Cancel
										</Button>
									)}
									{sched.status === 'completed' && (
										<Button 
											variant="danger" 
											size="sm"
											onClick={() => showDeleteModal(sched.id)}
										>
											Delete
										</Button>
									)}
								</td>
							</tr>
						))}
					</tbody>
				</Table>
			)}

			<CancelModal onConfirm={handleCancel} />
			<DeleteModal onConfirm={handleDelete} />
		</Container>
	);
}


export { SchedulingsPage };