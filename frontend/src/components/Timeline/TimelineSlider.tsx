import React, { useState } from 'react';
import { Box, Slider, Typography, Paper, Chip, IconButton, Collapse } from '@mui/material';
import { ExpandMore, ExpandLess } from '@mui/icons-material';
import { TimelineSliderProps } from '../../types';

const TimelineSlider: React.FC<TimelineSliderProps> = ({
  selectedYear,
  onYearChange,
  mathematicians,
  politicalContexts,
  onMathematicianClick
}) => {
  // State for collapsible sections
  const [mathematiciansExpanded, setMathematiciansExpanded] = useState(true);
  const [politicalExpanded, setPoliticalExpanded] = useState(true);

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

  // Get political events for current year (within 5 years for timeline display)
  const relevantPoliticalEvents = politicalContexts.filter(event => 
    Math.abs(event.year - selectedYear) <= 5
  ).sort((a, b) => Math.abs(a.year - selectedYear) - Math.abs(b.year - selectedYear))
    .slice(0, 3); // Show only top 3 most relevant events

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
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="body2" sx={{ color: '#5d6d7e', mb: 1 }}>
              Active in {selectedYear}:
            </Typography>
            <IconButton
              size="small"
              onClick={() => setMathematiciansExpanded(!mathematiciansExpanded)}
              sx={{
                color: '#5d6d7e',
                '&:hover': {
                  backgroundColor: 'rgba(212, 165, 116, 0.1)',
                  color: '#c9b037'
                }
              }}
            >
              {mathematiciansExpanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          <Collapse in={mathematiciansExpanded}>
            <Box 
              sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 1,
                maxHeight: '120px', // Fixed height to prevent overwhelming the screen
                overflowY: 'auto',  // Enable vertical scrolling
                overflowX: 'hidden',
                padding: '4px', // Small padding to prevent chips from touching the scrollbar
                // Custom scrollbar styling
                '&::-webkit-scrollbar': {
                  width: '6px',
                },
                '&::-webkit-scrollbar-track': {
                  background: 'rgba(212, 165, 116, 0.1)', // Light dusty rose track
                  borderRadius: '3px',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: 'rgba(201, 176, 55, 0.6)', // Antique gold thumb
                  borderRadius: '3px',
                  '&:hover': {
                    background: 'rgba(201, 176, 55, 0.8)', // Darker on hover
                  },
                },
              }}
            >
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
                    flexShrink: 0, // Prevent chips from shrinking when scrolling
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
          </Collapse>
        </Box>
      )}

      {/* Political Events Section */}
      {relevantPoliticalEvents.length > 0 && (
        <Box mt={2}>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="body2" sx={{ color: '#5d6d7e', mb: 1, fontSize: '0.85rem' }}>
              🏛️ Political Context ({selectedYear}):
            </Typography>
            <IconButton
              size="small"
              onClick={() => setPoliticalExpanded(!politicalExpanded)}
              sx={{
                color: '#5d6d7e',
                '&:hover': {
                  backgroundColor: 'rgba(139, 69, 19, 0.1)',
                  color: '#8B4513'
                }
              }}
            >
              {politicalExpanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
          <Collapse in={politicalExpanded}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {relevantPoliticalEvents.map(event => {
                const yearDiff = Math.abs(event.year - selectedYear);
                const opacity = yearDiff === 0 ? 1.0 : yearDiff === 1 ? 0.8 : 0.6;
                const getCategoryColor = (category: string) => {
                  switch (category) {
                    case 'war': return '#DC143C';
                    case 'political_change': return '#8B4513';
                    case 'treaty': return '#228B22';
                    case 'royal_succession': return '#FFD700';
                    case 'intellectual_milestone': return '#9370DB';
                    default: return '#696969';
                  }
                };

                return (
                  <Box 
                    key={event.id}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      opacity: opacity,
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: 'rgba(139, 69, 19, 0.05)',
                      border: '1px solid rgba(139, 69, 19, 0.1)',
                      fontSize: '0.75rem'
                    }}
                  >
                    <Box
                      sx={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        backgroundColor: getCategoryColor(event.category),
                        flexShrink: 0
                      }}
                    />
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#8B4513', 
                        fontWeight: 'bold',
                        minWidth: '32px'
                      }}
                    >
                      {event.year}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#2c3e50',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        flex: 1
                      }}
                      title={`${event.headline}: ${event.impact_on_science}`}
                    >
                      {event.headline}
                    </Typography>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: '#5d6d7e',
                        fontSize: '0.7rem',
                        opacity: 0.8
                      }}
                    >
                      {Math.round(event.relevance_score * 100)}%
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          </Collapse>
        </Box>
      )}
    </Paper>
  );
};

export default TimelineSlider;