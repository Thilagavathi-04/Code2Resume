import { create } from 'zustand';

export const useUserStore = create((set) => ({
  userData: null,
  repos: [],
  setUserData: (data) => set({ userData: data }),
  setRepos: (repos) => set({ repos }),
}));
