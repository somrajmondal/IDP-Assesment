import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit2, Trash2, X, ChevronDown, ChevronRight, Code, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import { templatesApi, documentTypesApi } from '../../utils/api'
import './Admin.css'

const DATA_TYPES = ['Alphabet', 'AlphaNumeric', 'Numeric', 'Date', 'Boolean', 'Text']

function EntityModal({ entity, templateId, onClose }: { entity?: any, templateId: number, onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    entity_name: entity?.entity_name || '',
    entity_name_for_dms: entity?.entity_name_for_dms || '',
    entity_key_customer_type: entity?.entity_key_customer_type || 'Individual',
    entity_key_rp_type: entity?.entity_key_rp_type || 'Individual-RP',
    entity_data_type: entity?.entity_data_type || 'AlphaNumeric',
    backend_entity_key: entity?.backend_entity_key || '',
    entity_description: entity?.entity_description || '',
    example_value: entity?.example_value || '',
    is_required: entity?.is_required || false,
    is_active: entity?.is_active ?? true,
  })

  const mutation = useMutation({
    mutationFn: () => entity?.id
      ? templatesApi.updateEntity(entity.id, form)
      : templatesApi.addEntity(templateId, form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['templates'] })
      toast.success(entity ? 'Entity updated' : 'Entity added')
      onClose()
    },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Error')
  })

  const set = (k: string) => (e: any) => setForm(f => ({ ...f, [k]: e.target.value }))
  const setBool = (k: string) => (e: any) => setForm(f => ({ ...f, [k]: e.target.checked }))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{entity ? 'Edit' : 'Add'} Entity</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label>Entity Name</label>
            <input value={form.entity_name} onChange={set('entity_name')} placeholder="e.g. Passport Number" />
          </div>
          <div className="form-group">
            <label>Entity Name (DMS)</label>
            <input value={form.entity_name_for_dms} onChange={set('entity_name_for_dms')} placeholder="e.g. Passport Number (as per Passport)" />
          </div>
          <div className="form-group">
            <label>Backend Key</label>
            <input value={form.backend_entity_key} onChange={set('backend_entity_key')} placeholder="e.g. passport_number" />
          </div>
          <div className="form-group">
            <label>Data Type</label>
            <select value={form.entity_data_type} onChange={set('entity_data_type')}>
              {DATA_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Customer Type</label>
            <select value={form.entity_key_customer_type} onChange={set('entity_key_customer_type')}>
              <option value="Individual">Individual</option>
            </select>
          </div>
       
          <div className="form-group">
            <label>Example Value</label>
            <input value={form.example_value} onChange={set('example_value')} placeholder="e.g. A1234567" />
          </div>
          <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <label>Flags</label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, textTransform: 'none', fontSize: 13, letterSpacing: 0 }}>
              <input type="checkbox" checked={form.is_required} onChange={setBool('is_required')} style={{ width: 'auto' }} />
              Required field
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, textTransform: 'none', fontSize: 13, letterSpacing: 0 }}>
              <input type="checkbox" checked={form.is_active} onChange={setBool('is_active')} style={{ width: 'auto' }} />
              Active
            </label>
          </div>
        </div>
        <div className="form-group">
          <label>Entity Description (used in LLM prompt)</label>
          <textarea rows={3} value={form.entity_description} onChange={set('entity_description')}
            placeholder="Describe what this entity extracts and how to identify it in the document..." />
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => mutation.mutate()}
            disabled={!form.entity_name || !form.backend_entity_key || mutation.isPending}>
            {mutation.isPending ? 'Saving...' : 'Save Entity'}
          </button>
        </div>
      </div>
    </div>
  )
}

