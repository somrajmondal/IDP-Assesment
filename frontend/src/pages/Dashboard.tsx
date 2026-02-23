import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { useNavigate } from 'react-router-dom'
import { Plus, Upload, FolderOpen, Play, Eye, Download, Trash2, X, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { foldersApi, documentTypesApi, processApi } from '../utils/api'
import './Dashboard.css'

function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

function CreateFolderModal({ onClose, docTypes }: { onClose: () => void, docTypes: any[] }) {
  const [name, setName] = useState('')
  const [docTypeId, setDocTypeId] = useState('')
  const qc = useQueryClient()

  const mutation = useMutation({
    mutationFn: () => foldersApi.create({ name, document_type_id: docTypeId ? Number(docTypeId) : null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['folders'] })
      toast.success('Folder created!')
      onClose()
    },
    onError: () => toast.error('Failed to create folder')
  })

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Create New Folder</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <div className="form-group">
          <label>Folder Name</label>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Customer KYC Batch 1" />
        </div>
        
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => mutation.mutate()} disabled={!name || mutation.isPending}>
            {mutation.isPending ? 'Creating...' : 'Create Folder'}
          </button>
        </div>
      </div>
    </div>
  )
}

function UploadModal({ folder, onClose }: { folder: any, onClose: () => void }) {
  const [files, setFiles] = useState<File[]>([])
  const qc = useQueryClient()

  const onDrop = useCallback((accepted: File[]) => {
    const remaining = 5 - (folder.files?.length || 0)
    const toAdd = accepted.slice(0, remaining)
    if (accepted.length > remaining) {
      toast.error(`Only ${remaining} more files allowed (max 5 per folder)`)
    }
    setFiles(prev => [...prev, ...toAdd].slice(0, 5))
  }, [folder])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/pdf': ['.pdf'], 'image/*': ['.jpg','.jpeg','.png','.tif','.tiff'] }
  })

  const mutation = useMutation({
    mutationFn: () => foldersApi.uploadFiles(folder.id, files),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['folders'] })
      toast.success(`${files.length} file(s) uploaded!`)
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Upload failed')
  })

  const removeFile = (i: number) => setFiles(prev => prev.filter((_, idx) => idx !== i))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Upload Files to "{folder.name}"</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <div className="upload-info">
          <AlertCircle size={14} />
          <span>{folder.files?.length || 0}/5 files used · Max 5 files per folder</span>
        </div>
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          <Upload size={32} className="dropzone-icon" />
          <p>Drop files here or <strong>click to browse</strong></p>
          <p className="text-muted text-sm">PDF, JPG, PNG, TIFF supported</p>
        </div>
        {files.length > 0 && (
          <div className="file-list mt-2">
            {files.map((f, i) => (
              <div key={i} className="file-item">
                <span className="file-name">{f.name}</span>
                <span className="text-muted text-sm">{(f.size / 1024).toFixed(1)}KB</span>
                <button className="btn btn-danger btn-icon btn-sm" onClick={() => removeFile(i)}><X size={12} /></button>
              </div>
            ))}
          </div>
        )}
        <div className="flex gap-2 mt-4">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => mutation.mutate()} disabled={!files.length || mutation.isPending}>
            {mutation.isPending ? 'Uploading...' : `Upload ${files.length} file(s)`}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [showCreate, setShowCreate] = useState(false)
  const [uploadFolder, setUploadFolder] = useState<any>(null)
  const qc = useQueryClient()
  const navigate = useNavigate()

  const { data: folders = [], isLoading } = useQuery({
    queryKey: ['folders'],
    queryFn: () => foldersApi.list().then(r => r.data),
    refetchInterval: 5000
  })

  const { data: docTypes = [] } = useQuery({
    queryKey: ['document-types'],
    queryFn: () => documentTypesApi.list().then(r => r.data)
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => foldersApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['folders'] }); toast.success('Folder deleted') }
  })

  const processMutation = useMutation({
    mutationFn: (folderId: number) => processApi.start({ folder_id: folderId }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['folders'] }); toast.success('Processing started!') },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Failed to start processing')
  })

  const seedMutation = useMutation({
    mutationFn: () => documentTypesApi.seed(),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['document-types'] }); toast.success('Sample data seeded!') }
  })

  const stats = {
    total: folders.length,
    pending: folders.filter((f: any) => f.status === 'pending').length,
    processing: folders.filter((f: any) => f.status === 'processing').length,
    completed: folders.filter((f: any) => f.status === 'completed').length,
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="page-title"> Inteligent Document Processing Software</h1>
          <p className="page-sub">Upload, process and Break down data barriers with  AI extract valuable information from documents.</p>
        </div>
        <div className="flex gap-2">
          
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <Plus size={16} /> New Folder
          </button>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Folders</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.pending}</div>
          <div className="stat-label">Pending</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--accent)' }}>{stats.processing}</div>
          <div className="stat-label">Processing</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.completed}</div>
          <div className="stat-label">Completed</div>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-state">
          <div className="spinner" />
          <span>Loading folders...</span>
        </div>
      ) : folders.length === 0 ? (
        <div className="empty-state">
          <FolderOpen size={48} className="empty-icon" />
          <h3>No folders yet</h3>
          <p>Create a folder and upload documents to get started</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <Plus size={16} /> Create First Folder
          </button>
        </div>
      ) : (
        <div className="folders-grid">
          {folders.map((folder: any) => {
            const docType = docTypes.find((dt: any) => dt.id === folder.document_type_id)
            return (
              <div key={folder.id} className="folder-card">
                <div className="folder-card-header">
                  <div className="folder-icon-wrap">
                    <FolderOpen size={18} />
                  </div>
                  <div className="folder-info">
                    <div className="folder-name">{folder.name}</div>
                    {docType && <div className="folder-type">{docType.document_name}</div>}
                  </div>
                  <StatusBadge status={folder.status} />
                </div>

                <div className="folder-meta">
                  <div className="file-count-bar">
                    <div className="file-count-fill" style={{ width: `${(folder.files?.length || 0) / 5 * 100}%` }} />
                  </div>
                  <div className="flex justify-between text-sm text-muted mt-2">
                    <span>{folder.files?.length || 0} / 5 files</span>
                    <span>{new Date(folder.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="folder-actions">
                  <button className="btn btn-secondary btn-sm" onClick={() => setUploadFolder(folder)}
                    disabled={(folder.files?.length || 0) >= 5}>
                    <Upload size={13} /> Upload
                  </button>

                  <button className="btn btn-success btn-sm"
                    onClick={() => processMutation.mutate(folder.id)}
                    disabled={!folder.files?.length || folder.status === 'processing'}>
                    <Play size={13} /> Process
                  </button>


                  <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/folder/${folder.id}`)}>
                    <Eye size={13} /> View
                  </button>
                  <a className="btn btn-secondary btn-sm" href={foldersApi.downloadZip(folder.id)} download>
                    <Download size={13} />
                  </a>
                  <button className="btn btn-danger btn-sm" onClick={() => {
                    if (confirm('Delete this folder?')) deleteMutation.mutate(folder.id)
                  }}>
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showCreate && <CreateFolderModal onClose={() => setShowCreate(false)} docTypes={docTypes} />}
      {uploadFolder && <UploadModal folder={uploadFolder} onClose={() => setUploadFolder(null)} />}
    </div>
  )
}
