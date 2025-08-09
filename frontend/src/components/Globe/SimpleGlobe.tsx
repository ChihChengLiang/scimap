import React, { useEffect, useState } from 'react';
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
      very_high: '#c9b037', // Antique Gold
      high: '#d4a574',      // Dusty Rose  
      medium: '#8b7355',    // Darker gold
      low: '#9bb0c1',       // Muted powder blue
      very_low: '#b8860b'   // Dark golden rod
    };
    return colors[tier as keyof typeof colors] || '#9bb0c1';
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
      background: 'radial-gradient(circle at center, #9bb0c1 0%, #8aa3b3 40%, #7a96a5 100%)', // Ocean gradient in muted blues
      overflow: 'hidden'
    }}>
      {/* Earth representation with Rococo styling */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '80%',
          height: '80%',
          borderRadius: '50%',
          background: 'radial-gradient(circle at 30% 30%, #a8c0d8 0%, #9bb0c1 100%)', // Ocean blue gradient
          border: '3px solid #d4a574', // Dusty Rose border
          boxShadow: 'inset 0 0 30px rgba(155, 176, 193, 0.4), 0 0 20px rgba(201, 176, 55, 0.3)', // Ocean shadows
          opacity: 0.95
        }}
      >
        {/* Simple continent representations */}
        {/* Europe */}
        <Box sx={{
          position: 'absolute',
          top: '25%',
          left: '48%',
          width: '12%',
          height: '20%',
          background: 'linear-gradient(135deg, #e8e8e8 0%, #d4a574 100%)', // Pearl Gray to Dusty Rose for land
          borderRadius: '40% 20% 60% 30%',
          opacity: 0.9,
          border: '1px solid rgba(201, 176, 55, 0.3)'
        }} />
        
        {/* Asia */}
        <Box sx={{
          position: 'absolute',
          top: '20%',
          left: '60%',
          width: '25%',
          height: '30%',
          background: 'linear-gradient(135deg, #e8e8e8 0%, #d4a574 100%)',
          borderRadius: '30% 50% 40% 60%',
          opacity: 0.9,
          border: '1px solid rgba(201, 176, 55, 0.3)'
        }} />
        
        {/* Africa */}
        <Box sx={{
          position: 'absolute',
          top: '35%',
          left: '45%',
          width: '15%',
          height: '35%',
          background: 'linear-gradient(135deg, #e8e8e8 0%, #d4a574 100%)',
          borderRadius: '20% 30% 40% 70%',
          opacity: 0.9,
          border: '1px solid rgba(201, 176, 55, 0.3)'
        }} />
        
        {/* North America */}
        <Box sx={{
          position: 'absolute',
          top: '15%',
          left: '15%',
          width: '20%',
          height: '25%',
          background: 'linear-gradient(135deg, #e8e8e8 0%, #d4a574 100%)',
          borderRadius: '50% 30% 40% 60%',
          opacity: 0.9,
          border: '1px solid rgba(201, 176, 55, 0.3)'
        }} />
        
        {/* South America */}
        <Box sx={{
          position: 'absolute',
          top: '45%',
          left: '25%',
          width: '12%',
          height: '30%',
          background: 'linear-gradient(135deg, #e8e8e8 0%, #d4a574 100%)',
          borderRadius: '30% 40% 20% 70%',
          opacity: 0.9,
          border: '1px solid rgba(201, 176, 55, 0.3)'
        }} />
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
          background: 'rgba(232, 232, 232, 0.95)', // Pearl Gray
          padding: 2,
          borderRadius: 2,
          border: '1px solid rgba(201, 176, 55, 0.3)',
          color: '#2c3e50',
          fontSize: '0.75rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#c9b037' }}></div>
          Very High Popularity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#d4a574' }}></div>
          High Popularity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#8b7355' }}></div>
          Medium Popularity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#9bb0c1' }}></div>
          Low Popularity
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '4px', height: '4px', borderRadius: '50%', backgroundColor: '#b8860b' }}></div>
          Very Low Popularity
        </div>
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