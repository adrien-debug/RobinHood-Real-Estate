'use client'

import { useState, useEffect } from 'react'
import { Building, Bed, Bath, Maximize2, Eye } from 'lucide-react'
import { useAutoRefresh } from '@/lib/useAutoRefresh'

interface Floorplan {
  id: number
  beds: number
  baths: number
  category: string[]
  state: string
  models: string[]
  '2d_imgs': string[]
  '3d_imgs': string[]
}

interface FloorplanViewerProps {
  locationId?: number
  projectId?: number
}

export default function FloorplanViewer({ locationId, projectId }: FloorplanViewerProps) {
  const AUTO_REFRESH_MS = 5000
  const [floorplans, setFloorplans] = useState<Floorplan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFloorplan, setSelectedFloorplan] = useState<Floorplan | null>(null)
  const canFetch = Boolean(locationId || projectId)

  useEffect(() => {
    fetchFloorplans()
  }, [locationId, projectId])

  const fetchFloorplans = async () => {
    if (!canFetch) return
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams()
      if (locationId) params.append('location', locationId.toString())
      if (projectId) params.append('externalID', projectId.toString())

      // Call local API route (handles RapidAPI server-side)
      const response = await fetch(`/api/floorplans?${params}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setFloorplans(data.floorplans || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch floorplans')
      console.error('Error fetching floorplans:', err)
    } finally {
      setLoading(false)
    }
  }

  useAutoRefresh({
    intervalMs: AUTO_REFRESH_MS,
    onTick: fetchFloorplans,
    enabled: canFetch,
    deps: [locationId, projectId]
  })

  if (loading && floorplans.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
        <span className="ml-3 text-text-secondary">Chargement des plans...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-danger/10 border border-danger/20 rounded-lg p-4">
        <p className="text-danger text-sm">Erreur : {error}</p>
      </div>
    )
  }

  if (floorplans.length === 0) {
    return (
      <div className="bg-background-secondary border border-border rounded-lg p-8 text-center">
        <Building className="w-12 h-12 text-text-muted mx-auto mb-3" />
        <p className="text-text-secondary">Aucun plan d'étage disponible</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-text-primary">
          Plans d'Étage
        </h3>
        <span className="text-sm text-text-muted">
          {floorplans.length} plan{floorplans.length > 1 ? 's' : ''} disponible{floorplans.length > 1 ? 's' : ''}
        </span>
      </div>

      {/* Floorplans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {floorplans.map((floorplan) => (
          <div
            key={floorplan.id}
            className="bg-background-secondary border border-border rounded-lg overflow-hidden hover:border-accent transition-colors cursor-pointer"
            onClick={() => setSelectedFloorplan(floorplan)}
          >
            {/* Image Preview */}
            <div className="relative aspect-video bg-background-primary">
              {floorplan['2d_imgs'] && floorplan['2d_imgs'][0] ? (
                <img
                  src={floorplan['2d_imgs'][0]}
                  alt={`Plan ${floorplan.beds} chambres`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <Building className="w-12 h-12 text-text-muted" />
                </div>
              )}
              
              {/* Badges */}
              <div className="absolute top-2 right-2 flex gap-2">
                {floorplan.models && floorplan.models.length > 0 && (
                  <span className="bg-accent text-background-primary text-xs px-2 py-1 rounded-full">
                    3D
                  </span>
                )}
                {floorplan.state === 'active' && (
                  <span className="bg-success text-background-primary text-xs px-2 py-1 rounded-full">
                    Actif
                  </span>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="p-4 space-y-3">
              {/* Category */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-text-muted">
                  {floorplan.category.join(' • ')}
                </span>
              </div>

              {/* Specs */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5">
                  <Bed className="w-4 h-4 text-accent" />
                  <span className="text-sm text-text-primary font-medium">
                    {floorplan.beds === 0 ? 'Studio' : `${floorplan.beds} ch`}
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Bath className="w-4 h-4 text-accent" />
                  <span className="text-sm text-text-primary font-medium">
                    {floorplan.baths} sdb
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                {floorplan['2d_imgs'] && floorplan['2d_imgs'].length > 0 && (
                  <button className="flex-1 flex items-center justify-center gap-1.5 bg-background-primary border border-border rounded px-3 py-1.5 text-xs text-text-secondary hover:border-accent transition-colors">
                    <Maximize2 className="w-3 h-3" />
                    2D
                  </button>
                )}
                {floorplan['3d_imgs'] && floorplan['3d_imgs'].length > 0 && (
                  <button className="flex-1 flex items-center justify-center gap-1.5 bg-background-primary border border-border rounded px-3 py-1.5 text-xs text-text-secondary hover:border-accent transition-colors">
                    <Eye className="w-3 h-3" />
                    3D
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal for selected floorplan */}
      {selectedFloorplan && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedFloorplan(null)}
        >
          <div
            className="bg-background-secondary rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-background-secondary border-b border-border p-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-text-primary">
                  Plan {selectedFloorplan.beds === 0 ? 'Studio' : `${selectedFloorplan.beds} Chambres`}
                </h3>
                <p className="text-sm text-text-muted">
                  {selectedFloorplan.category.join(' • ')}
                </p>
              </div>
              <button
                onClick={() => setSelectedFloorplan(null)}
                className="text-text-muted hover:text-text-primary"
              >
                ✕
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* 3D Model */}
              {selectedFloorplan.models && selectedFloorplan.models[0] && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-text-primary">Modèle 3D Interactif</h4>
                  <div className="aspect-video rounded-lg overflow-hidden bg-background-primary">
                    <iframe
                      src={selectedFloorplan.models[0]}
                      className="w-full h-full"
                      allowFullScreen
                    />
                  </div>
                </div>
              )}

              {/* 2D Images */}
              {selectedFloorplan['2d_imgs'] && selectedFloorplan['2d_imgs'].length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-text-primary">Plans 2D</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedFloorplan['2d_imgs'].map((img, idx) => (
                      <img
                        key={idx}
                        src={img}
                        alt={`Plan 2D ${idx + 1}`}
                        className="w-full rounded-lg border border-border"
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* 3D Images */}
              {selectedFloorplan['3d_imgs'] && selectedFloorplan['3d_imgs'].length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-text-primary">Rendus 3D</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {selectedFloorplan['3d_imgs'].map((img, idx) => (
                      <img
                        key={idx}
                        src={img}
                        alt={`Rendu 3D ${idx + 1}`}
                        className="w-full rounded-lg border border-border"
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
