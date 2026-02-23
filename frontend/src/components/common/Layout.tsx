import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Settings, FolderOpen, ChevronRight } from 'lucide-react'
import './Layout.css'

export default function Layout() {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <FolderOpen size={20} />
          </div>
          <div>
            <div className="logo-title">IDP</div>
            <div className="logo-sub">AI Digitization</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Processing</div>
          <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={16} />
            Dashboard
          </NavLink>

          <div className="nav-section-label" style={{ marginTop: 24 }}>Configuration</div>
    
          <NavLink to="/admin/templates" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <ChevronRight size={16} />
            Templates & Entities
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <div className="pulse-dot" />
            <span>API Connected</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
