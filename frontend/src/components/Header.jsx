import { Navbar, Container, Button } from 'react-bootstrap';

import { useAuthStore, useModalStore } from "@src/scripts/state";


function Header() {
	const { token } = useAuthStore();
	const { showLogoutModal } = useModalStore();


	return (
		<Navbar bg="light" className="mb-4">
			<Container>
				<Navbar.Brand href="/">Schedle</Navbar.Brand>
				{token && (
					<Button variant="outline-danger" onClick={showLogoutModal}>
						Logout
					</Button>
				)}
			</Container>
		</Navbar>
	);
}


export { Header };