import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Book, Network, List, Users, Tag } from 'lucide-react';
import { useLanguageStore } from '../stores/languageStore';
import { t } from '../i18n/translations';
import { storiesApi, StoryDetail, StoryGraph } from '../lib/api';
import { StoryGraphView } from '../components/stories/StoryGraphView';
import clsx from 'clsx';

type ViewMode = 'list' | 'graph';

export function StoryDetailPage() {
  const { storyId } = useParams<{ storyId: string }>();
  const { language } = useLanguageStore();
  const [story, setStory] = useState<StoryDetail | null>(null);
  const [graphData, setGraphData] = useState<StoryGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  useEffect(() => {
    if (storyId) {
      loadStory();
    }
  }, [storyId]);

  async function loadStory() {
    setLoading(true);
    try {
      const [storyRes, graphRes] = await Promise.all([
        storiesApi.getStory(storyId!),
        storiesApi.getStoryGraph(storyId!),
      ]);
      setStory(storyRes.data);
      setGraphData(graphRes.data);
    } catch (error) {
      console.error('Failed to load story:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!story) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-center">
        <p className="text-gray-500">Story not found</p>
        <Link to="/stories" className="text-primary-600 hover:underline mt-4 inline-block">
          Back to Stories
        </Link>
      </div>
    );
  }

  const name = language === 'ar' ? story.name_ar : story.name_en;
  const summary = language === 'ar' ? story.summary_ar : story.summary_en;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Link */}
      <Link
        to="/stories"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        {language === 'ar' ? 'العودة للقصص' : 'Back to Stories'}
      </Link>

      {/* Header */}
      <div className="card mb-8">
        <div className="flex items-start gap-4 mb-6">
          <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Book className="w-7 h-7 text-primary-600" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold">{name}</h1>
              <span className="text-sm bg-gray-100 text-gray-600 px-2 py-1 rounded">
                {story.category}
              </span>
            </div>
            {summary && <p className="text-gray-600">{summary}</p>}
          </div>
        </div>

        {/* Meta Info */}
        <div className="flex flex-wrap gap-6 text-sm">
          {story.main_figures && story.main_figures.length > 0 && (
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-gray-600">
                {story.main_figures.join(', ')}
              </span>
            </div>
          )}
          {story.themes && story.themes.length > 0 && (
            <div className="flex items-center gap-2">
              <Tag className="w-4 h-4 text-gray-400" />
              <div className="flex gap-1">
                {story.themes.map((theme) => (
                  <span
                    key={theme}
                    className="bg-primary-50 text-primary-700 px-2 py-0.5 rounded text-xs"
                  >
                    {theme}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* View Toggle */}
      <div className="flex items-center gap-4 mb-6">
        <h2 className="text-lg font-semibold flex-1">
          {t('story_segments', language)} ({story.segments.length})
        </h2>
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('list')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              viewMode === 'list'
                ? 'bg-white shadow text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            <List className="w-4 h-4" />
            {t('view_list', language)}
          </button>
          <button
            onClick={() => setViewMode('graph')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors',
              viewMode === 'graph'
                ? 'bg-white shadow text-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            <Network className="w-4 h-4" />
            {t('view_graph', language)}
          </button>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'list' ? (
        <div className="space-y-4">
          {story.segments
            .sort((a, b) => a.narrative_order - b.narrative_order)
            .map((segment) => {
              const segSummary =
                language === 'ar' ? segment.summary_ar : segment.summary_en;

              return (
                <div key={segment.id} className="card">
                  <div className="flex items-start gap-4">
                    <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">
                      {segment.narrative_order}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-medium">
                          {segment.verse_reference}
                        </span>
                        {segment.aspect && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                            {segment.aspect}
                          </span>
                        )}
                      </div>
                      {segSummary && (
                        <p className="text-gray-600 text-sm">{segSummary}</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      ) : (
        <div className="card p-0 overflow-hidden" style={{ height: '600px' }}>
          {graphData && <StoryGraphView graph={graphData} language={language} />}
        </div>
      )}
    </div>
  );
}
