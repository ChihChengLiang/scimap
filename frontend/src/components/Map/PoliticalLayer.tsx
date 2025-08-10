import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { PoliticalContext } from '../../types';

interface PoliticalLayerProps {
  politicalContexts: PoliticalContext[];
  selectedYear: number;
  visible: boolean;
}

// Custom political context marker icon
const createPoliticalIcon = (category: string, relevanceScore: number) => {
  const getIconColor = (cat: string): string => {
    switch (cat) {
      case 'political_change': return '#8B4513'; // Saddle brown
      case 'war': return '#DC143C'; // Crimson
      case 'peace_treaty': return '#228B22'; // Forest green
      case 'cultural_event': return '#9370DB'; // Medium purple
      case 'economic_shift': return '#FF8C00'; // Dark orange
      default: return '#696969'; // Dim gray
    }
  };

  const getIconSymbol = (cat: string): string => {
    switch (cat) {
      case 'political_change': return '👑';
      case 'war': return '⚔️';
      case 'peace_treaty': return '🕊️';
      case 'cultural_event': return '🎭';
      case 'economic_shift': return '💰';
      default: return '📜';
    }
  };

  const size = Math.max(16, Math.min(24, relevanceScore * 25)); // Size based on relevance
  
  return L.divIcon({
    className: 'political-marker',
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${getIconColor(category)};
        border: 2px solid #2c3e50;
        border-radius: 4px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${size * 0.6}px;
        opacity: 0.8;
      ">
        ${getIconSymbol(category)}
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  });
};

const PoliticalLayer: React.FC<PoliticalLayerProps> = ({
  politicalContexts,
  selectedYear,
  visible
}) => {
  if (!visible) return null;

  // Filter political contexts relevant to the selected year (within 10 years)
  const relevantContexts = politicalContexts.filter(context => 
    Math.abs(context.year - selectedYear) <= 10
  );

  return (
    <>
      {relevantContexts.map(context => (
        <Marker
          key={context.context_id}
          position={[context.location.lat, context.location.lng]}
          icon={createPoliticalIcon(context.category, context.relevance_score)}
        >
          <Popup>
            <div style={{ fontFamily: 'serif', color: '#2c3e50', minWidth: '200px' }}>
              <h3 style={{ 
                margin: '0 0 8px 0', 
                color: '#8B4513',
                fontSize: '1.1em',
                fontWeight: 'bold'
              }}>
                {context.headline}
              </h3>
              <p style={{ 
                margin: '4px 0', 
                fontSize: '0.85em',
                fontStyle: 'italic',
                color: '#5d6d7e'
              }}>
                {context.year} • {context.location.region}
              </p>
              <p style={{ 
                margin: '8px 0', 
                fontSize: '0.9em',
                lineHeight: '1.4'
              }}>
                {context.description}
              </p>
              <div style={{
                background: 'rgba(139, 69, 19, 0.1)',
                padding: '6px 8px',
                borderRadius: '4px',
                margin: '8px 0 4px 0'
              }}>
                <p style={{ 
                  margin: '0', 
                  fontSize: '0.85em',
                  fontWeight: 'bold',
                  color: '#8B4513'
                }}>
                  Impact on Mathematics:
                </p>
                <p style={{ 
                  margin: '2px 0 0 0', 
                  fontSize: '0.85em',
                  lineHeight: '1.3'
                }}>
                  {context.impact_on_science}
                </p>
              </div>
              <p style={{ 
                margin: '6px 0 0 0', 
                fontSize: '0.75em',
                color: '#888',
                textAlign: 'right'
              }}>
                Relevance: {Math.round(context.relevance_score * 100)}%
              </p>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default PoliticalLayer;