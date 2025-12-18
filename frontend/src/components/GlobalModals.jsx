import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal, Button, Spinner } from 'react-bootstrap';

import { useAuthStore, useModalStore } from "@src/scripts/state";
import { logout } from "@src/scripts/api";


function LogoutModal() {
	const navigate = useNavigate();
	const { logoutModal, hideLogoutModal } = useModalStore();
	const { token, clearAuth } = useAuthStore();
	const [loading, setLoading] = React.useState(false);

	const handleLogout = async () => {
		setLoading(true);
		try {
			await logout(token);
			clearAuth();
			hideLogoutModal();
			navigate('/login');
		} catch (error) {
			console.error(error);
			clearAuth();
			hideLogoutModal();
			navigate('/login');
		}
	};

	return (
		<Modal show={logoutModal} onHide={hideLogoutModal}>
			<Modal.Header closeButton>
				<Modal.Title>Confirm Logout</Modal.Title>
			</Modal.Header>
			<Modal.Body>Are you sure you want to log out?</Modal.Body>
			<Modal.Footer>
				<Button variant="secondary" onClick={hideLogoutModal} disabled={loading}>
					Cancel
				</Button>
				<Button variant="danger" onClick={handleLogout} disabled={loading}>
					{loading ? <Spinner size="sm" animation="border" /> : 'Logout'}
				</Button>
			</Modal.Footer>
		</Modal>
	);
}


function CancelModal({ onConfirm }) {
	const { cancelModal, hideCancelModal } = useModalStore();
	const [loading, setLoading] = React.useState(false);

	const handleConfirm = async () => {
		setLoading(true);
		await onConfirm();
		setLoading(false);
		hideCancelModal();
	};

	return (
		<Modal show={cancelModal} onHide={hideCancelModal}>
			<Modal.Header closeButton>
				<Modal.Title>Cancel Scheduling</Modal.Title>
			</Modal.Header>
			<Modal.Body>Are you sure you want to cancel this scheduling?</Modal.Body>
			<Modal.Footer>
				<Button variant="secondary" onClick={hideCancelModal} disabled={loading}>
					No
				</Button>
				<Button variant="danger" onClick={handleConfirm} disabled={loading}>
					{loading ? <Spinner size="sm" animation="border" /> : 'Yes, Cancel'}
				</Button>
			</Modal.Footer>
		</Modal>
	);
}


function DeleteModal({ onConfirm }) {
	const { deleteModal, hideDeleteModal } = useModalStore();
	const [loading, setLoading] = React.useState(false);

	const handleConfirm = async () => {
		setLoading(true);
		await onConfirm();
		setLoading(false);
		hideDeleteModal();
	};

	return (
		<Modal show={deleteModal} onHide={hideDeleteModal}>
			<Modal.Header closeButton>
				<Modal.Title>Delete Scheduling</Modal.Title>
			</Modal.Header>
			<Modal.Body>Are you sure you want to delete this scheduling?</Modal.Body>
			<Modal.Footer>
				<Button variant="secondary" onClick={hideDeleteModal} disabled={loading}>
					No
				</Button>
				<Button variant="danger" onClick={handleConfirm} disabled={loading}>
					{loading ? <Spinner size="sm" animation="border" /> : 'Yes, Delete'}
				</Button>
			</Modal.Footer>
		</Modal>
	);
}


export { LogoutModal, CancelModal, DeleteModal };