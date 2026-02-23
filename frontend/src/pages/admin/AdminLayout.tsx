import { Outlet, NavLink } from 'react-router-dom'
import { FileType, Layers } from 'lucide-react'
import './AdminLayout.css'

export default function AdminLayout() {
  return (
    <div className="admin-layout">
      <div className="admin-header">
        <div>
          <h1 className="page-title">Admin Panel</h1>
          <p className="page-sub">Manage document types, templates, and extraction entities</p>
        </div>
      </div>
      <div className="admin-tabs">
       
        <NavLink to="/admin/templates" className={({ isActive }) => `admin-tab ${isActive ? 'active' : ''}`}>
          <Layers size={15} /> Templates & Entities
        </NavLink>
      </div>
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  )
}
