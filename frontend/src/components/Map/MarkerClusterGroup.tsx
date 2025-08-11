import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.markercluster';

interface MarkerClusterGroupProps {
  markers: L.Marker[];
  chunkedLoading?: boolean;
  maxClusterRadius?: number;
  spiderfyOnMaxZoom?: boolean;
  showCoverageOnHover?: boolean;
  zoomToBoundsOnClick?: boolean;
  removeOutsideVisibleBounds?: boolean;
}

const MarkerClusterGroup: React.FC<MarkerClusterGroupProps> = ({
  markers,
  chunkedLoading = false,
  maxClusterRadius = 50, // Smaller radius for better separation
  spiderfyOnMaxZoom = true,
  showCoverageOnHover = false, // Disable to reduce visual clutter
  zoomToBoundsOnClick = true,
  removeOutsideVisibleBounds = true, // Performance optimization
}) => {
  const map = useMap();
  const clusterGroupRef = useRef<L.MarkerClusterGroup | null>(null);
  const styleRef = useRef<HTMLStyleElement | null>(null);

  useEffect(() => {
    // Create custom CSS styling for clusters to match Rococo theme
    if (!styleRef.current) {
      const style = document.createElement('style');
      style.textContent = `
        .marker-cluster {
          background-clip: padding-box;
          border-radius: 20px;
          border: 2px solid #2c3e50;
          box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        .marker-cluster div {
          width: 36px;
          height: 36px;
          margin-left: 2px;
          margin-top: 2px;
          text-align: center;
          border-radius: 18px;
          font: 12px "Roboto", serif;
          font-weight: bold;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .marker-cluster-small {
          background-color: rgba(201, 176, 55, 0.8); /* Antique Gold */
        }
        .marker-cluster-small div {
          background-color: rgba(201, 176, 55, 1);
        }
        .marker-cluster-medium {
          background-color: rgba(212, 165, 116, 0.8); /* Dusty Rose */
        }
        .marker-cluster-medium div {
          background-color: rgba(212, 165, 116, 1);
        }
        .marker-cluster-large {
          background-color: rgba(139, 69, 19, 0.8); /* Saddle Brown */
        }
        .marker-cluster-large div {
          background-color: rgba(139, 69, 19, 1);
        }
        
        /* Spiderfy lines styling */
        .leaflet-cluster-anim .leaflet-marker-icon, .leaflet-cluster-anim .leaflet-marker-shadow {
          -webkit-transition: -webkit-transform 0.3s ease-out, opacity 0.3s ease-in;
          -moz-transition: -moz-transform 0.3s ease-out, opacity 0.3s ease-in;
          -o-transition: -o-transform 0.3s ease-out, opacity 0.3s ease-in;
          transition: transform 0.3s ease-out, opacity 0.3s ease-in;
        }
        
        /* Hide marker shadows for cleaner look */
        .leaflet-marker-shadow {
          display: none;
        }
      `;
      
      document.head.appendChild(style);
      styleRef.current = style;
    }

    // Create marker cluster group with custom styling
    const clusterGroup = L.markerClusterGroup({
      chunkedLoading,
      maxClusterRadius,
      spiderfyOnMaxZoom,
      showCoverageOnHover,
      zoomToBoundsOnClick,
      removeOutsideVisibleBounds,
      // Custom cluster icon creation
      iconCreateFunction: (cluster) => {
        const childCount = cluster.getChildCount();
        let className = 'marker-cluster-';
        
        // Style clusters based on size with Rococo theme colors
        if (childCount < 10) {
          className += 'small';
        } else if (childCount < 20) {
          className += 'medium';
        } else {
          className += 'large';
        }

        return L.divIcon({
          html: `<div class="cluster-inner"><span>${childCount}</span></div>`,
          className: `marker-cluster ${className}`,
          iconSize: L.point(40, 40)
        });
      }
    });

    clusterGroupRef.current = clusterGroup;
    map.addLayer(clusterGroup);

    return () => {
      if (clusterGroupRef.current) {
        map.removeLayer(clusterGroupRef.current);
      }
    };
  }, [map, chunkedLoading, maxClusterRadius, spiderfyOnMaxZoom, showCoverageOnHover, zoomToBoundsOnClick, removeOutsideVisibleBounds]);

  // Update markers when they change
  useEffect(() => {
    if (clusterGroupRef.current) {
      // Clear existing markers
      clusterGroupRef.current.clearLayers();
      
      // Add new markers to cluster group
      markers.forEach(marker => {
        clusterGroupRef.current?.addLayer(marker);
      });
    }
  }, [markers]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (styleRef.current) {
        document.head.removeChild(styleRef.current);
        styleRef.current = null;
      }
    };
  }, []);

  return null; // This component doesn't render anything directly
};

export default MarkerClusterGroup;