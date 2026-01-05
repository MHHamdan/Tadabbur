import { useState, useEffect } from 'react';
import { Send, AlertTriangle, BookOpen, CheckCircle, Settings2, ChevronDown, ChevronUp, FileText, Eye } from 'lucide-react';
import { useLanguageStore } from '../stores/languageStore';
import { t } from '../i18n/translations';
import { ragApi, RAGResponse, Citation, TafseerSource, EvidenceChunk } from '../lib/api';
import clsx from 'clsx';

export function AskPage() {
  const { language } = useLanguageStore();
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Tafseer source selection
  const [sources, setSources] = useState<TafseerSource[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [showSourceSelector, setShowSourceSelector] = useState(false);
  const [loadingSources, setLoadingSources] = useState(true);

  // Load available sources on mount
  useEffect(() => {
    async function loadSources() {
      try {
        const result = await ragApi.getSources();
        setSources(result.data.sources);
        // Default: select all sources
        setSelectedSources(result.data.sources.map(s => s.id));
      } catch (err) {
        console.error('Failed to load sources:', err);
      } finally {
        setLoadingSources(false);
      }
    }
    loadSources();
  }, []);

  function toggleSource(sourceId: string) {
    setSelectedSources(prev =>
      prev.includes(sourceId)
        ? prev.filter(id => id !== sourceId)
        : [...prev, sourceId]
    );
  }

  function selectAllSources() {
    setSelectedSources(sources.map(s => s.id));
  }

  function clearAllSources() {
    setSelectedSources([]);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const result = await ragApi.ask(question, language, selectedSources);
      setResponse(result.data);
    } catch (err) {
      console.error('RAG error:', err);
      setError(
        language === 'ar'
          ? 'حدث خطأ أثناء معالجة السؤال'
          : 'An error occurred while processing your question'
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('ask_title', language)}
        </h1>
        <p className="text-gray-600">{t('ask_subtitle', language)}</p>
      </div>

      {/* Tafseer Source Selector */}
      <div className="card mb-4">
        <button
          onClick={() => setShowSourceSelector(!showSourceSelector)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-2">
            <Settings2 className="w-5 h-5 text-primary-600" />
            <span className="font-medium">
              {language === 'ar' ? 'مصادر التفسير' : 'Tafseer Sources'}
            </span>
            <span className="text-sm text-gray-500">
              ({selectedSources.length}/{sources.length} {language === 'ar' ? 'محدد' : 'selected'})
            </span>
          </div>
          {showSourceSelector ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </button>

        {showSourceSelector && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            {/* Quick actions */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={selectAllSources}
                className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded hover:bg-primary-200 transition-colors"
              >
                {language === 'ar' ? 'اختر الكل' : 'Select All'}
              </button>
              <button
                onClick={clearAllSources}
                className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                {language === 'ar' ? 'إلغاء الكل' : 'Clear All'}
              </button>
            </div>

            {/* Source list */}
            {loadingSources ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full" />
              </div>
            ) : (
              <div className="grid gap-2 sm:grid-cols-2">
                {sources.map((source) => (
                  <label
                    key={source.id}
                    className={clsx(
                      'flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
                      selectedSources.includes(source.id)
                        ? 'border-primary-300 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    )}
                    dir={language === 'ar' ? 'rtl' : 'ltr'}
                  >
                    <input
                      type="checkbox"
                      checked={selectedSources.includes(source.id)}
                      onChange={() => toggleSource(source.id)}
                      className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm">
                        {language === 'ar' ? source.name_ar : source.name_en}
                      </div>
                      <div className="text-xs text-gray-500 truncate">
                        {language === 'ar' ? source.author_ar : source.author_en}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={clsx(
                          'text-xs px-1.5 py-0.5 rounded',
                          source.era === 'classical' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                        )}>
                          {source.era === 'classical'
                            ? (language === 'ar' ? 'تراثي' : 'Classical')
                            : (language === 'ar' ? 'معاصر' : 'Modern')
                          }
                        </span>
                        <span className="text-xs text-gray-400">
                          {source.language.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Question Form */}
      <form onSubmit={handleSubmit} className="card mb-8">
        <div className="flex gap-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={t('ask_placeholder', language)}
            className="input flex-1"
            dir={language === 'ar' ? 'rtl' : 'ltr'}
          />
          <button
            type="submit"
            disabled={loading || !question.trim() || selectedSources.length === 0}
            className={clsx(
              'btn-primary flex items-center gap-2',
              (loading || !question.trim() || selectedSources.length === 0) && 'opacity-50 cursor-not-allowed'
            )}
          >
            {loading ? (
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
            ) : (
              <Send className="w-5 h-5" />
            )}
            {t('ask_button', language)}
          </button>
        </div>
        {selectedSources.length === 0 && (
          <p className="text-sm text-red-500 mt-2">
            {language === 'ar' ? 'يرجى اختيار مصدر تفسير واحد على الأقل' : 'Please select at least one tafseer source'}
          </p>
        )}
      </form>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Response */}
      {response && (
        <div className="space-y-6">
          {/* Warnings */}
          {response.warnings.length > 0 && (
            <div className="bg-gold-50 border border-gold-200 rounded-lg p-4">
              {response.warnings.map((warning, i) => (
                <p key={i} className="text-gold-800 text-sm flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  {warning}
                </p>
              ))}
            </div>
          )}

          {/* Answer */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">
                {language === 'ar' ? 'الإجابة' : 'Answer'}
              </h2>
              <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-500">
                  {t('confidence', language)}: {Math.round(response.confidence * 100)}%
                </span>
                {response.scholarly_consensus && (
                  <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded">
                    {response.scholarly_consensus}
                  </span>
                )}
              </div>
            </div>

            <div
              className="prose max-w-none"
              dir={language === 'ar' ? 'rtl' : 'ltr'}
            >
              {response.answer.split('\n').map((para, i) => (
                <p key={i} className="mb-3 text-gray-700 leading-relaxed">
                  {para}
                </p>
              ))}
            </div>
          </div>

          {/* Citations */}
          {response.citations.length > 0 && (
            <div className="card">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                {t('citations', language)} ({response.citations.length})
              </h2>
              <div className="space-y-3">
                {response.citations.map((citation) => (
                  <CitationCard key={citation.chunk_id} citation={citation} language={language} />
                ))}
              </div>
            </div>
          )}

          {/* Evidence Panel */}
          {response.evidence && response.evidence.length > 0 && (
            <EvidencePanel evidence={response.evidence} language={language} />
          )}

          {/* Processing Info */}
          <div className="text-center text-sm text-gray-400">
            {language === 'ar' ? 'وقت المعالجة:' : 'Processing time:'}{' '}
            {response.processing_time_ms}ms
          </div>
        </div>
      )}

      {/* Sample Questions */}
      {!response && (
        <div className="card">
          <h3 className="font-semibold mb-4">
            {language === 'ar' ? 'أسئلة مقترحة' : 'Sample Questions'}
          </h3>
          <div className="grid gap-2">
            {getSampleQuestions(language).map((q, i) => (
              <button
                key={i}
                onClick={() => setQuestion(q)}
                className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm transition-colors"
                dir={language === 'ar' ? 'rtl' : 'ltr'}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function CitationCard({ citation, language }: { citation: Citation; language: 'ar' | 'en' }) {
  const sourceName = language === 'ar' && citation.source_name_ar
    ? citation.source_name_ar
    : citation.source_name;

  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="font-medium text-sm">{sourceName}</span>
        </div>
        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded">
          {citation.verse_reference}
        </span>
      </div>
      <p className="text-sm text-gray-600 line-clamp-2">{citation.excerpt}</p>
    </div>
  );
}

function EvidencePanel({ evidence, language }: { evidence: EvidenceChunk[]; language: 'ar' | 'en' }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());

  function toggleChunk(chunkId: string) {
    setExpandedChunks(prev => {
      const next = new Set(prev);
      if (next.has(chunkId)) {
        next.delete(chunkId);
      } else {
        next.add(chunkId);
      }
      return next;
    });
  }

  return (
    <div className="card">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left"
      >
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Eye className="w-5 h-5 text-blue-600" />
          {language === 'ar' ? 'الأدلة المسترجعة' : 'Retrieved Evidence'} ({evidence.length})
        </h2>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <p className="text-sm text-gray-500 mb-4">
            {language === 'ar'
              ? 'هذه هي المقاطع النصية التي تم استرجاعها من مصادر التفسير والتي استخدمت لتوليد الإجابة.'
              : 'These are the raw text chunks retrieved from tafseer sources that were used to generate the answer.'}
          </p>
          {evidence.map((chunk) => {
            const isChunkExpanded = expandedChunks.has(chunk.chunk_id);
            const sourceName = language === 'ar' ? chunk.source_name_ar : chunk.source_name;
            const content = language === 'ar' ? (chunk.content_ar || chunk.content) : (chunk.content_en || chunk.content);

            return (
              <div
                key={chunk.chunk_id}
                className="bg-blue-50 rounded-lg border border-blue-100 overflow-hidden"
                dir={language === 'ar' ? 'rtl' : 'ltr'}
              >
                <button
                  onClick={() => toggleChunk(chunk.chunk_id)}
                  className="w-full p-3 flex items-start justify-between text-left hover:bg-blue-100 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <FileText className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <span className="font-medium text-sm">{sourceName}</span>
                      <span className="text-xs bg-blue-200 text-blue-800 px-1.5 py-0.5 rounded">
                        {chunk.verse_reference}
                      </span>
                      <span className="text-xs text-blue-600">
                        {Math.round(chunk.relevance_score * 100)}% {language === 'ar' ? 'صلة' : 'match'}
                      </span>
                      {chunk.methodology && (
                        <span className="text-xs bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded">
                          {chunk.methodology}
                        </span>
                      )}
                    </div>
                    {!isChunkExpanded && (
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {content}
                      </p>
                    )}
                  </div>
                  {isChunkExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0 ml-2" />
                  )}
                </button>
                {isChunkExpanded && (
                  <div className="p-3 pt-0 border-t border-blue-100 bg-white">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {content}
                    </p>
                    <div className="mt-2 text-xs text-gray-400">
                      {language === 'ar' ? 'السورة' : 'Sura'}: {chunk.sura_no}, {language === 'ar' ? 'الآيات' : 'Ayat'}: {chunk.aya_start}-{chunk.aya_end}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function getSampleQuestions(language: 'ar' | 'en'): string[] {
  if (language === 'ar') {
    return [
      'ما معنى آية الكرسي؟',
      'أخبرني عن قصة يوسف عليه السلام',
      'ماذا يقول القرآن عن الصبر؟',
    ];
  }
  return [
    'What is the meaning of Ayat al-Kursi?',
    'Tell me about the story of Prophet Yusuf',
    'What does the Quran say about patience?',
  ];
}