function JsonPreviewModal({ templateId, onClose }: { templateId: number, onClose: () => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['template-json', templateId],
    queryFn: () => templatesApi.getJson(templateId).then(r => r.data)
  })

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">Template JSON Preview</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <p className="text-muted text-sm" style={{ marginBottom: 12 }}>
          This is the exact JSON sent to the LLM backend during processing.
        </p>
        {isLoading ? <div className="spinner" /> : (
          <div className="json-viewer">
            {JSON.stringify(data, null, 2)}
          </div>
        )}
        <div className="flex gap-2 mt-4">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
          {data && (
            <button className="btn btn-primary" onClick={() => {
              navigator.clipboard.writeText(JSON.stringify(data, null, 2))
              toast.success('Copied to clipboard!')
            }}>
              Copy JSON
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function FullJsonPreviewModal({ onClose }: { onClose: () => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ['template-json-all'],
    queryFn: () => templatesApi.getAllJson().then(r => r.data)
  })

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">All Templates JSON Preview</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <p className="text-muted text-sm" style={{ marginBottom: 12 }}>
          This is the full LLM payload with all document types, templates, and entities.
        </p>
        {isLoading ? <div className="spinner" /> : (
          <div className="json-viewer">
            {JSON.stringify(data, null, 2)}
          </div>
        )}
        <div className="flex gap-2 mt-4">
          <button className="btn btn-secondary" onClick={onClose}>Close</button>
          {data && (
            <button className="btn btn-primary" onClick={() => {
              navigator.clipboard.writeText(JSON.stringify(data, null, 2))
              toast.success('Copied full JSON to clipboard!')
            }}>
              Copy JSON
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function TemplateModal({ template, docTypeId, onClose }: { template?: any, docTypeId: number, onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    document_type_id: docTypeId,
    template_name: template?.template_name || '',
    description: template?.description || '',
    describe_document: template?.describe_document || '',
    keywords: template?.keywords || '',
    version: template?.version || '1.0',
    is_active: template?.is_active ?? true,
  })

  const mutation = useMutation({
    mutationFn: () => template?.id
      ? templatesApi.update(template.id, form)
      : templatesApi.create(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['templates'] })
      toast.success(template ? 'Template updated' : 'Template created')
      onClose()
    },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Error')
  })

  const set = (k: string) => (e: any) => setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">{template ? 'Edit' : 'New'} Template</span>
          <button className="btn btn-secondary btn-icon" onClick={onClose}><X size={14} /></button>
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label>Template Name</label>
            <input value={form.template_name} onChange={set('template_name')} placeholder="e.g. Standard Passport v1" />
          </div>
          <div className="form-group">
            <label>Version</label>
            <input value={form.version} onChange={set('version')} placeholder="1.0" />
          </div>
          <div className="form-group">
            <label>Keywords (comma separated)</label>
            <input value={form.keywords} onChange={set('keywords')} placeholder="e.g. passport, travel document" />
          </div>
        </div>
        <div className="form-group">
          <label>Short Description</label>
          <textarea rows={2} value={form.description} onChange={set('description')} placeholder="Brief description of the template" />
        </div>
        <div className="form-group">
          <label>Detailed Document Description (used in LLM prompt)</label>
          <textarea rows={4} value={form.describe_document} onChange={set('describe_document')}
            placeholder="Purpose: ...\nKey Features: ..." />
        </div>
        <div className="flex gap-2">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => mutation.mutate()} disabled={!form.template_name || mutation.isPending}>
            {mutation.isPending ? 'Saving...' : 'Save Template'}
          </button>
        </div>
      </div>
    </div>
  )
}

