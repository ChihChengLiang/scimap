import React from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  Link,
  Divider
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot
} from '@mui/lab';
import {
  Close as CloseIcon,
  School as SchoolIcon,
  Work as WorkIcon,
  LocationOn as LocationIcon,
  MenuBook as BookIcon,
  Flight as FlightIcon,
  Person as PersonIcon,
  AccessTime as TimelineIconMaterial,
  Group as GroupIcon,
  EmojiEvents as AwardIcon
} from '@mui/icons-material';
import { MathematicianPanelProps, TimelineEvent } from '../../types';

const EVENT_ICONS: Record<string, any> = {
  birth: PersonIcon,
  education: SchoolIcon,
  position: WorkIcon,
  publication: BookIcon,
  travel: FlightIcon,
  death: PersonIcon,
  collaboration: GroupIcon,
  award: AwardIcon,
  career: WorkIcon,
  other: TimelineIconMaterial
};

const EVENT_COLORS: Record<string, string> = {
  birth: '#4caf50',
  education: '#2196f3', 
  position: '#ff9800',
  publication: '#9c27b0',
  travel: '#00bcd4',
  death: '#f44336',
  collaboration: '#e91e63',
  award: '#ffc107',
  career: '#ff6b35',
  other: '#607d8b'
};

const POPULARITY_COLORS = {
  very_high: '#c9b037', // Antique Gold
  high: '#d4a574',      // Dusty Rose  
  medium: '#8b7355',    // Darker gold
  low: '#9bb0c1',       // Muted powder blue
  very_low: '#b8860b'   // Dark golden rod
};

const MathematicianPanel: React.FC<MathematicianPanelProps> = ({
  mathematician,
  locations,
  onClose
}) => {
  const formatEventYear = (year: number | string) => {
    if (typeof year === 'number') return year.toString();
    return year.replace('-', '–'); // en dash for ranges
  };

  const getLocationInfo = (event: TimelineEvent) => {
    if (!event.location.place_name) return null;
    
    const locationData = locations[event.location.place_name];
    return locationData;
  };

  return (
    <Paper
      elevation={12}
      className="mathematician-panel"
      sx={{
        position: 'absolute',
        top: 24,
        right: 24,
        width: 400,
        maxWidth: '40vw',
        maxHeight: 'calc(100vh - 48px)',
        background: 'rgba(232, 232, 232, 0.98)', // Pearl Gray
        backdropFilter: 'blur(20px)',
        borderRadius: 3,
        overflow: 'hidden',
        zIndex: 2000
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 3,
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: `linear-gradient(135deg, ${POPULARITY_COLORS[mathematician.popularity_tier]}22 0%, transparent 100%)`
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Typography variant="h5" sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
            {mathematician.name}
          </Typography>
          <IconButton 
            onClick={onClose}
            size="small"
            sx={{ color: '#5d6d7e' }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
        
        <Typography variant="body1" sx={{ color: '#5d6d7e', mb: 2 }}>
          {mathematician.birth_year} – {mathematician.death_year} • {mathematician.nationality}
        </Typography>
        
        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          {mathematician.fields.map(field => (
            <Chip
              key={field}
              label={field}
              size="small"
              variant="outlined"
              sx={{
                color: '#2c3e50',
                borderColor: '#d4a574', // Dusty Rose
                fontSize: '0.75rem'
              }}
            />
          ))}
        </Box>

        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={`${mathematician.popularity_tier.replace('_', ' ')} popularity`}
            size="small"
            sx={{
              backgroundColor: POPULARITY_COLORS[mathematician.popularity_tier],
              color: 'white',
              fontWeight: 'bold'
            }}
          />
          <Typography variant="caption" sx={{ color: '#5d6d7e' }}>
            {mathematician.page_views.toLocaleString()} page views
          </Typography>
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
        {/* Timeline Events */}
        <Box p={3}>
          <Typography variant="h6" sx={{ color: '#2c3e50', mb: 2 }} display="flex" alignItems="center" gap={1}>
            <TimelineIconMaterial fontSize="small" />
            Timeline Events
          </Typography>
          
          {mathematician.timeline_events.length > 0 ? (
            <Timeline sx={{ p: 0 }}>
              {mathematician.timeline_events
                .sort((a, b) => {
                  const yearA = typeof a.year === 'number' ? a.year : parseInt(a.year.toString().split('-')[0]);
                  const yearB = typeof b.year === 'number' ? b.year : parseInt(b.year.toString().split('-')[0]);
                  return yearA - yearB;
                })
                .map((event, index) => {
                  const IconComponent = EVENT_ICONS[event.event_type] || EVENT_ICONS.other;
                  const locationInfo = getLocationInfo(event);
                  
                  return (
                    <TimelineItem key={index}>
                      <TimelineSeparator>
                        <TimelineDot sx={{ backgroundColor: EVENT_COLORS[event.event_type] || EVENT_COLORS.other }}>
                          <IconComponent sx={{ fontSize: 16, color: 'white' }} />
                        </TimelineDot>
                        {index < mathematician.timeline_events.length - 1 && (
                          <TimelineConnector sx={{ bgcolor: 'rgba(44, 62, 80, 0.3)' }} />
                        )}
                      </TimelineSeparator>
                      
                      <TimelineContent sx={{ pb: 3 }}>
                        <Box>
                          <Typography variant="body2" sx={{ color: '#2c3e50', fontWeight: 'bold' }}>
                            {formatEventYear(event.year)} • {event.event_type}
                          </Typography>
                          
                          <Typography variant="body2" sx={{ color: '#5d6d7e', mt: 0.5 }}>
                            {event.description}
                          </Typography>
                          
                          {event.location.place_name && (
                            <Box mt={1} display="flex" alignItems="center" gap={1}>
                              <LocationIcon sx={{ fontSize: 14, color: '#d4a574' }} />
                              <Typography variant="caption" sx={{ color: '#5d6d7e' }}>
                                {event.location.place_name}
                                {locationInfo && (
                                  <span> • {locationInfo.historical_context}</span>
                                )}
                              </Typography>
                            </Box>
                          )}
                          
                          <Typography variant="caption" sx={{ color: '#8b7355', mt: 1 }} display="block">
                            Confidence: {Math.round(event.confidence * 100)}%
                          </Typography>
                        </Box>
                      </TimelineContent>
                    </TimelineItem>
                  );
                })}
            </Timeline>
          ) : (
            <Typography sx={{ color: '#5d6d7e' }}>
              No timeline events extracted yet.
            </Typography>
          )}
        </Box>

        <Divider sx={{ borderColor: 'rgba(44, 62, 80, 0.2)' }} />

        {/* Links */}
        <Box p={3}>
          <Typography variant="h6" sx={{ color: '#2c3e50', mb: 2 }}>
            Learn More
          </Typography>
          <Link
            href={mathematician.wikipedia_url}
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              color: '#c9b037', // Antique Gold
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              '&:hover': {
                textDecoration: 'underline',
                color: '#d4a574' // Dusty Rose on hover
              }
            }}
          >
            <BookIcon fontSize="small" />
            Wikipedia Article
          </Link>
        </Box>

        {/* Metadata */}
        <Box p={3} pt={0}>
          <Typography variant="caption" sx={{ color: '#8b7355' }}>
            Data processed: {new Date(mathematician.processed_at).toLocaleDateString()}
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
};

export default MathematicianPanel;