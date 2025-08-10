import React from 'react';
import { Box, ToggleButton, Paper, Typography } from '@mui/material';
import { People, AccountBalance } from '@mui/icons-material';
import { LayerVisibility } from '../../types';

interface LayerControlsProps {
  layerVisibility: LayerVisibility;
  onLayerToggle: (layer: keyof LayerVisibility) => void;
}

const LayerControls: React.FC<LayerControlsProps> = ({
  layerVisibility,
  onLayerToggle
}) => {
  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        top: 80,
        right: 24,
        zIndex: 1000,
        padding: '12px 16px',
        background: 'rgba(245, 245, 220, 0.95)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(201, 176, 55, 0.3)',
        borderRadius: '8px',
        minWidth: '160px'
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{
          color: '#2c3e50',
          fontFamily: 'serif',
          fontWeight: 'bold',
          marginBottom: '8px',
          textAlign: 'center'
        }}
      >
        Map Layers
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {/* People Layer Toggle */}
        <ToggleButton
          value="people"
          selected={layerVisibility.people}
          onChange={() => onLayerToggle('people')}
          sx={{
            padding: '8px 12px',
            border: '1px solid rgba(201, 176, 55, 0.4)',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontFamily: 'serif',
            color: layerVisibility.people ? '#c9b037' : '#5d6d7e',
            backgroundColor: layerVisibility.people ? 'rgba(201, 176, 55, 0.1)' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(201, 176, 55, 0.05)',
              border: '1px solid rgba(201, 176, 55, 0.6)',
            },
            '&.Mui-selected': {
              backgroundColor: 'rgba(201, 176, 55, 0.15)',
              border: '1px solid #c9b037',
              '&:hover': {
                backgroundColor: 'rgba(201, 176, 55, 0.2)',
              }
            }
          }}
        >
          <People sx={{ fontSize: 16, marginRight: '6px' }} />
          Mathematicians
        </ToggleButton>

        {/* Political Layer Toggle */}
        <ToggleButton
          value="political"
          selected={layerVisibility.political}
          onChange={() => onLayerToggle('political')}
          sx={{
            padding: '8px 12px',
            border: '1px solid rgba(139, 69, 19, 0.4)',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontFamily: 'serif',
            color: layerVisibility.political ? '#8B4513' : '#5d6d7e',
            backgroundColor: layerVisibility.political ? 'rgba(139, 69, 19, 0.1)' : 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(139, 69, 19, 0.05)',
              border: '1px solid rgba(139, 69, 19, 0.6)',
            },
            '&.Mui-selected': {
              backgroundColor: 'rgba(139, 69, 19, 0.15)',
              border: '1px solid #8B4513',
              '&:hover': {
                backgroundColor: 'rgba(139, 69, 19, 0.2)',
              }
            }
          }}
        >
          <AccountBalance sx={{ fontSize: 16, marginRight: '6px' }} />
          Political Context
        </ToggleButton>
      </Box>

      {/* Layer Legend */}
      <Box sx={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px solid rgba(201, 176, 55, 0.2)' }}>
        <Typography
          variant="caption"
          sx={{
            color: '#5d6d7e',
            fontFamily: 'serif',
            fontStyle: 'italic',
            fontSize: '0.75rem',
            lineHeight: '1.2'
          }}
        >
          Toggle layers to explore mathematical and historical context separately or together
        </Typography>
      </Box>
    </Paper>
  );
};

export default LayerControls;