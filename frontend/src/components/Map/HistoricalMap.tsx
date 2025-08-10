import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import { HistoricalMapProps } from '../../types';
import PeopleLayer from './PeopleLayer';
import PoliticalLayer from './PoliticalLayer';
import 'leaflet/dist/leaflet.css';
import './HistoricalMap.css';


// Component to handle map styling
const MapStyling: React.FC = () => {
  const map = useMap();
  
  useEffect(() => {
    // Apply custom CSS styling to the map container
    const mapContainer = map.getContainer();
    mapContainer.style.filter = 'sepia(20%) saturate(80%) contrast(90%)';
    mapContainer.style.background = '#f5f5dc'; // Cream background
  }, [map]);
  
  return null;
};

const HistoricalMap: React.FC<HistoricalMapProps> = ({
  mathematicians,
  locations,
  politicalContexts,
  selectedYear,
  layerVisibility,
  onMathematicianClick
}) => {
  const mapRef = useRef<L.Map | null>(null);

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      <MapContainer
        center={[50.0, 10.0]} // Center on Europe
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        attributionControl={false}
      >
        {/* Custom OpenStreetMap tile layer with Rococo styling */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© OpenStreetMap contributors'
          opacity={0.8}
        />
        
        <MapStyling />
        
        {/* People Layer - Mathematician markers */}
        <PeopleLayer
          mathematicians={mathematicians}
          locations={locations}
          selectedYear={selectedYear}
          onMathematicianClick={onMathematicianClick}
          visible={layerVisibility.people}
        />
        
        {/* Political Layer - Historical context markers */}
        <PoliticalLayer
          politicalContexts={politicalContexts}
          selectedYear={selectedYear}
          visible={layerVisibility.political}
        />
      </MapContainer>
    </div>
  );
};

export default HistoricalMap;