// UI state store (Zustand)

import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;

  // Modal states
  newProjectModalVisible: boolean;
  setNewProjectModalVisible: (visible: boolean) => void;

  newExperimentModalVisible: boolean;
  setNewExperimentModalVisible: (visible: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  newProjectModalVisible: false,
  setNewProjectModalVisible: (visible) => set({ newProjectModalVisible: visible }),

  newExperimentModalVisible: false,
  setNewExperimentModalVisible: (visible) => set({ newExperimentModalVisible: visible }),
}));
