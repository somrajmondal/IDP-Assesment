import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit2, Trash2, X, FileType } from 'lucide-react'
import toast from 'react-hot-toast'
import { documentTypesApi } from '../../utils/api'
import './Admin.css'

function DocTypeModal({ item, onClose }: { item?: any, onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    document_name: item?.document_name || '',
    document_backend_key: item?.document_backend_key || '',
    features: item?.features || '',
    is_active: item?.is_active ?? true,
  })

  const mutation = useMutation({
    mutationFn: () => item
      ? documentTypesApi.update(item.id, form)
      : documentTypesApi.create(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['document-types'] })
      toast.success(item ? 'Updated!' : 'Created!')
      onClose()
    },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Error')
  })

  const set = (k: string) => (e: any) => setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{item ? 'Edit' : 'New'} Document Type</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <div className="form-group">
          <label>Document Name</label>
          <input value={form.document_name} onChange={set('document_name')} placeholder="e.g. Passport" />
        </div>
        <div className="form-group">
          <label>Backend Key</label>
          <input value={form.document_backend_key} onChange={set('document_backend_key')} placeholder="e.g. passport" disabled={!!item} />
          <div className="field-hint">Snake_case unique identifier used in API</div>
        </div>
        <div className="form-group">
          <label>Features / Description</label>
          <textarea rows={3} value={form.features} onChange={set('features')} placeholder="Describe what this document type includes..." />
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => mutation.mutate()} disabled={!form.document_name || !form.document_backend_key || mutation.isPending}>
            {mutation.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function AdminDocumentTypes() {
  const [modal, setModal] = useState<any>(null)
  const qc = useQueryClient()

  const { data: docTypes = [], isLoading } = useQuery({
    queryKey: ['document-types'],
    queryFn: () => documentTypesApi.list().then(r => r.data)
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentTypesApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['document-types'] }); toast.success('Deleted') }
  })

  const seedMutation = useMutation({
    mutationFn: () => documentTypesApi.seed(),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['document-types'] }); toast.success('Seeded sample data') }
  })

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="section-title" style={{ margin: 0 }}>Document Types ({docTypes.length})</div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={() => seedMutation.mutate()} disabled={seedMutation.isPending}>
            Seed Sample Data
          </button>
          <button className="btn btn-primary" onClick={() => setModal({})}>
            <Plus size={15} /> Add Type
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2" style={{ padding: 40 }}>
          <div className="spinner" /> Loading...
        </div>
      ) : docTypes.length === 0 ? (
        <div className="admin-empty">
          <FileType size={40} />
          <h3>No document types</h3>
          <p>Add a document type or seed sample data to get started</p>
          <button className="btn btn-primary" onClick={() => setModal({})}>
            <Plus size={15} /> Add First Type
          </button>
        </div>
      ) : (
        <div className="admin-cards">
          {docTypes.map((dt: any) => (
            <div key={dt.id} className="admin-card">
              <div className="admin-card-header">
                <div>
                  <div className="admin-card-title">{dt.document_name}</div>
                  <div className="admin-card-key">{dt.document_backend_key}</div>
                </div>
                <div className="flex gap-2 items-center">
                  <span className={`badge ${dt.is_active ? 'badge-completed' : 'badge-failed'}`}>
                    {dt.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <button className="btn btn-secondary btn-icon btn-sm" onClick={() => setModal(dt)}>
                    <Edit2 size={13} />
                  </button>
                  <button className="btn btn-danger btn-icon btn-sm" onClick={() => {
                    if (confirm('Delete this document type? All templates will be deleted too.'))
                      deleteMutation.mutate(dt.id)
                  }}>
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
              {dt.features && <p className="admin-card-desc">{dt.features}</p>}
              <div className="admin-card-meta">
                <span>{dt.templates?.length || 0} template(s)</span>
                <span>{new Date(dt.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {modal !== null && <DocTypeModal item={modal?.id ? modal : undefined} onClose={() => setModal(null)} />}
    </div>
  )
}
