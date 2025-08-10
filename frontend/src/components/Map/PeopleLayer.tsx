import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Mathematician, LocationData, TimelineEvent } from '../../types';

interface PeopleLayerProps {
  mathematicians: Mathematician[];
  locations: Record<string, LocationData>;
  selectedYear: number;
  onMathematicianClick: (mathematician: Mathematician) => void;
  visible: boolean;
}

// Custom marker icons for different event types
const createCustomIcon = (color: string, size: 'small' | 'medium' | 'large') => {
  const sizeMap = {
    small: 20,
    medium: 30,
    large: 40
  };
  
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        width: ${sizeMap[size]}px;
        height: ${sizeMap[size]}px;
        background-color: ${color};
        border: 3px solid #c9b037;
        border-radius: 50%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: ${sizeMap[size] * 0.3}px;
      ">
        M
      </div>
    `,
    iconSize: [sizeMap[size], sizeMap[size]],
    iconAnchor: [sizeMap[size] / 2, sizeMap[size] / 2]
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
  if (!visible) return null;

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
      icon: createCustomIcon(color, size)
    };
  }).filter((item): item is NonNullable<typeof item> => item !== null);

  return (
    <>
      {visibleMathematicians.map(item => {
        const { mathematician, location, icon } = item;
        
        return (
          <Marker
            key={mathematician.id}
            position={[location.lat, location.lng]}
            icon={icon}
            eventHandlers={{
              click: () => onMathematicianClick(mathematician)
            }}
          >
            <Popup>
              <div style={{ fontFamily: 'serif', color: '#2c3e50' }}>
                <h3 style={{ margin: '0 0 8px 0', color: '#c9b037' }}>
                  {mathematician.name}
                </h3>
                <p style={{ margin: '4px 0', fontSize: '0.9em' }}>
                  <strong>Location:</strong> {location.place}
                </p>
                <p style={{ margin: '4px 0', fontSize: '0.9em' }}>
                  <strong>Years:</strong> {mathematician.birth_year}-{mathematician.death_year}
                </p>
                <p style={{ margin: '4px 0', fontSize: '0.9em' }}>
                  <strong>Fields:</strong> {mathematician.fields.join(', ')}
                </p>
                <p style={{ 
                  margin: '8px 0 0 0', 
                  fontSize: '0.8em', 
                  fontStyle: 'italic',
                  color: '#5d6d7e'
                }}>
                  Click marker for full biography
                </p>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

export default PeopleLayer;