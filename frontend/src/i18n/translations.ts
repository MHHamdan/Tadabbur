export type Language = 'ar' | 'en';

export interface Translations {
  [key: string]: {
    ar: string;
    en: string;
  };
}

export const translations: Translations = {
  // Navigation
  nav_home: {
    ar: 'الرئيسية',
    en: 'Home',
  },
  nav_stories: {
    ar: 'قصص القرآن',
    en: 'Quran Stories',
  },
  nav_ask: {
    ar: 'اسأل',
    en: 'Ask',
  },
  nav_explorer: {
    ar: 'المستكشف',
    en: 'Explorer',
  },

  // Common
  app_title: {
    ar: 'تدبر',
    en: 'Tadabbur-AI',
  },
  app_subtitle: {
    ar: 'منصة معرفة قرآنية مبنية على المصادر',
    en: 'RAG-Grounded Quranic Knowledge Platform',
  },
  loading: {
    ar: 'جاري التحميل...',
    en: 'Loading...',
  },
  error: {
    ar: 'حدث خطأ',
    en: 'An error occurred',
  },
  search: {
    ar: 'بحث',
    en: 'Search',
  },
  close: {
    ar: 'إغلاق',
    en: 'Close',
  },

  // Stories
  stories_title: {
    ar: 'قصص القرآن الكريم',
    en: 'Stories of the Holy Quran',
  },
  stories_subtitle: {
    ar: 'استكشف القصص القرآنية وترابطها عبر السور',
    en: 'Explore Quranic narratives and their connections across surahs',
  },
  story_segments: {
    ar: 'المقاطع',
    en: 'Segments',
  },
  story_connections: {
    ar: 'الروابط',
    en: 'Connections',
  },
  story_themes: {
    ar: 'المواضيع',
    en: 'Themes',
  },
  story_figures: {
    ar: 'الشخصيات',
    en: 'Figures',
  },
  view_graph: {
    ar: 'عرض الرسم البياني',
    en: 'View Graph',
  },
  view_list: {
    ar: 'عرض القائمة',
    en: 'View List',
  },

  // Categories
  category_prophet: {
    ar: 'قصص الأنبياء',
    en: 'Prophet Stories',
  },
  category_nation: {
    ar: 'قصص الأمم',
    en: 'Nation Stories',
  },
  category_parable: {
    ar: 'الأمثال',
    en: 'Parables',
  },
  category_historical: {
    ar: 'الأحداث التاريخية',
    en: 'Historical Events',
  },

  // Ask/RAG
  ask_title: {
    ar: 'اسأل عن القرآن',
    en: 'Ask About the Quran',
  },
  ask_subtitle: {
    ar: 'احصل على إجابات مستندة إلى المصادر العلمية',
    en: 'Get answers grounded in scholarly sources',
  },
  ask_placeholder: {
    ar: 'اكتب سؤالك هنا...',
    en: 'Type your question here...',
  },
  ask_button: {
    ar: 'اسأل',
    en: 'Ask',
  },
  citations: {
    ar: 'المصادر',
    en: 'Citations',
  },
  confidence: {
    ar: 'الثقة',
    en: 'Confidence',
  },
  scholarly_consensus: {
    ar: 'إجماع العلماء',
    en: 'Scholarly Consensus',
  },

  // Tafseer
  tafseer: {
    ar: 'التفسير',
    en: 'Tafseer',
  },
  tafseer_sources: {
    ar: 'مصادر التفسير',
    en: 'Tafseer Sources',
  },
  view_tafseer: {
    ar: 'عرض التفسير',
    en: 'View Tafseer',
  },

  // Verse
  verse: {
    ar: 'آية',
    en: 'Verse',
  },
  surah: {
    ar: 'سورة',
    en: 'Surah',
  },
  juz: {
    ar: 'جزء',
    en: 'Juz',
  },
  page: {
    ar: 'صفحة',
    en: 'Page',
  },

  // Warnings
  warning_fiqh: {
    ar: 'ملاحظة: هذه المعلومات للأغراض التعليمية فقط وليست فتوى',
    en: 'Note: This is informational only, not a religious ruling (fatwa)',
  },
  warning_no_sources: {
    ar: 'يتطلب هذا استشارة علمية إضافية',
    en: 'This requires further scholarly consultation',
  },

  // Footer
  footer_disclaimer: {
    ar: 'جميع الإجابات مستندة إلى مصادر تفسيرية موثقة',
    en: 'All answers are grounded in authenticated tafseer sources',
  },
};

export function t(key: string, language: Language): string {
  const translation = translations[key];
  if (!translation) {
    console.warn(`Missing translation for key: ${key}`);
    return key;
  }
  return translation[language];
}
