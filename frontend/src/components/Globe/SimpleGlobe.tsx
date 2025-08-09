import React, { useEffect, useRef, useState } from 'react';
import { Box } from '@mui/material';
import { GlobeProps, GlobePoint } from '../../types';

// Fallback simple globe component without react-globe.gl
const SimpleGlobe: React.FC<GlobeProps> = ({
  mathematicians,
  locations,
  selectedYear,
  onMathematicianClick
}) => {
  const [globePoints, setGlobePoints] = useState<GlobePoint[]>([]);

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

      if (eventWithLocation && eventWithLocation.location.coordinates) {
        points.push({
          lat: eventWithLocation.location.coordinates.lat,
          lng: eventWithLocation.location.coordinates.lng,
          mathematician,
          size: getPopularitySize(mathematician.popularity_tier),
          color: getPopularityColor(mathematician.popularity_tier)
        });
      }
    });

    setGlobePoints(points);
  }, [mathematicians, selectedYear]);

  const getPopularityColor = (tier: string) => {
    const colors = {
      very_high: '#ff6b6b',
      high: '#ffa726', 
      medium: '#66bb6a',
      low: '#42a5f5',
      very_low: '#ab47bc'
    };
    return colors[tier as keyof typeof colors] || '#42a5f5';
  };

  const getPopularitySize = (tier: string) => {
    const sizes = {
      very_high: 12,
      high: 10,
      medium: 8,
      low: 6,
      very_low: 4
    };
    return sizes[tier as keyof typeof sizes] || 6;
  };

  // Convert lat/lng to screen coordinates (simple orthographic projection)
  const projectToScreen = (lat: number, lng: number, width: number, height: number) => {
    const centerLat = 50; // Center on Europe
    const centerLng = 10;
    
    const x = width/2 + (lng - centerLng) * 5;
    const y = height/2 - (lat - centerLat) * 5;
    
    return { x: Math.max(0, Math.min(width, x)), y: Math.max(0, Math.min(height, y)) };
  };

  const handlePointClick = (mathematician: any) => {
    onMathematicianClick(mathematician);
  };

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%', 
      position: 'relative',
      background: 'radial-gradient(circle, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
      overflow: 'hidden'
    }}>
      {/* Earth representation */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '80%',
          height: '80%',
          borderRadius: '50%',
          background: 'radial-gradient(circle at 30% 30%, #4a90e2 0%, #2c3e50 70%, #1a1a1a 100%)',
          border: '2px solid rgba(74, 144, 226, 0.3)',
          boxShadow: 'inset 0 0 50px rgba(0,0,0,0.5), 0 0 30px rgba(74, 144, 226, 0.3)'
        }}
      >
        {/* Mathematician points */}
        {globePoints.map((point, index) => {
          const width = window.innerWidth * 0.8;
          const height = window.innerHeight * 0.8;
          const { x, y } = projectToScreen(point.lat, point.lng, width, height);
          
          return (
            <Box
              key={index}
              onClick={() => handlePointClick(point.mathematician)}
              sx={{
                position: 'absolute',
                left: `${(x / width) * 100}%`,
                top: `${(y / height) * 100}%`,
                width: point.size + 'px',
                height: point.size + 'px',
                borderRadius: '50%',
                backgroundColor: point.color,
                cursor: 'pointer',
                border: '2px solid rgba(255,255,255,0.8)',
                boxShadow: `0 0 ${point.size}px ${point.color}`,
                transform: 'translate(-50%, -50%)',
                animation: 'pulse 2s ease-in-out infinite',
                '&:hover': {
                  transform: 'translate(-50%, -50%) scale(1.2)',
                  boxShadow: `0 0 ${point.size * 2}px ${point.color}`
                }
              }}
              title={`${point.mathematician.name} (${point.mathematician.birth_year}-${point.mathematician.death_year})`}
            />
          );
        })}
      </Box>
      
      {/* Grid lines for geographic reference */}
      <svg 
        style={{ 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          width: '100%', 
          height: '100%',
          pointerEvents: 'none'
        }}
      >
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
      
      {/* Legend */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          background: 'rgba(26, 26, 26, 0.9)',
          padding: 2,
          borderRadius: 2,
          color: 'white',
          fontSize: '0.75rem'
        }}
      >
        <div>🔴 Very High Popularity</div>
        <div>🟠 High Popularity</div>
        <div>🟢 Medium Popularity</div>
        <div>🔵 Low Popularity</div>
        <div>🟣 Very Low Popularity</div>
      </Box>
      
      <style>{`
        @keyframes pulse {
          0% { opacity: 0.8; }
          50% { opacity: 1; }
          100% { opacity: 0.8; }
        }
      `}</style>
    </Box>
  );
};

export default SimpleGlobe;