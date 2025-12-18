import { create } from 'zustand';


const useAuthStore = create((set) => ({
	token: localStorage.getItem('token'),
	user: JSON.parse(localStorage.getItem('user') || 'null'),
	
	setAuth: (token, user) => {
		localStorage.setItem('token', token);
		localStorage.setItem('user', JSON.stringify(user));
		set({ token, user });
	},
	
	clearAuth: () => {
		localStorage.removeItem('token');
		localStorage.removeItem('user');
		set({ token: null, user: null });
	},
}));


const useModalStore = create((set) => ({
	logoutModal: false,
	cancelModal: false,
	deleteModal: false,
	targetId: null,
	
	showLogoutModal: () => set({ logoutModal: true }),
	hideLogoutModal: () => set({ logoutModal: false }),
	
	showCancelModal: (id) => set({ cancelModal: true, targetId: id }),
	hideCancelModal: () => set({ cancelModal: false, targetId: null }),
	
	showDeleteModal: (id) => set({ deleteModal: true, targetId: id }),
	hideDeleteModal: () => set({ deleteModal: false, targetId: null }),
}));


export { useAuthStore, useModalStore };