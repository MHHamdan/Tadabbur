import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  verse_reference: string;
  excerpt: string;
  relevance_score: number;
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
}

// API functions
export const quranApi = {
  getSuraVerses: (suraNo: number) =>
    api.get<Verse[]>(`/quran/suras/${suraNo}`),

  getVerse: (suraNo: number, ayaNo: number) =>
    api.get<Verse>(`/quran/verses/${suraNo}/${ayaNo}`),

  getPageVerses: (pageNo: number) =>
    api.get<Verse[]>(`/quran/page/${pageNo}`),

  getTafseer: (suraNo: number, ayaNo: number, sources?: string[]) =>
    api.get(`/quran/tafseer/${suraNo}/${ayaNo}`, { params: { sources } }),

  search: (query: string) =>
    api.get(`/quran/search`, { params: { q: query } }),
};

export const storiesApi = {
  listStories: (category?: string) =>
    api.get<Story[]>('/stories', { params: { category } }),

  getStory: (storyId: string) =>
    api.get<StoryDetail>(`/stories/${storyId}`),

  getStoryGraph: (storyId: string) =>
    api.get<StoryGraph>(`/stories/${storyId}/graph`),

  getCategories: () =>
    api.get('/stories/categories'),
};

export const ragApi = {
  ask: (question: string, language: string = 'en') =>
    api.post<RAGResponse>('/rag/ask', {
      question,
      language,
      include_scholarly_debate: true,
    }),

  getIntents: () =>
    api.get('/rag/intents'),

  getSampleQuestions: (language: string = 'en') =>
    api.get('/rag/sample-questions', { params: { language } }),
};