function TemplateBlock({ template }: { template: any }) {
  const qc = useQueryClient()
  const [expanded, setExpanded] = useState(true)
  const [entityModal, setEntityModal] = useState<any>(null)
  const [templateModal, setTemplateModal] = useState(false)
  const [jsonModal, setJsonModal] = useState(false)

  const deleteMutation = useMutation({
    mutationFn: (id: number) => templatesApi.deleteEntity(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['templates'] }); toast.success('Entity deleted') }
  })

  const deleteTemplate = useMutation({
    mutationFn: () => templatesApi.delete(template.id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['templates'] }); toast.success('Template deleted') }
  })

  return (
    <div className="template-block">
      <div className="template-header" onClick={() => setExpanded(e => !e)}>
        <div className="flex items-center gap-2">
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <span className="template-name">{template.template_name || `Template #${template.id}`}</span>
          <span className="text-muted text-sm">v{template.version}</span>
          <span className={`badge ${template.is_active ? 'badge-completed' : 'badge-failed'}`} style={{ fontSize: 10 }}>
            {template.is_active ? 'Active' : 'Inactive'}
          </span>
          <span className="entity-count">{template.entities?.length || 0} entities</span>
        </div>
        <div className="flex gap-2" onClick={e => e.stopPropagation()}>
          <button className="btn btn-secondary btn-sm" onClick={() => setJsonModal(true)}>
            <Code size={12} /> JSON
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => setTemplateModal(true)}>
            <Edit2 size={12} />
          </button>
          <button className="btn btn-danger btn-sm" onClick={() => {
            if (confirm('Delete this template and all its entities?')) deleteTemplate.mutate()
          }}>
            <Trash2 size={12} />
          </button>
        </div>
      </div>

      {expanded && (
        <div className="template-body">
          {template.description && <p className="template-desc">{template.description}</p>}

          <div className="entities-header">
            <span className="section-title" style={{ margin: 0 }}>Entities</span>
            <button className="btn btn-primary btn-sm" onClick={() => setEntityModal({})}>
              <Plus size={12} /> Add Entity
            </button>
          </div>

          {template.entities?.length === 0 ? (
            <div className="no-entities-admin">No entities yet. Add extraction fields.</div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Entity Name (T24)</th>
                  <th>Backend Key</th>
                  <th>Data Type</th>
                  <th>Customer Type</th>
                  <th>Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {template.entities?.map((entity: any) => (
                  <tr key={entity.id}>
                    <td>
                      <div>{entity.entity_name}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{entity.entity_description?.slice(0, 60)}...</div>
                    </td>
                    <td><code style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent)' }}>{entity.backend_entity_key}</code></td>
                    <td><span className="type-tag">{entity.entity_data_type}</span></td>
                    <td style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{entity.entity_key_customer_type}</td>
                    <td>
                      <span className={`badge ${entity.is_active ? 'badge-completed' : 'badge-failed'}`} style={{ fontSize: 9 }}>
                        {entity.is_active ? '✓' : '✗'}
                      </span>
                    </td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn btn-secondary btn-icon btn-sm" onClick={() => setEntityModal(entity)}>
                          <Edit2 size={11} />
                        </button>
                        <button className="btn btn-danger btn-icon btn-sm" onClick={() => {
                          if (confirm('Delete this entity?')) deleteMutation.mutate(entity.id)
                        }}>
                          <Trash2 size={11} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {entityModal !== null && (
        <EntityModal
          entity={entityModal?.id ? entityModal : undefined}
          templateId={template.id}
          onClose={() => setEntityModal(null)}
        />
      )}
      {templateModal && (
        <TemplateModal
          template={template}
          docTypeId={template.document_type_id}
          onClose={() => setTemplateModal(false)}
        />
      )}
      {jsonModal && <JsonPreviewModal templateId={template.id} onClose={() => setJsonModal(false)} />}
    </div>
  )
}

export default function AdminTemplates() {
  const [selectedDocType, setSelectedDocType] = useState<number | null>(null)
  const [templateModal, setTemplateModal] = useState(false)
  const [fullJsonModal, setFullJsonModal] = useState(false)

  const { data: docTypes = [] } = useQuery({
    queryKey: ['document-types'],
    queryFn: () => documentTypesApi.list().then(r => r.data)
  })

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['templates', selectedDocType],
    queryFn: () => templatesApi.list(selectedDocType || undefined).then(r => r.data)
  })

  const activeDocType = selectedDocType || docTypes[0]?.id

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="section-title" style={{ margin: 0 }}>Templates & Entities</div>
        <div className="flex gap-2 items-center">
          <select style={{ width: 'auto' }} value={selectedDocType || ''} onChange={e => setSelectedDocType(e.target.value ? Number(e.target.value) : null)}>
            <option value="">All Document Types</option>
            {docTypes.map((dt: any) => (
              <option key={dt.id} value={dt.id}>{dt.document_name}</option>
            ))}
          </select>
          <button className="btn btn-secondary" onClick={() => setFullJsonModal(true)}>
            <Code size={15} /> Full JSON
          </button>
          <button className="btn btn-primary" onClick={() => setTemplateModal(true)} disabled={docTypes.length === 0}>
            <Plus size={15} /> New Template
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2" style={{ padding: 40 }}>
          <div className="spinner" /> Loading...
        </div>
      ) : templates.length === 0 ? (
        <div className="admin-empty">
          <h3>No templates</h3>
          <p>{docTypes.length === 0 ? 'First create a document type, then add templates.' : 'Add a template to this document type'}</p>
        </div>
      ) : (
        <div>
          {templates.map((tmpl: any) => (
            <TemplateBlock key={tmpl.id} template={tmpl} />
          ))}
        </div>
      )}

      {templateModal && (
        <TemplateModal
          docTypeId={activeDocType}
          onClose={() => setTemplateModal(false)}
        />
      )}
      {fullJsonModal && <FullJsonPreviewModal onClose={() => setFullJsonModal(false)} />}
    </div>
  )
}
