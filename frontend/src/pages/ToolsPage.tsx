import { Video, Newspaper, Globe, BookOpen, Map, Plane, DollarSign, Lock } from 'lucide-react';
import { useLanguageStore } from '../stores/languageStore';
import clsx from 'clsx';

interface ToolModule {
  id: string;
  name_en: string;
  name_ar: string;
  description_en: string;
  description_ar: string;
  icon: React.ElementType;
  status: 'coming_soon' | 'beta' | 'available';
  color: string;
}

const TOOL_MODULES: ToolModule[] = [
  {
    id: 'videos',
    name_en: 'Videos',
    name_ar: 'الفيديوهات',
    description_en: 'Search Islamic lectures and educational videos from verified scholars',
    description_ar: 'البحث في المحاضرات الإسلامية والفيديوهات التعليمية من علماء موثقين',
    icon: Video,
    status: 'coming_soon',
    color: 'red',
  },
  {
    id: 'news',
    name_en: 'News',
    name_ar: 'الأخبار',
    description_en: 'Curated news from Islamic world and Muslim communities',
    description_ar: 'أخبار منتقاة من العالم الإسلامي والمجتمعات المسلمة',
    icon: Newspaper,
    status: 'coming_soon',
    color: 'blue',
  },
  {
    id: 'web',
    name_en: 'Web Search',
    name_ar: 'البحث في الويب',
    description_en: 'Search verified Islamic websites and scholarly resources',
    description_ar: 'البحث في المواقع الإسلامية الموثقة والموارد العلمية',
    icon: Globe,
    status: 'coming_soon',
    color: 'green',
  },
  {
    id: 'books',
    name_en: 'Books',
    name_ar: 'الكتب',
    description_en: 'Access Islamic books, manuscripts, and scholarly publications',
    description_ar: 'الوصول إلى الكتب الإسلامية والمخطوطات والمنشورات العلمية',
    icon: BookOpen,
    status: 'coming_soon',
    color: 'amber',
  },
  {
    id: 'maps',
    name_en: 'Maps',
    name_ar: 'الخرائط',
    description_en: 'Find mosques, halal restaurants, and Islamic centers nearby',
    description_ar: 'العثور على المساجد والمطاعم الحلال والمراكز الإسلامية القريبة',
    icon: Map,
    status: 'coming_soon',
    color: 'teal',
  },
  {
    id: 'flights',
    name_en: 'Flights',
    name_ar: 'الرحلات',
    description_en: 'Search flights for Hajj, Umrah, and Islamic travel',
    description_ar: 'البحث عن رحلات الحج والعمرة والسفر الإسلامي',
    icon: Plane,
    status: 'coming_soon',
    color: 'purple',
  },
  {
    id: 'finance',
    name_en: 'Finance',
    name_ar: 'المالية',
    description_en: 'Islamic finance tools, Zakat calculator, and halal investment info',
    description_ar: 'أدوات التمويل الإسلامي وحاسبة الزكاة ومعلومات الاستثمار الحلال',
    icon: DollarSign,
    status: 'coming_soon',
    color: 'emerald',
  },
];

export function ToolsPage() {
  const { language } = useLanguageStore();

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {language === 'ar' ? 'الأدوات' : 'Tools'}
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          {language === 'ar'
            ? 'أدوات مساعدة إسلامية قادمة قريباً - مصممة لتعزيز تجربتك مع التطبيق'
            : 'Upcoming Islamic helper tools - designed to enhance your experience with the app'}
        </p>
      </div>

      {/* Coming Soon Notice */}
      <div className="mb-8 p-4 bg-primary-50 border border-primary-200 rounded-lg text-center">
        <p className="text-primary-800 font-medium">
          {language === 'ar'
            ? 'هذه الأدوات قيد التطوير وستكون متاحة قريباً إن شاء الله'
            : 'These tools are under development and will be available soon, insha\'Allah'}
        </p>
      </div>

      {/* Tools Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {TOOL_MODULES.map((tool) => (
          <ToolCard key={tool.id} tool={tool} language={language} />
        ))}
      </div>
    </div>
  );
}

interface ToolCardProps {
  tool: ToolModule;
  language: 'ar' | 'en';
}

function ToolCard({ tool, language }: ToolCardProps) {
  const Icon = tool.icon;
  const name = language === 'ar' ? tool.name_ar : tool.name_en;
  const description = language === 'ar' ? tool.description_ar : tool.description_en;

  const colorClasses: Record<string, { bg: string; icon: string; border: string }> = {
    red: { bg: 'bg-red-50', icon: 'text-red-600', border: 'border-red-200' },
    blue: { bg: 'bg-blue-50', icon: 'text-blue-600', border: 'border-blue-200' },
    green: { bg: 'bg-green-50', icon: 'text-green-600', border: 'border-green-200' },
    amber: { bg: 'bg-amber-50', icon: 'text-amber-600', border: 'border-amber-200' },
    teal: { bg: 'bg-teal-50', icon: 'text-teal-600', border: 'border-teal-200' },
    purple: { bg: 'bg-purple-50', icon: 'text-purple-600', border: 'border-purple-200' },
    emerald: { bg: 'bg-emerald-50', icon: 'text-emerald-600', border: 'border-emerald-200' },
  };

  const colors = colorClasses[tool.color] || colorClasses.blue;

  return (
    <div
      className={clsx(
        'card border-2 transition-all opacity-70 cursor-not-allowed',
        colors.border
      )}
      dir={language === 'ar' ? 'rtl' : 'ltr'}
    >
      <div className="flex items-start gap-4">
        <div className={clsx('p-3 rounded-lg', colors.bg)}>
          <Icon className={clsx('w-6 h-6', colors.icon)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-semibold text-gray-700">{name}</h3>
            <span className="flex items-center gap-1 text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
              <Lock className="w-3 h-3" />
              {language === 'ar' ? 'قريباً' : 'Coming Soon'}
            </span>
          </div>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>
    </div>
  );
}
