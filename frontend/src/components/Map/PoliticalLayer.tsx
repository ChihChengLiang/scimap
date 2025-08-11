import React, { useMemo } from 'react';
import L from 'leaflet';
import { PoliticalContext } from '../../types';
import MarkerClusterGroup from './MarkerClusterGroup';

interface PoliticalLayerProps {
  politicalContexts: PoliticalContext[];
  selectedYear: number;
  visible: boolean;
}

// Helper function for getting category colors
const getIconColor = (cat: string): string => {
  switch (cat) {
    case 'political_change': return '#8B4513'; // Saddle brown
    case 'war': return '#DC143C'; // Crimson
    case 'treaty': return '#228B22'; // Forest green
    case 'city_founding': return '#4169E1'; // Royal blue
    case 'social_reform': return '#FF69B4'; // Hot pink
    case 'royal_succession': return '#FFD700'; // Gold
    case 'legal_change': return '#800080'; // Purple
    case 'natural_disaster': return '#B22222'; // Fire brick
    case 'military_conquest': return '#8B0000'; // Dark red
    case 'rebellion': return '#FF4500'; // Orange red
    case 'revolution': return '#FF0000'; // Red
    case 'political_declaration': return '#4B0082'; // Indigo
    case 'intellectual_milestone': return '#9370DB'; // Medium purple
    case 'military_alliance': return '#006400'; // Dark green
    case 'territorial_partition': return '#A0522D'; // Sienna
    case 'political_coup': return '#DC143C'; // Crimson
    case 'exploration': return '#20B2AA'; // Light sea green
    case 'religious_movement': return '#DAA520'; // Goldenrod
    case 'climate_event': return '#87CEEB'; // Sky blue
    case 'calendar_reform': return '#DDA0DD'; // Plum
    case 'military_battle': return '#B22222'; // Fire brick
    case 'political_crisis': return '#FF6347'; // Tomato
    case 'state_founding': return '#4169E1'; // Royal blue
    default: return '#696969'; // Dim gray
  }
};

// Helper function for getting category symbols
const getIconSymbol = (cat: string): string => {
  switch (cat) {
    case 'political_change': return '👑';
    case 'war': return '⚔️';
    case 'treaty': return '🕊️';
    case 'city_founding': return '🏛️';
    case 'social_reform': return '⚖️';
    case 'royal_succession': return '👑';
    case 'legal_change': return '📜';
    case 'natural_disaster': return '🌪️';
    case 'military_conquest': return '🏹';
    case 'rebellion': return '🔥';
    case 'revolution': return '🔴';
    case 'political_declaration': return '📋';
    case 'intellectual_milestone': return '💡';
    case 'military_alliance': return '🤝';
    case 'territorial_partition': return '📍';
    case 'political_coup': return '💥';
    case 'exploration': return '🧭';
    case 'religious_movement': return '⛪';
    case 'climate_event': return '❄️';
    case 'calendar_reform': return '📅';
    case 'military_battle': return '⚔️';
    case 'political_crisis': return '⚠️';
    case 'state_founding': return '🏛️';
    default: return '📜';
  }
};

// Custom political context marker icon
const createPoliticalIcon = (category: string, relevanceScore: number) => {
  const size = Math.max(18, Math.min(28, 18 + relevanceScore * 10)); // Enhanced size scaling
  
  return L.divIcon({
    className: 'political-marker',
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${getIconColor(category)};
        border: 2px solid #2c3e50;
        border-radius: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${size * 0.6}px;
        opacity: 0.85;
        transform: scale(1);
        transition: all 0.2s ease;
        position: relative;
      ">
        ${getIconSymbol(category)}
        <div style="
          position: absolute;
          top: -2px;
          right: -2px;
          width: 8px;
          height: 8px;
          background: ${relevanceScore > 0.8 ? '#FFD700' : relevanceScore > 0.6 ? '#FFA500' : '#87CEEB'};
          border-radius: 50%;
          border: 1px solid white;
          box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        "></div>
      </div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2]
  });
};

