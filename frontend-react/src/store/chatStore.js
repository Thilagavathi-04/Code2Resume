import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useChatStore = create(
  persist(
    (set, get) => ({
      messages: [],
      loading: false,

      addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),

      updateLastAssistantMessage: (updater) =>
        set((state) => {
          const msgs = [...state.messages];
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === 'assistant') {
              msgs[i] = typeof updater === 'function' ? updater(msgs[i]) : { ...msgs[i], ...updater };
              break;
            }
          }
          return { messages: msgs };
        }),

      setLoading: (val) => set({ loading: val }),

      clearMessages: () => set({ messages: [] }),
    }),
    {
      name: 'chat-storage',
    }
  )
);
