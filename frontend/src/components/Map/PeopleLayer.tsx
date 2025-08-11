import React, { useMemo } from 'react';
import L from 'leaflet';
import { Mathematician, LocationData, TimelineEvent } from '../../types';
import MarkerClusterGroup from './MarkerClusterGroup';

interface PeopleLayerProps {
  mathematicians: Mathematician[];
  locations: Record<string, LocationData>;
  selectedYear: number;
  onMathematicianClick: (mathematician: Mathematician) => void;
  visible: boolean;
}

// Enhanced custom marker icons with event indicators
const createCustomIcon = (color: string, size: 'small' | 'medium' | 'large', eventCount: number = 0) => {
  const sizeMap = {
    small: 24,
    medium: 32,
    large: 42
  };
  
  const currentSize = sizeMap[size];
  const indicatorSize = Math.max(8, currentSize * 0.2);
  
  return L.divIcon({
    className: 'enhanced-mathematician-marker',
    html: `
      <div style="
        position: relative;
        width: ${currentSize}px;
        height: ${currentSize}px;
        background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%);
        border: 3px solid #c9b037;
        border-radius: 50%;
        box-shadow: 0 3px 12px rgba(0,0,0,0.4), 0 1px 4px rgba(201,176,55,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${currentSize * 0.35}px;
        font-family: serif;
        transition: transform 0.2s ease;
      ">
        𝕄
        ${eventCount > 3 ? `
          <div style="
            position: absolute;
            top: -4px;
            right: -4px;
            width: ${indicatorSize}px;
            height: ${indicatorSize}px;
            background: #FF6B6B;
            border: 2px solid white;
            border-radius: 50%;
            font-size: ${indicatorSize * 0.6}px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
          ">
            ${eventCount > 9 ? '9+' : eventCount}
          </div>
        ` : ''}
      </div>
    `,
    iconSize: [currentSize + 8, currentSize + 8],
    iconAnchor: [(currentSize + 8) / 2, (currentSize + 8) / 2]
  });
};

// Get marker color based on event type
const getEventTypeColor = (events: TimelineEvent[], year: number): string => {
  const relevantEvents = events.filter(event => {
    const eventYear = typeof event.year === 'string' ? parseInt(event.year, 10) : event.year;
    return Math.abs(eventYear - year) <= 5; // Show events within 5 years
  });
  
  if (relevantEvents.length === 0) return '#8B7355'; // Default sage green
  
  const eventTypes = relevantEvents.map(e => e.event_type);
  
  if (eventTypes.includes('birth')) return '#d4a574'; // Dusty rose
  if (eventTypes.includes('death')) return '#5d6d7e'; // Muted gray
  if (eventTypes.includes('publication')) return '#b0c4de'; // Powder blue
  if (eventTypes.includes('position')) return '#c9b037'; // Antique gold
  if (eventTypes.includes('education')) return '#8FBC8F'; // Light sage
  if (eventTypes.includes('travel')) return '#DDA0DD'; // Plum
  if (eventTypes.includes('collaboration')) return '#F0E68C'; // Khaki
  if (eventTypes.includes('award')) return '#FFD700'; // Gold
  
  return '#8B7355'; // Default sage green
};

// Get marker size based on popularity
const getMarkerSize = (popularity: string): 'small' | 'medium' | 'large' => {
  switch (popularity) {
    case 'very_high': return 'large';
    case 'high': 
    case 'medium': return 'medium';
    default: return 'small';
  }
};

