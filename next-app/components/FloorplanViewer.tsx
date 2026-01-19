'use client'

import { useState, useEffect } from 'react'
import { Building, Bed, Bath, Maximize2 } from 'lucide-react'
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
    <div className="h-full flex flex-col">
      {/* Grille de plans - Utilise tout l'espace */}
      <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-3 overflow-auto">
        {floorplans.map((floorplan) => (
          <div
            key={floorplan.id}
            className="bg-background-secondary border border-border rounded-lg overflow-hidden hover:border-accent transition-colors cursor-pointer flex flex-col"
            onClick={() => setSelectedFloorplan(floorplan)}
          >
            {/* Image - Grande */}
            <div className="relative flex-1 min-h-[200px] bg-background-primary">
              {floorplan['2d_imgs'] && floorplan['2d_imgs'][0] ? (
                <img
                  src={floorplan['2d_imgs'][0]}
                  alt={`Plan ${floorplan.beds} chambres`}
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <Building className="w-10 h-10 text-text-muted" />
                </div>
              )}
              
              {/* Badges */}
              <div className="absolute top-2 right-2 flex gap-1">
                {floorplan.models && floorplan.models.length > 0 && (
                  <span className="bg-accent text-background-primary text-[10px] px-1.5 py-0.5 rounded">3D</span>
                )}
              </div>
            </div>

            {/* Info compacte */}
            <div className="p-2 border-t border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs">
                  <Bed className="w-3 h-3 text-accent" />
                  <span className="text-text-primary">{floorplan.beds === 0 ? 'Studio' : `${floorplan.beds}ch`}</span>
                  <Bath className="w-3 h-3 text-accent ml-1" />
                  <span className="text-text-primary">{floorplan.baths}sdb</span>
                </div>
                <Maximize2 className="w-3 h-3 text-text-muted" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal plein écran pour le plan sélectionné */}
      {selectedFloorplan && (
        <div
          className="fixed inset-0 bg-background-primary z-50 flex flex-col"
          onClick={() => setSelectedFloorplan(null)}
        >
          {/* Header minimal */}
          <div className="flex items-center justify-between p-3 border-b border-border bg-background-secondary">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-text-primary">
                {selectedFloorplan.beds === 0 ? 'Studio' : `${selectedFloorplan.beds} Chambres`} • {selectedFloorplan.baths} SDB
              </span>
              <span className="text-xs text-text-muted">{selectedFloorplan.category.join(' • ')}</span>
            </div>
            <button
              onClick={() => setSelectedFloorplan(null)}
              className="p-2 text-text-muted hover:text-text-primary rounded-lg hover:bg-background-hover"
            >
              ✕
            </button>
          </div>

          {/* Contenu - Modèle 3D plein écran */}
          <div className="flex-1 p-4" onClick={(e) => e.stopPropagation()}>
            {selectedFloorplan.models && selectedFloorplan.models[0] ? (
              <iframe
                src={selectedFloorplan.models[0]}
                className="w-full h-full rounded-lg border border-border"
                allowFullScreen
              />
            ) : selectedFloorplan['2d_imgs'] && selectedFloorplan['2d_imgs'][0] ? (
              <div className="w-full h-full flex items-center justify-center">
                <img
                  src={selectedFloorplan['2d_imgs'][0]}
                  alt="Plan 2D"
                  className="max-w-full max-h-full object-contain rounded-lg"
                />
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Building className="w-16 h-16 text-text-muted" />
              </div>
            )}
          </div>

          {/* Thumbnails en bas */}
          {(selectedFloorplan['2d_imgs']?.length > 1 || selectedFloorplan['3d_imgs']?.length > 0) && (
            <div className="p-3 border-t border-border bg-background-secondary">
              <div className="flex gap-2 overflow-x-auto">
                {selectedFloorplan['2d_imgs']?.map((img, idx) => (
                  <img
                    key={`2d-${idx}`}
                    src={img}
                    alt={`Plan ${idx + 1}`}
                    className="h-16 w-auto rounded border border-border hover:border-accent cursor-pointer"
                  />
                ))}
                {selectedFloorplan['3d_imgs']?.map((img, idx) => (
                  <img
                    key={`3d-${idx}`}
                    src={img}
                    alt={`Rendu ${idx + 1}`}
                    className="h-16 w-auto rounded border border-border hover:border-accent cursor-pointer"
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
