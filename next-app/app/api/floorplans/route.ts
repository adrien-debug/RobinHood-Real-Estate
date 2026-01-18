import { NextRequest, NextResponse } from 'next/server'

// Mock floorplans data for Dubai properties
const MOCK_FLOORPLANS = [
  {
    id: 1,
    beds: 0,
    baths: 1,
    category: ['Studio', 'Apartment'],
    state: 'active',
    models: [],
    '2d_imgs': ['https://images.bayut.com/thumbnails/floorplans/studio-type-1.jpg'],
    '3d_imgs': []
  },
  {
    id: 2,
    beds: 1,
    baths: 1,
    category: ['1 Bedroom', 'Apartment'],
    state: 'active',
    models: [],
    '2d_imgs': ['https://images.bayut.com/thumbnails/floorplans/1br-type-a.jpg'],
    '3d_imgs': []
  },
  {
    id: 3,
    beds: 2,
    baths: 2,
    category: ['2 Bedroom', 'Apartment'],
    state: 'active',
    models: [],
    '2d_imgs': ['https://images.bayut.com/thumbnails/floorplans/2br-type-b.jpg'],
    '3d_imgs': []
  },
  {
    id: 4,
    beds: 3,
    baths: 3,
    category: ['3 Bedroom', 'Penthouse'],
    state: 'active',
    models: [],
    '2d_imgs': ['https://images.bayut.com/thumbnails/floorplans/3br-penthouse.jpg'],
    '3d_imgs': []
  }
]

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const location = searchParams.get('location')
    const externalID = searchParams.get('externalID')

    // Get API key from server-side env
    const apiKey = process.env.BAYUT_API_KEY

    // If no API key, return mock data
    if (!apiKey) {
      console.log('Floorplans API: Using mock data (no BAYUT_API_KEY)')
      return NextResponse.json({
        floorplans: MOCK_FLOORPLANS,
        source: 'mock'
      })
    }

    // Build query params
    const params = new URLSearchParams()
    if (location) params.append('location', location)
    if (externalID) params.append('externalID', externalID)

    // Call RapidAPI
    const response = await fetch(
      `https://uae-real-estate2.p.rapidapi.com/floorplans?${params}`,
      {
        headers: {
          'X-RapidAPI-Key': apiKey,
          'X-RapidAPI-Host': 'uae-real-estate2.p.rapidapi.com'
        }
      }
    )

    if (!response.ok) {
      console.error(`Floorplans API error: ${response.status}`)
      // Fallback to mock on error
      return NextResponse.json({
        floorplans: MOCK_FLOORPLANS,
        source: 'mock',
        error: `API returned ${response.status}`
      })
    }

    const data = await response.json()
    
    // If no floorplans returned, use mock
    if (!data.floorplans || data.floorplans.length === 0) {
      return NextResponse.json({
        floorplans: MOCK_FLOORPLANS,
        source: 'mock',
        note: 'No floorplans found for this location'
      })
    }

    return NextResponse.json({
      floorplans: data.floorplans,
      source: 'live'
    })

  } catch (error) {
    console.error('Floorplans API error:', error)
    // Fallback to mock on any error
    return NextResponse.json({
      floorplans: MOCK_FLOORPLANS,
      source: 'mock',
      error: 'Failed to fetch from API'
    })
  }
}
