'use client'

import { useState } from 'react'
import FloorplanViewer from '@/components/FloorplanViewer'
import { Building2, Search } from 'lucide-react'

export default function FloorplansPage() {
  const [searchType, setSearchType] = useState<'location' | 'project'>('location')
  const [searchId, setSearchId] = useState<string>('')

  // IDs des principales zones Dubai
  const locations = [
    { id: 10, name: 'Dubai Marina' },
    { id: 36, name: 'Downtown Dubai' },
    { id: 21741, name: 'Palm Jumeirah' },
    { id: 59, name: 'Business Bay' },
    { id: 72, name: 'JBR' },
    { id: 16770, name: 'Dubai Hills' },
    { id: 11, name: 'Arabian Ranches' },
    { id: 87107, name: 'Dubai Creek Harbour' },
  ]

  const handleSearch = () => {
    // Trigger search
  }

  return (
    <div className="min-h-screen bg-background-primary p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-accent rounded-full flex items-center justify-center">
            <Building2 className="w-6 h-6 text-background-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Plans d'Étage</h1>
            <p className="text-text-muted">Visualisation 2D/3D des propriétés à Dubai</p>
          </div>
        </div>

        {/* Search Controls */}
        <div className="bg-background-secondary border border-border rounded-lg p-6 space-y-4">
          <div className="flex gap-4">
            {/* Search Type Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setSearchType('location')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  searchType === 'location'
                    ? 'bg-accent text-background-primary'
                    : 'bg-background-primary text-text-secondary border border-border hover:border-accent'
                }`}
              >
                Par Zone
              </button>
              <button
                onClick={() => setSearchType('project')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  searchType === 'project'
                    ? 'bg-accent text-background-primary'
                    : 'bg-background-primary text-text-secondary border border-border hover:border-accent'
                }`}
              >
                Par Projet
              </button>
            </div>
          </div>

          {/* Search Input */}
          {searchType === 'location' ? (
            <div className="space-y-2">
              <label className="text-sm text-text-muted">Sélectionner une zone</label>
              <select
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                className="w-full bg-background-primary border border-border rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-accent"
              >
                <option value="">-- Choisir une zone --</option>
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div className="space-y-2">
              <label className="text-sm text-text-muted">ID du projet</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  placeholder="Ex: 87107"
                  className="flex-1 bg-background-primary border border-border rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-accent"
                />
                <button
                  onClick={handleSearch}
                  className="px-6 py-2 bg-accent text-background-primary rounded-lg font-medium hover:bg-accent/90 transition-colors flex items-center gap-2"
                >
                  <Search className="w-4 h-4" />
                  Rechercher
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Floorplans Viewer */}
        {searchId && (
          <FloorplanViewer
            locationId={searchType === 'location' ? parseInt(searchId) : undefined}
            projectId={searchType === 'project' ? parseInt(searchId) : undefined}
          />
        )}

        {/* Info Card */}
        {!searchId && (
          <div className="bg-background-secondary border border-border rounded-lg p-8 text-center space-y-4">
            <Building2 className="w-16 h-16 text-text-muted mx-auto" />
            <div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Explorez les Plans d'Étage
              </h3>
              <p className="text-text-muted max-w-2xl mx-auto">
                Sélectionnez une zone ou entrez un ID de projet pour visualiser les plans d'étage 2D/3D
                avec modèles interactifs.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-2 pt-4">
              {locations.slice(0, 4).map((loc) => (
                <button
                  key={loc.id}
                  onClick={() => {
                    setSearchType('location')
                    setSearchId(loc.id.toString())
                  }}
                  className="px-4 py-2 bg-background-primary border border-border rounded-lg text-sm text-text-secondary hover:border-accent hover:text-accent transition-colors"
                >
                  {loc.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
