import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  FileText,
  ChevronRight,
  Download,
  RefreshCw,
  Code,
  List,
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react'
import toast from 'react-hot-toast'
import { foldersApi, processApi } from '../utils/api'
import './FolderDetail.css'

/* ---------------------------------- */
/* FILE ICON */
/* ---------------------------------- */
function FileIcon({ type }: { type: string }) {
  const colors: Record<string, string> = {
    pdf: '#ef4444',
    jpg: '#f59e0b',
    jpeg: '#f59e0b',
    png: '#10b981',
    tiff: '#8b5cf6'
  }

  return (
    <div
      className="file-type-badge"
      style={{
        background: `${colors[type] || '#4f6ef7'}20`,
        color: colors[type] || '#4f6ef7'
      }}
    >
      {type?.toUpperCase() || 'FILE'}
    </div>
  )
}

/* ---------------------------------- */
/* EXTRACTION PANEL (PAGE-BASED) */


function ExtractionPanel({
  fileId,
  extractions
}: {
  fileId: number
  extractions: any[]
}) {
  if (!extractions || extractions.length === 0) {
    return (
      <div className="no-extraction">
        <Clock size={32} />
        <p>No extraction data yet</p>
        <span>Process this file to see results</span>
      </div>
    )
  }

  return (
    <div className="extraction-panel">
      {/* TOOLBAR */}
      <div className="extraction-toolbar">
        <span className="json-only-label">
          <Code size={14} /> JSON Output
        </span>

        <a
          href={`/api/documents/${fileId}/json`}
          download
          className="btn btn-secondary btn-sm"
        >
          <Download size={12} /> Export JSON
        </a>
      </div>

      {/* PAGE BLOCKS */}
      {extractions.map((pageBlock: any, idx: number) => (
        <div key={idx} className="extraction-block">
          {/* HEADER */}
          <div className="extraction-header">
            <div className="page-indicator">
              Page {pageBlock.page ?? idx + 1}
            </div>

            {pageBlock.classification && (
              <div className="classification-info">
                <span className="class-name">
                  {pageBlock.classification.class_name}
                </span>
                <span className="confidence-badge">
                  {(pageBlock.classification.score * 100).toFixed(0)}%
                </span>
                <span className="technique-tag">
                  {pageBlock.classification.technique}
                </span>
              </div>
            )}
          </div>

          {/* JSON VIEW */}
          <pre className="json-viewer">
            {JSON.stringify(pageBlock, null, 2)}
          </pre>
        </div>
      ))}
    </div>
  )
}
/* ---------------------------------- */
/* MAIN PAGE */
/* ---------------------------------- */
export default function FolderDetail() {
  const { folderId } = useParams<{ folderId: string }>()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [selectedFile, setSelectedFile] = useState<number | null>(null)

  const { data: folder, isLoading } = useQuery({
    queryKey: ['folder', folderId],
    queryFn: () => foldersApi.get(Number(folderId)).then(r => r.data),
    refetchInterval: 3000
  })

  const { data: results } = useQuery({
    queryKey: ['folder-results', folderId],
    queryFn: () => processApi.getResults(Number(folderId)).then(r => r.data),
    refetchInterval: folder?.status === 'processing' ? 2000 : false,
    enabled: !!folder
  })

  const processMutation = useMutation({
    mutationFn: () => processApi.start({ folder_id: Number(folderId) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['folder', folderId] })
      toast.success('Processing started!')
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.detail || 'Failed to start processing')
  })

  if (isLoading) {
    return (
      <div className="folder-detail-loading">
        <div className="spinner" /> Loading...
      </div>
    )
  }

  if (!folder) return <div>Folder not found</div>

  const activeFileId = selectedFile || folder.files?.[0]?.id
  const fileRes = results?.files?.find(
    (f: any) => f.file_id === activeFileId
  )

  return (
    <div className="folder-detail">
      {/* HEADER */}
      <div className="detail-header">
        <button className="btn btn-secondary btn-sm" onClick={() => navigate('/')}>
          <ArrowLeft size={14} /> Back
        </button>

        <h2>{folder.name}</h2>

        <button
          className="btn btn-success btn-sm"
          onClick={() => processMutation.mutate()}
          disabled={!folder.files?.length || folder.status === 'processing'}
        >
          Process All
        </button>
      </div>

      <div className="detail-panels">
        {/* FILE LIST */}
        <div className="files-panel">
          {folder.files.map((file: any) => (
            <div
              key={file.id}
              className={`file-list-item ${
                activeFileId === file.id ? 'active' : ''
              }`}
              onClick={() => setSelectedFile(file.id)}
            >
              <FileIcon type={file.file_type} />
              <span>{file.original_filename}</span>
            </div>
          ))}
        </div>

        {/* RESULTS */}
        <div className="results-panel">
          <ExtractionPanel
            fileId={activeFileId}
            extractions={fileRes?.extractions || []}
          />
        </div>
      </div>
    </div>
  )
}

/* ---------------------------------- */
function Play(props: any) {
  return (
    <svg {...props} viewBox="0 0 24 24" fill="currentColor">
      <path d="M8 5v14l11-7z" />
    </svg>
  )
}