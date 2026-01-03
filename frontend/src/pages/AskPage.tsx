import { useState } from 'react';
import { Send, AlertTriangle, BookOpen, CheckCircle } from 'lucide-react';
import { useLanguageStore } from '../stores/languageStore';
import { t } from '../i18n/translations';
import { ragApi, RAGResponse, Citation } from '../lib/api';
import clsx from 'clsx';

export function AskPage() {
  const { language } = useLanguageStore();
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;

    setLoading(true);
    setError(null);

    try {
      const result = await ragApi.ask(question, language);
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
            disabled={loading || !question.trim()}
            className={clsx(
              'btn-primary flex items-center gap-2',
              (loading || !question.trim()) && 'opacity-50 cursor-not-allowed'
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
                  <CitationCard key={citation.chunk_id} citation={citation} />
                ))}
              </div>
            </div>
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

function CitationCard({ citation }: { citation: Citation }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="font-medium text-sm">{citation.source_name}</span>
        </div>
        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded">
          {citation.verse_reference}
        </span>
      </div>
      <p className="text-sm text-gray-600 line-clamp-2">{citation.excerpt}</p>
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
