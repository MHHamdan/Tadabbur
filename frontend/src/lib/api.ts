import axios from 'axios';

// Use relative URL for Vite proxy, or absolute URL from env for production
const API_BASE = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Verse {
  id: number;
  sura_no: number;
  sura_name_ar: string;
  sura_name_en: string;
  aya_no: number;
  text_uthmani: string;
  text_imlaei: string;
  page_no: number;
  juz_no: number;
  translations: Translation[];
}

export interface Translation {
  language: string;
  translator: string;
  text: string;
}

export interface Story {
  id: string;
  name_ar: string;
  name_en: string;
  category: string;
  main_figures: string[];
  themes: string[];
  summary_ar: string | null;
  summary_en: string | null;
  total_verses: number;
  suras_mentioned: number[];
}

export interface StorySegment {
  id: string;
  narrative_order: number;
  segment_type: string | null;
  aspect: string | null;
  sura_no: number;
  aya_start: number;
  aya_end: number;
  verse_reference: string;
  summary_ar: string | null;
  summary_en: string | null;
}

export interface StoryDetail extends Story {
  segments: StorySegment[];
}

export interface StoryGraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, unknown>;
}

export interface StoryGraphEdge {
  source: string;
  target: string;
  type: string;
  label: string | null;
}

export interface StoryGraph {
  nodes: StoryGraphNode[];
  edges: StoryGraphEdge[];
}

export interface Citation {
  chunk_id: string;
  source_id: string;
  source_name: string;
  source_name_ar: string;
  verse_reference: string;
  excerpt: string;
  relevance_score: number;
}

export interface EvidenceChunk {
  chunk_id: string;
  source_id: string;
  source_name: string;
  source_name_ar: string;
  verse_reference: string;
  sura_no: number;
  aya_start: number;
  aya_end: number;
  content: string;
  content_ar: string | null;
  content_en: string | null;
  relevance_score: number;
  methodology: string | null;
}

export interface RAGResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  scholarly_consensus: string | null;
  warnings: string[];
  related_queries: string[];
  intent: string;
  processing_time_ms: number;
  evidence: EvidenceChunk[];
  evidence_density?: {
    chunk_count: number;
    source_count: number;
  };
}

export interface TafseerSource {
  id: string;
  name_ar: string;
  name_en: string;
  author_ar: string;
  author_en: string;
  methodology: string;
  era: string;
  language: string;
  reliability_score: number;
  is_primary_source: boolean;
  is_enabled: boolean;
}

export interface TafseerSourcesResponse {
  sources: TafseerSource[];
  count: number;
}

// API functions
export const quranApi = {
  getSuraVerses: (suraNo: number) =>
    api.get<Verse[]>(`/quran/suras/${suraNo}`),

  getVerse: (suraNo: number, ayaNo: number) =>
    api.get<Verse>(`/quran/verses/${suraNo}/${ayaNo}`),

  getVerseRange: (suraNo: number, ayaStart: number, ayaEnd: number) =>
    api.get<Verse[]>(`/quran/verses/${suraNo}/${ayaStart}/${ayaEnd}`),

  getPageVerses: (pageNo: number) =>
    api.get<Verse[]>(`/quran/page/${pageNo}`),

  getTafseer: (suraNo: number, ayaNo: number, sources?: string[]) =>
    api.get(`/quran/tafseer/${suraNo}/${ayaNo}`, { params: { sources } }),

  search: (query: string) =>
    api.get(`/quran/search`, { params: { q: query } }),
};

export const storiesApi = {
  listStories: (category?: string) =>
    api.get<Story[]>('/stories/', { params: { category } }),

  getStory: (storyId: string) =>
    api.get<StoryDetail>(`/stories/${storyId}`),

  getStoryGraph: (storyId: string, language: 'ar' | 'en' = 'en') =>
    api.get<StoryGraph>(`/stories/${storyId}/graph`, { params: { language } }),

  getCategories: () =>
    api.get('/stories/categories'),
};