const PeopleLayer: React.FC<PeopleLayerProps> = ({
  mathematicians,
  locations,
  selectedYear,
  onMathematicianClick,
  visible
}) => {

  // Get mathematician's location for the selected year
  const getMathematicianLocation = (mathematician: Mathematician) => {
    const relevantEvents = mathematician.timeline_events?.filter(event => {
      if (!event.location?.place_name) return false;
      const eventYear = typeof event.year === 'string' ? parseInt(event.year, 10) : event.year;
      return Math.abs(eventYear - selectedYear) <= 10;
    }) || [];
    
    if (relevantEvents.length === 0) {
      // Fallback to birth location or first known location
      const birthEvent = mathematician.timeline_events?.find(e => e.event_type === 'birth');
      if (birthEvent?.location?.place_name) {
        const locationData = locations[birthEvent.location.place_name];
        if (locationData) {
          return {
            lat: locationData.coordinates.lat,
            lng: locationData.coordinates.lng,
            place: birthEvent.location.place_name
          };
        }
      }
      return null;
    }
    
    // Use the most recent event location
    const mostRecentEvent = relevantEvents.sort((a, b) => {
      const aYear = typeof a.year === 'string' ? parseInt(a.year, 10) : a.year;
      const bYear = typeof b.year === 'string' ? parseInt(b.year, 10) : b.year;
      return Math.abs(aYear - selectedYear) - Math.abs(bYear - selectedYear);
    })[0];
    
    if (mostRecentEvent.location?.place_name) {
      const locationData = locations[mostRecentEvent.location.place_name];
      if (locationData) {
        return {
          lat: locationData.coordinates.lat,
          lng: locationData.coordinates.lng,
          place: mostRecentEvent.location.place_name
        };
      }
    }
    
    return null;
  };

  const visibleMathematicians = mathematicians.map(mathematician => {
    const location = getMathematicianLocation(mathematician);
    if (!location) return null;
    
    const events = mathematician.timeline_events || [];
    const color = getEventTypeColor(events, selectedYear);
    const size = getMarkerSize(mathematician.popularity_tier);
    
    return {
      mathematician,
      location,
      color,
      size,
      icon: createCustomIcon(color, size, events.length)
    };
  }).filter((item): item is NonNullable<typeof item> => item !== null);

  // Create Leaflet markers for clustering
  const leafletMarkers = useMemo(() => {
    return visibleMathematicians.map(item => {
      const { mathematician, location, icon } = item;
      
      // Create the popup HTML content
      const popupContent = `
        <div style="font-family: serif; color: #2c3e50; min-width: 280px;">
          <h3 style="margin: 0 0 8px 0; color: #c9b037; font-size: 1.1em;">
            ${mathematician.name}
          </h3>
          <p style="margin: 4px 0; font-size: 0.85em; color: #5d6d7e; font-style: italic;">
            ${mathematician.birth_year}-${mathematician.death_year} • ${mathematician.nationality}
          </p>
          <p style="margin: 6px 0; font-size: 0.9em;">
            <strong>Current Location:</strong> ${location.place}
          </p>
          <p style="margin: 6px 0; font-size: 0.9em;">
            <strong>Fields:</strong> ${mathematician.fields.join(', ')}
          </p>
          
          ${mathematician.timeline_events && mathematician.timeline_events.length > 0 ? `
            <div style="margin: 8px 0; padding: 6px 0; border-top: 1px solid rgba(201, 176, 55, 0.3);">
              <p style="margin: 0 0 4px 0; font-size: 0.85em; font-weight: bold; color: #8B4513;">
                Recent Timeline Events:
              </p>
              ${mathematician.timeline_events
                .filter(event => {
                  const eventYear = typeof event.year === 'string' ? parseInt(event.year.split('-')[0], 10) : event.year;
                  return Math.abs(eventYear - selectedYear) <= 5;
                })
                .slice(0, 2)
                .map((event, idx) => {
                  const eventYear = typeof event.year === 'string' ? event.year : event.year.toString();
                  const eventTypeColors: Record<string, string> = {
                    birth: '#d4a574',
                    death: '#5d6d7e', 
                    publication: '#b0c4de',
                    position: '#c9b037',
                    education: '#8FBC8F',
                    travel: '#DDA0DD',
                    collaboration: '#F0E68C',
                    award: '#FFD700',
                    other: '#8B7355'
                  };
                  return `
                    <div style="margin: 2px 0; font-size: 0.8em; padding-left: 8px; border-left: 3px solid ${eventTypeColors[event.event_type] || '#8B7355'}">
                      <strong style="color: ${eventTypeColors[event.event_type] || '#8B7355'}">
                        ${eventYear}:
                      </strong> ${event.description.substring(0, 60)}...
                    </div>
                  `;
                }).join('')}
              ${mathematician.timeline_events.length > 2 ? `
                <p style="margin: 4px 0 0 0; font-size: 0.75em; color: #888;">
                  +${mathematician.timeline_events.length - 2} more events
                </p>
              ` : ''}
            </div>
          ` : ''}
          
          <p style="margin: 8px 0 0 0; font-size: 0.75em; font-style: italic; color: #5d6d7e; text-align: center;">
            Click marker for complete biography
          </p>
        </div>
      `;

      // Create Leaflet marker
      const marker = L.marker([location.lat, location.lng], { icon });
      
      // Bind popup
      marker.bindPopup(popupContent);
      
      // Add click event handler
      marker.on('click', () => {
        onMathematicianClick(mathematician);
      });

      return marker;
    });
  }, [visibleMathematicians, selectedYear, onMathematicianClick]);

  if (!visible) return null;

  return (
    <>
      <MarkerClusterGroup 
        markers={leafletMarkers}
        maxClusterRadius={60}
        spiderfyOnMaxZoom={true}
        showCoverageOnHover={false}
        zoomToBoundsOnClick={true}
        removeOutsideVisibleBounds={true}
      />
    </>
  );
};

export default PeopleLayer;