import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import Layout from './components/common/Layout'
import Dashboard from './pages/Dashboard'
import FolderDetail from './pages/FolderDetail'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDocumentTypes from './pages/admin/AdminDocumentTypes'
import AdminTemplates from './pages/admin/AdminTemplates'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 30000 } }
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster position="top-right" toastOptions={{
          style: { background: '#1a1a2e', color: '#e0e0ff', border: '1px solid #3d3d6b' }
        }} />
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="folder/:folderId" element={<FolderDetail />} />
            <Route path="admin" element={<AdminLayout />}>
              <Route index element={<AdminDocumentTypes />} />
              <Route path="templates" element={<AdminTemplates />} />
              <Route path="templates/:docTypeId" element={<AdminTemplates />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
