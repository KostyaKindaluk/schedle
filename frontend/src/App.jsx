import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { Header } from "@src/components/Header";
import { RegisterPage } from "@src/pages/RegisterPage";
import { LoginPage } from "@src/pages/LoginPage";
import { SchedulingsPage } from "@src/pages/SchedulingsPage";
import { NewSchedulingPage } from "@src/pages/NewSchedulingPage";
import { SchedulingDetailPage } from "@src/pages/SchedulingDetailPage";
import { LogoutModal } from "@src/components/GlobalModals";

import { useAuthStore } from "@src/scripts/state";


function ProtectedRoute({ children }) {
	const { token } = useAuthStore();
	return token ? children : <Navigate to="/login" />;
}

function PublicRoute({ children }) {
	const { token } = useAuthStore();
	return !token ? children : <Navigate to="/schedulings" />;
}


function App() {
	return (
		<BrowserRouter>
			<Header />
			<LogoutModal />
			<Routes>
				<Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
				<Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
				<Route path="/schedulings" element={<ProtectedRoute><SchedulingsPage /></ProtectedRoute>} />
				<Route path="/schedulings/new" element={<ProtectedRoute><NewSchedulingPage /></ProtectedRoute>} />
				<Route path="/schedulings/:id" element={<ProtectedRoute><SchedulingDetailPage /></ProtectedRoute>} />
				<Route path="/" element={<Navigate to="/schedulings" />} />
			</Routes>
		</BrowserRouter>
	);
}


export default App;