// Category display name helper
const getCategoryDisplayName = (category: string): string => {
  switch (category) {
    case 'political_change': return 'Political Change';
    case 'war': return 'War';
    case 'treaty': return 'Treaty';
    case 'city_founding': return 'City Founded';
    case 'social_reform': return 'Social Reform';
    case 'royal_succession': return 'Royal Succession';
    case 'legal_change': return 'Legal Reform';
    case 'natural_disaster': return 'Natural Disaster';
    case 'military_conquest': return 'Military Conquest';
    case 'rebellion': return 'Rebellion';
    case 'revolution': return 'Revolution';
    case 'political_declaration': return 'Political Declaration';
    case 'intellectual_milestone': return 'Intellectual Milestone';
    case 'military_alliance': return 'Military Alliance';
    case 'territorial_partition': return 'Territorial Partition';
    case 'political_coup': return 'Political Coup';
    case 'exploration': return 'Exploration';
    case 'religious_movement': return 'Religious Movement';
    case 'climate_event': return 'Climate Event';
    case 'calendar_reform': return 'Calendar Reform';
    case 'military_battle': return 'Military Battle';
    case 'political_crisis': return 'Political Crisis';
    case 'state_founding': return 'State Founded';
    default: return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
};

const PoliticalLayer: React.FC<PoliticalLayerProps> = ({
  politicalContexts,
  selectedYear,
  visible
}) => {
  // Filter political contexts relevant to the selected year (within 15 years for broader context)
  const relevantContexts = politicalContexts.filter(context => 
    Math.abs(context.year - selectedYear) <= 15
  );

  // Create Leaflet markers for clustering
  const leafletMarkers = useMemo(() => {
    return relevantContexts.map(context => {
      const icon = createPoliticalIcon(context.category, context.relevance_score);
      
      // Create the popup HTML content
      const popupContent = `
        <div style="font-family: serif; color: #2c3e50; line-height: 1.4; max-width: 280px;">
          <h3 style="margin: 0 0 8px 0; color: #8B4513; font-size: 1.1em; font-weight: bold;">
            ${context.headline}
          </h3>
          
          <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0 8px 0; font-size: 0.85em; font-style: italic; color: #5d6d7e;">
            <span style="background: ${getIconColor(context.category)}20; color: ${getIconColor(context.category)}; padding: 2px 6px; border-radius: 12px; font-size: 0.8em; font-weight: bold; font-style: normal;">
              ${getCategoryDisplayName(context.category)}
            </span>
            <span>${context.year}</span>
          </div>
          
          <p style="margin: 0 0 4px 0; font-size: 0.8em; font-weight: bold; color: #5d6d7e;">
            📍 ${context.location.primary_location}, ${context.location.region}
          </p>
          
          <p style="margin: 8px 0; font-size: 0.9em; line-height: 1.4;">
            ${context.description}
          </p>
          
          <div style="background: rgba(139, 69, 19, 0.08); padding: 8px 10px; border-radius: 6px; margin: 10px 0; border-left: 3px solid #8B4513;">
            <p style="margin: 0 0 4px 0; font-size: 0.85em; font-weight: bold; color: #8B4513;">
              📚 Impact on Mathematics & Science:
            </p>
            <p style="margin: 0; font-size: 0.85em; line-height: 1.3; font-style: italic;">
              ${context.impact_on_science}
            </p>
          </div>
          
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 8px; border-top: 1px solid rgba(139, 69, 19, 0.2);">
            <a href="${context.wiki_link}" target="_blank" rel="noopener noreferrer" style="font-size: 0.8em; color: #8B4513; text-decoration: none; font-weight: bold; display: flex; align-items: center; gap: 4px;">
              📖 Read more
            </a>
            <div style="display: flex; align-items: center; gap: 4px;">
              <div style="width: 8px; height: 8px; border-radius: 50%; background: ${context.relevance_score > 0.8 ? '#FFD700' : context.relevance_score > 0.6 ? '#FFA500' : '#87CEEB'};"></div>
              <span style="font-size: 0.75em; color: #888; font-weight: bold;">
                ${Math.round(context.relevance_score * 100)}% relevance
              </span>
            </div>
          </div>
        </div>
      `;

      // Create Leaflet marker
      const marker = L.marker([context.location.coordinates.lat, context.location.coordinates.lng], { icon });
      
      // Bind popup
      marker.bindPopup(popupContent);

      return marker;
    });
  }, [relevantContexts]);

  if (!visible) return null;

  return (
    <>
      <MarkerClusterGroup 
        markers={leafletMarkers}
        maxClusterRadius={40} // Smaller radius for political events to separate them better
        spiderfyOnMaxZoom={true}
        showCoverageOnHover={false}
        zoomToBoundsOnClick={true}
        removeOutsideVisibleBounds={true}
      />
    </>
  );
};

export default PoliticalLayer;