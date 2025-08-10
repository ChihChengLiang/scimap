// Data types for the SciMap application

export interface TimelineEvent {
  year: number | string;
  year_confidence: 'exact' | 'approximate' | 'range';
  event_type: 'birth' | 'education' | 'position' | 'publication' | 'travel' | 'death' | 'other';
  description: string;
  location: {
    place_name: string | null;
    raw_text: string;
    confidence: number;
    coordinates?: {
      lat: number;
      lng: number;
    };
    geocoding_confidence?: number;
    historical_context?: string;
  };
  source_text: string;
  confidence: number;
  extraction_metadata: {
    model_version: string;
    extracted_at: string;
    extraction_confidence: number;
  };
}

export interface Mathematician {
  id: string;
  name: string;
  birth_year: number;
  death_year: number;
  wikipedia_url: string;
  page_views: number;
  popularity_tier: 'very_high' | 'high' | 'medium' | 'low' | 'very_low';
  fields: string[];
  nationality: string;
  timeline_events: TimelineEvent[];
  processed_at: string;
}

export interface LocationData {
  place_name: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  confidence: number;
  historical_context: string;
  alternative_names: string[];
  modern_equivalent: string;
  geocoded_at: string;
  geocoding_method: string;
  model_version: string;
}

export interface SummaryData {
  dataset_info: {
    total_mathematicians: number;
    total_timeline_events: number;
    total_unique_locations: number;
    generated_at: string;
    pipeline_mode: string;
  };
  event_type_distribution: Record<string, number>;
  popularity_distribution: Record<string, number>;
  temporal_coverage: {
    earliest_year: number | null;
    latest_year: number | null;
    total_years_covered: number;
  };
  success_metrics: {
    avg_events_per_mathematician: number;
    locations_per_mathematician: number;
  };
}

// Globe-specific types
export interface GlobePoint {
  lat: number;
  lng: number;
  mathematician: Mathematician;
  size: number;
  color: string;
}

// Political context data types
export interface PoliticalContext {
  context_id: string;
  year: number;
  location: {
    place_name: string;
    lat: number;
    lng: number;
    region: string;
  };
  headline: string;
  description: string;
  impact_on_science: string;
  category: 'political_change' | 'war' | 'peace_treaty' | 'cultural_event' | 'economic_shift';
  source: string;
  relevance_score: number;
}

// Layer visibility state
export interface LayerVisibility {
  people: boolean;
  political: boolean;
}

// Component prop types
export interface GlobeProps {
  mathematicians: Mathematician[];
  locations: Record<string, LocationData>;
  selectedYear: number;
  onMathematicianClick: (mathematician: Mathematician) => void;
}

export interface HistoricalMapProps {
  mathematicians: Mathematician[];
  locations: Record<string, LocationData>;
  politicalContexts: PoliticalContext[];
  selectedYear: number;
  layerVisibility: LayerVisibility;
  onMathematicianClick: (mathematician: Mathematician) => void;
}

export interface TimelineSliderProps {
  selectedYear: number;
  onYearChange: (year: number) => void;
  mathematicians: Mathematician[];
}

export interface MathematicianPanelProps {
  mathematician: Mathematician;
  locations: Record<string, LocationData>;
  onClose: () => void;
}