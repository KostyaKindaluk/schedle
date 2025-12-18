const baseServerUrl = "http://localhost:8000";


async function register({ email, password }) {
	const res = await fetch(`${baseServerUrl}/api/auth/register`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ email, password }),
	});
	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || error.error || "Registration failed");
	}
	return res.json();
}

async function login({ email, password }) {
	const res = await fetch(`${baseServerUrl}/api/auth/login`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ email, password }),
	});
	if (!res.ok) {
		const error = await res.json();
		throw new Error(error.detail || error.error || "Login failed");
	}
	return res.json();
}

async function logout(token) {
	const res = await fetch(`${baseServerUrl}/api/auth/logout`, {
		method: "POST",
		headers: { 
			"Content-Type": "application/json",
			"Authorization": `Token ${token}`
		},
	});
	if (!res.ok) {
		throw new Error("Logout failed");
	}
	return res.json();
}

async function getSchedulings(token) {
	const res = await fetch(`${baseServerUrl}/api/scheduling/schedulings`, {
		method: "GET",
		headers: { 
			"Authorization": `Token ${token}`
		},
	});
	if (!res.ok) {
		throw new Error("Failed to fetch schedulings");
	}
	return res.json();
}

async function createScheduling(token, data) {
	const res = await fetch(`${baseServerUrl}/api/scheduling/schedulings`, {
		method: "POST",
		headers: { 
			"Content-Type": "application/json",
			"Authorization": `Token ${token}`
		},
		body: JSON.stringify(data),
	});
	if (!res.ok) {
		const error = await res.json();
		throw new Error(JSON.stringify(error));
	}
	return res.json();
}

async function getSchedulingDetail(token, id) {
	const res = await fetch(`${baseServerUrl}/api/scheduling/schedulings/${id}`, {
		method: "GET",
		headers: { 
			"Authorization": `Token ${token}`
		},
	});
	if (!res.ok) {
		throw new Error("Failed to fetch scheduling details");
	}
	return res.json();
}

async function deleteScheduling(token, id) {
	const res = await fetch(`${baseServerUrl}/api/scheduling/schedulings/${id}`, {
		method: "DELETE",
		headers: { 
			"Authorization": `Token ${token}`
		},
	});
	if (!res.ok) {
		throw new Error("Failed to delete scheduling");
	}
}


export { register, login, logout, getSchedulings, createScheduling, getSchedulingDetail, deleteScheduling };