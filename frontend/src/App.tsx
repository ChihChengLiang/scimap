import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import HistoricalMap from './components/Map/HistoricalMap';
import TimelineSlider from './components/Timeline/TimelineSlider';
import MathematicianPanel from './components/MathematicianPanel/MathematicianPanel';
import { Mathematician, LocationData, PoliticalContext, LayerVisibility } from './types';
import LayerControls from './components/LayerControls/LayerControls';
import './App.css';

const rococoTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#b0c4de', // Powder Blue
      paper: 'rgba(232, 232, 232, 0.95)' // Pearl Gray with transparency
    },
    primary: {
      main: '#c9b037' // Antique Gold
    },
    secondary: {
      main: '#d4a574' // Dusty Rose
    },
    text: {
      primary: '#2c3e50', // Dark text for readability on light backgrounds
      secondary: '#5d6d7e'
    }
  },
  typography: {
    fontFamily: 'Roboto, serif',
    h1: { color: '#2c3e50' },
    h6: { color: '#2c3e50' }
  }
});

function App() {
  const [mathematicians, setMathematicians] = useState<Record<string, Mathematician>>({});
  const [locations, setLocations] = useState<Record<string, LocationData>>({});
  const [politicalContexts, setPoliticalContexts] = useState<PoliticalContext[]>([]);
  const [selectedYear, setSelectedYear] = useState<number>(1750);
  const [selectedMathematician, setSelectedMathematician] = useState<Mathematician | null>(null);
  const [layerVisibility, setLayerVisibility] = useState<LayerVisibility>({
    people: true,
    political: true
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load data on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [mathematiciansRes, locationsRes, politicalRes] = await Promise.all([
          fetch(`${process.env.PUBLIC_URL}/data/mathematicians.json`),
          fetch(`${process.env.PUBLIC_URL}/data/locations.json`),
          fetch(`${process.env.PUBLIC_URL}/data/political_events.json`)
        ]);

        if (!mathematiciansRes.ok || !locationsRes.ok || !politicalRes.ok) {
          throw new Error('Failed to load data');
        }

        const mathematiciansData = await mathematiciansRes.json();
        const locationsData = await locationsRes.json();
        const politicalData = await politicalRes.json();

        setMathematicians(mathematiciansData);
        setLocations(locationsData);
        setPoliticalContexts(politicalData); // Already an array
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Filter mathematicians visible in current year
  const getVisibleMathematicians = () => {
    return Object.values(mathematicians).filter(mathematician => {
      // Show if mathematician was alive in selected year
      return mathematician.birth_year <= selectedYear && 
             mathematician.death_year >= selectedYear;
    });
  };

  const handleMathematicianClick = (mathematician: Mathematician) => {
    setSelectedMathematician(mathematician);
  };

  const handleClosePanel = () => {
    setSelectedMathematician(null);
  };

  const handleLayerToggle = (layer: keyof LayerVisibility) => {
    setLayerVisibility(prev => ({
      ...prev,
      [layer]: !prev[layer]
    }));
  };

  if (loading) {
    return (
      <ThemeProvider theme={rococoTheme}>
        <CssBaseline />
        <Box 
          display="flex" 
          alignItems="center" 
          justifyContent="center" 
          height="100vh"
          color="#2c3e50"
          fontSize="1.2rem"
          bgcolor="#b0c4de"
        >
          Loading 18th century mathematical timeline...
        </Box>
      </ThemeProvider>
    );
  }

  if (error) {
    return (
      <ThemeProvider theme={rococoTheme}>
        <CssBaseline />
        <Box 
          display="flex" 
          alignItems="center" 
          justifyContent="center" 
          height="100vh"
          color="#d4a574"
          fontSize="1.2rem"
          bgcolor="#b0c4de"
        >
          Error: {error}
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={rococoTheme}>
      <CssBaseline />
      <div className="App">
        <Box sx={{ position: 'relative', height: '100vh', overflow: 'hidden', bgcolor: '#b0c4de' }}>
          {/* Historical Map */}
          <HistoricalMap 
            mathematicians={getVisibleMathematicians()}
            locations={locations}
            politicalContexts={politicalContexts}
            selectedYear={selectedYear}
            layerVisibility={layerVisibility}
            onMathematicianClick={handleMathematicianClick}
          />
          
          {/* Layer Controls */}
          <LayerControls
            layerVisibility={layerVisibility}
            onLayerToggle={handleLayerToggle}
          />
          
          {/* Timeline Slider */}
          <TimelineSlider
            selectedYear={selectedYear}
            onYearChange={setSelectedYear}
            mathematicians={Object.values(mathematicians)}
            politicalContexts={politicalContexts}
            onMathematicianClick={handleMathematicianClick}
          />
          
          {/* Mathematician Detail Panel */}
          {selectedMathematician && (
            <MathematicianPanel
              mathematician={selectedMathematician}
              locations={locations}
              onClose={handleClosePanel}
            />
          )}
          
          {/* Title */}
          <Box
            sx={{
              position: 'absolute',
              top: 24,
              left: 24,
              zIndex: 1000,
              color: 'white'
            }}
          >
            <h1 className="app-title" style={{ margin: 0, fontSize: '1.5rem', color: '#2c3e50', fontWeight: 'bold' }}>
              18th Century Mathematics
            </h1>
            <p className="app-subtitle" style={{ margin: '4px 0 0 0', opacity: 0.8, fontSize: '0.9rem', color: '#5d6d7e' }}>
              Interactive Timeline: {selectedYear}
            </p>
          </Box>
        </Box>
      </div>
    </ThemeProvider>
  );
}

export default App;