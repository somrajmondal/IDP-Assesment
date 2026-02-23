import { create } from 'zustand'

interface AppStore {
  selectedFolder: number | null
  selectedFile: number | null
  setSelectedFolder: (id: number | null) => void
  setSelectedFile: (id: number | null) => void
}

export const useAppStore = create<AppStore>((set) => ({
  selectedFolder: null,
  selectedFile: null,
  setSelectedFolder: (id) => set({ selectedFolder: id, selectedFile: null }),
  setSelectedFile: (id) => set({ selectedFile: id }),
}))