// Story Atlas Types
export interface StoryCluster {
  id: string;
  title_ar: string;
  title_en: string;
  short_title_en: string | null;
  category: string;
  era: string | null;
  main_persons: string[];
  places: Record<string, unknown>[];
  tags: string[];
  event_count: number;
  primary_sura: number | null;
  summary_en: string | null;
}

export interface StoryClusterListResponse {
  clusters: StoryCluster[];
  total: number;
  offset: number;
  limit: number;
}

export interface StoryAtlasEvent {
  id: string;
  title_ar: string;
  title_en: string;
  narrative_role: string;
  chronological_index: number;
  sura_no: number;
  aya_start: number;
  aya_end: number;
  verse_reference: string;
  summary_ar: string;
  summary_en: string;
  semantic_tags: string[];
  is_entry_point: boolean;
  evidence: Record<string, unknown>[];
}

export interface StoryClusterDetail extends StoryCluster {
  short_title_ar: string | null;
  groups: string[];
  era_basis: string;
  time_description_en: string | null;
  ayah_spans: Record<string, unknown>[];
  suras_mentioned: number[] | null;
  summary_ar: string | null;
  lessons_ar: string[] | null;
  lessons_en: string[] | null;
  total_verses: number;
  events: StoryAtlasEvent[];
}

export interface AtlasGraphNode {
  id: string;
  type: string;
  label: string;
  data: Record<string, unknown>;
  position: { x: number; y: number } | null;
}

export interface AtlasGraphEdge {
  source: string;
  target: string;
  type: string;
  label: string | null;
  is_chronological: boolean;
  strength: number;
  data: Record<string, unknown>;
}

export interface AtlasGraphResponse {
  cluster_id: string;
  nodes: AtlasGraphNode[];
  edges: AtlasGraphEdge[];
  entry_node_id: string | null;
  is_valid_dag: boolean;
  layout_mode: string;
}

export const storyAtlasApi = {
  listClusters: (params?: { category?: string; era?: string; person?: string; tag?: string; search?: string; limit?: number; offset?: number }) =>
    api.get<StoryClusterListResponse>('/story-atlas', { params }),

  getCluster: (clusterId: string) =>
    api.get<StoryClusterDetail>(`/story-atlas/${clusterId}`),

  getClusterGraph: (clusterId: string, language: 'ar' | 'en' = 'en', mode: string = 'timeline') =>
    api.get<AtlasGraphResponse>(`/story-atlas/${clusterId}/graph`, { params: { language, mode } }),

  getTimeline: (clusterId: string, language: 'ar' | 'en' = 'en') =>
    api.get(`/story-atlas/${clusterId}/timeline`, { params: { language } }),

  getFacets: () =>
    api.get('/story-atlas/facets'),

  getCategories: () =>
    api.get('/story-atlas/categories'),

  getEras: () =>
    api.get('/story-atlas/eras'),

  getRelatedClusters: (clusterId: string) =>
    api.get(`/story-atlas/${clusterId}/related`),
};

export const ragApi = {
  ask: (question: string, language: string = 'en', preferredSources: string[] = []) =>
    api.post<RAGResponse>('/rag/ask', {
      question,
      language,
      include_scholarly_debate: true,
      preferred_sources: preferredSources,
    }),

  getIntents: () =>
    api.get('/rag/intents'),

  getSampleQuestions: (language: string = 'en') =>
    api.get('/rag/sample-questions', { params: { language } }),

  getSources: (language?: string) =>
    api.get<TafseerSourcesResponse>('/rag/sources', { params: { language } }),

  // Admin endpoints (use X-Admin-Token header for security)
  toggleSource: (sourceId: string, isEnabled: boolean, adminToken: string) =>
    api.put(`/rag/admin/sources/${sourceId}/toggle`, { is_enabled: isEnabled }, {
      headers: { 'X-Admin-Token': adminToken }
    }),

  getAdminSources: (adminToken: string) =>
    api.get<TafseerSourcesResponse>('/rag/admin/sources', {
      headers: { 'X-Admin-Token': adminToken }
    }),
};
