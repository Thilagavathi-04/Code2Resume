import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useThemeStore = create(
  persist(
    (set, get) => ({
      isDark: typeof window !== 'undefined' 
        ? document.documentElement.classList.contains('dark')
        : false,
      toggle: () => {
        const newIsDark = !get().isDark;
        set({ isDark: newIsDark });
        if (newIsDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
      setDark: (isDark) => {
        set({ isDark });
        if (isDark) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state?.isDark) {
          document.documentElement.classList.add('dark');
        }
      },
    }
  )
);
