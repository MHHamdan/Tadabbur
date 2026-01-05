import { useState, useEffect, useRef } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { ArrowLeft, Book, ChevronLeft, ChevronRight, BookOpen } from 'lucide-react';
import { useLanguageStore } from '../stores/languageStore';
import { quranApi, Verse } from '../lib/api';
import clsx from 'clsx';

type ViewMode = 'mushaf' | 'list';

interface SuraInfo {
  sura_no: number;
  name_ar: string;
  name_en: string;
  total_verses: number;
}

export function QuranPage() {
  const { suraNo } = useParams<{ suraNo: string }>();
  const [searchParams] = useSearchParams();
  const highlightAya = searchParams.get('aya');
  const { language } = useLanguageStore();
  const [verses, setVerses] = useState<Verse[]>([]);
  const [suras, setSuras] = useState<SuraInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('mushaf');
  const highlightRef = useRef<HTMLSpanElement>(null);

  const currentSura = parseInt(suraNo || '1', 10);

  useEffect(() => {
    loadMetadata();
  }, []);

  useEffect(() => {
    if (currentSura >= 1 && currentSura <= 114) {
      loadSura(currentSura);
    }
  }, [currentSura]);

  useEffect(() => {
    if (highlightRef.current && !loading) {
      setTimeout(() => {
        highlightRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
  }, [loading, highlightAya]);

  async function loadMetadata() {
    try {
      const metaRes = await fetch('/api/v1/quran/metadata');
      const meta = await metaRes.json();
      setSuras(meta.suras || []);
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  }

  async function loadSura(suraNo: number) {
    setLoading(true);
    try {
      const res = await quranApi.getSuraVerses(suraNo);
      setVerses(res.data);
    } catch (error) {
      console.error('Failed to load sura:', error);
    } finally {
      setLoading(false);
    }
  }

  const suraName = verses.length > 0
    ? (language === 'ar' ? verses[0].sura_name_ar : verses[0].sura_name_en)
    : '';

  // Render verse number in Arabic-Indic numerals
  const toArabicNum = (num: number): string => {
    const arabicNums = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    return num.toString().split('').map(d => arabicNums[parseInt(d)]).join('');
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Link */}
      <Link
        to="/stories"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        {language === 'ar' ? 'العودة للقصص' : 'Back to Stories'}
      </Link>

      {/* Sura Header */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Book className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold font-arabic">{suraName}</h1>
              <p className="text-sm text-gray-500">
                {language === 'ar' ? `السورة ${toArabicNum(currentSura)}` : `Surah ${currentSura}`}
                {' - '}
                {language === 'ar' ? `${toArabicNum(verses.length)} آية` : `${verses.length} verses`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* View Mode Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('mushaf')}
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                  viewMode === 'mushaf'
                    ? 'bg-white shadow text-primary-600'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <BookOpen className="w-4 h-4" />
                {language === 'ar' ? 'المصحف' : 'Mushaf'}
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={clsx(
                  'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                  viewMode === 'list'
                    ? 'bg-white shadow text-primary-600'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                {language === 'ar' ? 'قائمة' : 'List'}
              </button>
            </div>

            {/* Navigation */}
            <div className="flex items-center gap-2">
              <Link
                to={`/quran/${Math.max(1, currentSura - 1)}`}
                className={clsx(
                  'p-2 rounded-lg hover:bg-gray-100 transition-colors',
                  currentSura <= 1 && 'opacity-50 pointer-events-none'
                )}
              >
                {language === 'ar' ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
              </Link>
              <select
                value={currentSura}
                onChange={(e) => window.location.href = `/quran/${e.target.value}`}
                className="input py-1 px-2 w-auto text-sm"
              >
                {suras.map((s) => (
                  <option key={s.sura_no} value={s.sura_no}>
                    {s.sura_no}. {language === 'ar' ? s.name_ar : s.name_en}
                  </option>
                ))}
              </select>
              <Link
                to={`/quran/${Math.min(114, currentSura + 1)}`}
                className={clsx(
                  'p-2 rounded-lg hover:bg-gray-100 transition-colors',
                  currentSura >= 114 && 'opacity-50 pointer-events-none'
                )}
              >
                {language === 'ar' ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Quran Content */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full" />
        </div>
      ) : viewMode === 'mushaf' ? (
        /* Mushaf Style View */
        <div className="card bg-[#fefcf3] border-2 border-amber-200 shadow-lg">
          {/* Decorative Header */}
          <div className="text-center mb-6 pb-4 border-b-2 border-amber-300">
            <div className="inline-block px-8 py-2 bg-gradient-to-r from-amber-100 via-amber-50 to-amber-100 rounded-lg border border-amber-300">
              <h2 className="text-2xl font-bold font-arabic text-amber-900">
                {verses[0]?.sura_name_ar}
              </h2>
            </div>
          </div>

          {/* Bismillah (except for Surah 9) */}
          {currentSura !== 9 && currentSura !== 1 && (
            <div className="text-center mb-6">
              <span className="text-xl font-arabic text-amber-800">
                بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
              </span>
            </div>
          )}

          {/* Verses in Mushaf Style */}
          <div className="text-center leading-[3] font-arabic text-2xl text-gray-900" dir="rtl">
            {verses.map((verse, idx) => {
              const isHighlighted = highlightAya && parseInt(highlightAya, 10) === verse.aya_no;
              return (
                <span key={verse.id}>
                  <span
                    ref={isHighlighted ? highlightRef : null}
                    className={clsx(
                      'inline transition-colors',
                      isHighlighted && 'bg-primary-200 rounded px-1'
                    )}
                  >
                    {verse.text_uthmani}
                  </span>
                  <span className="inline-flex items-center justify-center w-8 h-8 mx-1 text-sm bg-amber-100 text-amber-800 rounded-full border border-amber-300 font-semibold">
                    {toArabicNum(verse.aya_no)}
                  </span>
                  {idx < verses.length - 1 && ' '}
                </span>
              );
            })}
          </div>

          {/* Decorative Footer */}
          <div className="mt-6 pt-4 border-t-2 border-amber-300 flex justify-center gap-4 text-sm text-amber-700">
            <span>{language === 'ar' ? 'الصفحة' : 'Page'}: {verses[0]?.page_no}</span>
            <span>•</span>
            <span>{language === 'ar' ? 'الجزء' : 'Juz'}: {verses[0]?.juz_no}</span>
          </div>
        </div>
      ) : (
        /* List View with Translations */
        <div className="card">
          <div className="space-y-6">
            {verses.map((verse) => {
              const isHighlighted = highlightAya && parseInt(highlightAya, 10) === verse.aya_no;
              return (
                <div
                  key={verse.id}
                  className={clsx(
                    'p-4 rounded-lg transition-colors',
                    isHighlighted ? 'bg-primary-50 ring-2 ring-primary-300' : 'hover:bg-gray-50'
                  )}
                >
                  <div className="flex items-start gap-4" dir="rtl">
                    <span
                      ref={isHighlighted ? highlightRef : null}
                      className={clsx(
                        'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm',
                        isHighlighted ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700'
                      )}
                    >
                      {toArabicNum(verse.aya_no)}
                    </span>
                    <div className="flex-1">
                      <p className="text-xl leading-loose font-arabic text-gray-900 mb-3">
                        {verse.text_uthmani}
                      </p>
                      {verse.translations && verse.translations.length > 0 && (
                        <p className="text-sm text-gray-600 leading-relaxed" dir={language === 'ar' ? 'rtl' : 'ltr'}>
                          {verse.translations.find(t => t.language === (language === 'ar' ? 'ar' : 'en'))?.text ||
                           verse.translations[0]?.text}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
