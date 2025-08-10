import React from 'react';
import { Box, Slider, Typography, Paper, Chip } from '@mui/material';
import { TimelineSliderProps } from '../../types';

const TimelineSlider: React.FC<TimelineSliderProps> = ({
  selectedYear,
  onYearChange,
  mathematicians,
  onMathematicianClick
}) => {
  // Define the 18th century range
  const MIN_YEAR = 1700;
  const MAX_YEAR = 1800;
  
  // Create decade marks
  const marks = [];
  for (let year = MIN_YEAR; year <= MAX_YEAR; year += 10) {
    marks.push({
      value: year,
      label: `${year}s`
    });
  }

  // Count active mathematicians for current year
  const activeMathematicians = mathematicians.filter(m => 
    m.birth_year <= selectedYear && m.death_year >= selectedYear
  );

  // Get activity indicators for timeline
  const getActivityForYear = (year: number) => {
    return mathematicians.filter(m => 
      m.birth_year <= year && m.death_year >= year
    ).length;
  };

  return (
    <Paper
      elevation={8}
      className="timeline-container"
      sx={{
        position: 'absolute',
        bottom: 32,
        left: '50%',
        transform: 'translateX(-50%)',
        background: 'rgba(232, 232, 232, 0.95)', // Pearl Gray
        backdropFilter: 'blur(10px)',
        padding: '20px 32px',
        borderRadius: 4,
        minWidth: '600px',
        maxWidth: '80vw',
        zIndex: 1000,
        border: '2px solid #d4a574' // Dusty Rose border
      }}
    >
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6" sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
          Timeline: {selectedYear}
        </Typography>
        <Box display="flex" gap={1} alignItems="center">
          <Typography variant="body2" sx={{ color: '#5d6d7e' }}>
            Active mathematicians:
          </Typography>
          <Chip 
            label={activeMathematicians.length}
            size="small"
            sx={{ 
              backgroundColor: '#c9b037', // Antique Gold
              color: 'white',
              fontWeight: 'bold'
            }}
          />
        </Box>
      </Box>

      {/* Activity Heat Map Visualization */}
      <Box mb={3}>
        <Box display="flex" height="4px" borderRadius={2} overflow="hidden">
          {Array.from({ length: MAX_YEAR - MIN_YEAR + 1 }, (_, i) => {
            const year = MIN_YEAR + i;
            const activity = getActivityForYear(year);
            const intensity = activity / Math.max(1, Math.max(...Array.from({ length: 101 }, (_, j) => getActivityForYear(MIN_YEAR + j))));
            
            return (
              <Box
                key={year}
                sx={{
                  flex: 1,
                  backgroundColor: activity > 0 
                    ? `rgba(201, 176, 55, ${Math.max(0.3, intensity)})` // Antique Gold with opacity
                    : 'rgba(212, 165, 116, 0.2)', // Dusty Rose with low opacity
                  transition: 'all 0.2s'
                }}
              />
            );
          })}
        </Box>
        <Typography variant="caption" sx={{ color: '#5d6d7e', mt: 0.5 }}>
          Mathematical activity heat map
        </Typography>
      </Box>

      {/* Main Slider */}
      <Box px={2}>
        <Slider
          value={selectedYear}
          onChange={(_, value) => onYearChange(value as number)}
          min={MIN_YEAR}
          max={MAX_YEAR}
          step={1}
          marks={marks}
          valueLabelDisplay="on"
          valueLabelFormat={(value) => `${value}`}
          sx={{
            color: '#c9b037', // Antique Gold
            height: 8,
            '& .MuiSlider-track': {
              border: 'none',
              background: 'linear-gradient(45deg, #c9b037 30%, #d4a574 90%)' // Antique Gold to Dusty Rose
            },
            '& .MuiSlider-thumb': {
              height: 24,
              width: 24,
              backgroundColor: '#fff',
              border: '2px solid currentColor',
              '&:focus, &:hover, &.Mui-active': {
                boxShadow: 'inherit',
                transform: 'scale(1.2)'
              }
            },
            '& .MuiSlider-valueLabel': {
              lineHeight: 1.2,
              fontSize: 12,
              background: 'unset',
              padding: 0,
              width: 32,
              height: 32,
              borderRadius: '50% 50% 50% 0',
              backgroundColor: '#c9b037', // Antique Gold
              transformOrigin: 'bottom left',
              transform: 'translate(50%, -100%) rotate(-45deg) scale(0)',
              '&:before': { display: 'none' },
              '&.MuiSlider-valueLabelOpen': {
                transform: 'translate(50%, -100%) rotate(-45deg) scale(1)',
              },
              '& > *': {
                transform: 'rotate(45deg)',
              },
            },
            '& .MuiSlider-mark': {
              backgroundColor: 'rgba(44, 62, 80, 0.4)', // Dark text color with opacity
              height: 4,
              width: 2,
              '&.MuiSlider-markActive': {
                backgroundColor: 'currentColor',
                opacity: 1,
              },
            },
            '& .MuiSlider-markLabel': {
              fontSize: '0.75rem',
              color: '#5d6d7e', // Secondary text color
              '&.MuiSlider-markLabelActive': {
                color: '#c9b037', // Antique Gold
              },
            },
          }}
        />
      </Box>

      {/* Active Mathematicians List */}
      {activeMathematicians.length > 0 && (
        <Box mt={3}>
          <Typography variant="body2" sx={{ color: '#5d6d7e', mb: 1 }}>
            Active in {selectedYear}:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {activeMathematicians.map(mathematician => (
              <Chip
                key={mathematician.id}
                label={mathematician.name}
                size="small"
                variant="outlined"
                clickable
                onClick={() => onMathematicianClick?.(mathematician)}
                sx={{
                  color: '#2c3e50', // Dark text
                  borderColor: '#d4a574', // Dusty Rose border
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(212, 165, 116, 0.15)', // Light dusty rose hover
                    borderColor: '#c9b037', // Antique gold on hover
                    transform: 'translateY(-1px)',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
                  },
                  '&:active': {
                    transform: 'translateY(0px)'
                  }
                }}
              />
            ))}
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default TimelineSlider;