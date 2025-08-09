import React, { useEffect, useRef, useState } from 'react';
import { Box } from '@mui/material';
// @ts-ignore
import Globe from 'react-globe.gl';
import { GlobeProps, Mathematician, GlobePoint } from '../../types';

const POPULARITY_COLORS = {
  very_high: '#c9b037', // Antique Gold for highest
  high: '#d4a574',      // Dusty Rose  
  medium: '#8b7355',    // Darker gold
  low: '#9bb0c1',       // Muted powder blue
  very_low: '#b8860b'   // Dark golden rod
};

const POPULARITY_SIZES = {
  very_high: 0.8,
  high: 0.6,
  medium: 0.4,
  low: 0.3,
  very_low: 0.2
};

const GlobeComponent: React.FC<GlobeProps> = ({
  mathematicians,
  locations,
  selectedYear,
  onMathematicianClick
}) => {
  const globeEl = useRef<any>(null);
  const [globePoints, setGlobePoints] = useState<GlobePoint[]>([]);

  // Get default coordinates for mathematicians without location data
  const getDefaultCoordinates = (mathematician: any) => {
    const defaults: Record<string, {lat: number, lng: number}> = {
      'Swiss': { lat: 47.0, lng: 8.0 },
      'French': { lat: 48.8566, lng: 2.3522 },
      'Italian-French': { lat: 45.0, lng: 7.0 },
      'Italian': { lat: 41.9028, lng: 12.4964 },
      'German': { lat: 51.1657, lng: 10.4515 },
      'English': { lat: 51.5074, lng: -0.1278 },
      'Scottish': { lat: 56.0, lng: -4.0 }
    };
    return defaults[mathematician.nationality] || { lat: 48.8566, lng: 2.3522 }; // Default to Paris
  };

  // Convert mathematicians to globe points
  useEffect(() => {
    const points: GlobePoint[] = [];
    
    mathematicians.forEach(mathematician => {
      // Find events for current year with locations
      const currentYearEvents = mathematician.timeline_events.filter(event => {
        const eventYear = typeof event.year === 'number' 
          ? event.year 
          : parseInt(event.year.toString().split('-')[0]);
        
        const eventEndYear = typeof event.year === 'string' && event.year.includes('-')
          ? parseInt(event.year.split('-')[1])
          : eventYear;
        
        return eventYear <= selectedYear && eventEndYear >= selectedYear;
      });

      // Get the most relevant event with location data
      const eventWithLocation = currentYearEvents.find(event => 
        event.location.coordinates && 
        event.location.coordinates.lat && 
        event.location.coordinates.lng
      );

      let coordinates;
      if (eventWithLocation?.location.coordinates) {
        coordinates = eventWithLocation.location.coordinates;
      } else {
        // Fallback: use birth location if available
        const birthEvent = mathematician.timeline_events.find(e => 
          e.event_type === 'birth' && e.location.coordinates
        );
        
        if (birthEvent?.location.coordinates) {
          coordinates = birthEvent.location.coordinates;
        } else {
          // Final fallback: use nationality-based default
          coordinates = getDefaultCoordinates(mathematician);
        }
      }

      if (coordinates) {
        points.push({
          lat: coordinates.lat,
          lng: coordinates.lng,
          mathematician,
          size: POPULARITY_SIZES[mathematician.popularity_tier] || 0.3,
          color: POPULARITY_COLORS[mathematician.popularity_tier] || '#42a5f5'
        });
      }
    });

    setGlobePoints(points);
  }, [mathematicians, selectedYear]);

  // Initialize globe camera position
  useEffect(() => {
    if (globeEl.current) {
      // Set initial camera position (view of Europe)
      globeEl.current.pointOfView({ lat: 50, lng: 10, altitude: 2 });
    }
  }, []);

  const handlePointClick = (point: any) => {
    if (point.mathematician) {
      onMathematicianClick(point.mathematician);
    }
  };

  const getPointLabel = (point: any) => {
    const m = point.mathematician as Mathematician;
    return `
      <div style="
        background: rgba(0,0,0,0.8);
        padding: 8px 12px;
        border-radius: 6px;
        color: white;
        font-family: Roboto, Arial, sans-serif;
        max-width: 250px;
      ">
        <div style="font-weight: bold; margin-bottom: 4px;">
          ${m.name}
        </div>
        <div style="font-size: 0.9em; opacity: 0.9;">
          ${m.birth_year} - ${m.death_year} • ${m.nationality}
        </div>
        <div style="font-size: 0.8em; opacity: 0.8; margin-top: 4px;">
          ${m.fields.join(', ')}
        </div>
        <div style="font-size: 0.8em; opacity: 0.7; margin-top: 2px;">
          Click for details
        </div>
      </div>
    `;
  };

  return (
    <Box sx={{ width: '100%', height: '100%' }}>
      <Globe
        ref={globeEl}
        showGlobe={true}
        showGraticules={true}
        backgroundColor="#b0c4de"
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-day.jpg"
        showAtmosphere={true}
        atmosphereColor="#d4a574"
        
        // Points configuration
        pointsData={globePoints}
        pointColor="color"
        pointAltitude={(point: any) => point.size * 0.1}
        pointRadius="size"
        pointResolution={8}
        
        // Interactions
        onPointClick={handlePointClick}
        pointLabel={getPointLabel}
        
        // Animation and controls
        enablePointerInteraction={true}
        animateIn={false}
        
        // Atmosphere
        atmosphereAltitude={0.15}
        
        // Performance
        rendererConfig={{ antialias: true }}
        
        // Initial camera position
        width={window.innerWidth}
        height={window.innerHeight}
      />
    </Box>
  );
};

export default GlobeComponent;