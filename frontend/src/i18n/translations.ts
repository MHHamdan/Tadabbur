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
  nav_sources: {
    ar: 'المصادر',
    en: 'Sources',
  },
  nav_tools: {
    ar: 'الأدوات',
    en: 'Tools',
  },
  nav_explorer: {
    ar: 'المستكشف',
    en: 'Explorer',
  },
  nav_atlas: {
    ar: 'الأطلس',
    en: 'Atlas',
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

  // Sample questions
  sample_questions: {
    ar: 'أسئلة مقترحة',
    en: 'Sample Questions',
  },

  // Error messages
  error_processing: {
    ar: 'حدث خطأ أثناء معالجة السؤال',
    en: 'An error occurred while processing the question',
  },
};

// Story categories translation map
export const categoryTranslations: Record<string, { ar: string; en: string }> = {
  prophet: { ar: 'قصص الأنبياء', en: 'Prophet' },
  nation: { ar: 'قصص الأمم', en: 'Nation' },
  parable: { ar: 'أمثال', en: 'Parable' },
  historical: { ar: 'تاريخية', en: 'Historical' },
  righteous: { ar: 'الصالحين', en: 'Righteous' },
};

// Theme translations - comprehensive list covering ALL semantic tags in data
export const themeTranslations: Record<string, { ar: string; en: string }> = {
  // Core themes
  patience: { ar: 'الصبر', en: 'patience' },
  obedience: { ar: 'الطاعة', en: 'obedience' },
  repentance: { ar: 'التوبة', en: 'repentance' },
  creation: { ar: 'الخلق', en: 'creation' },
  arrogance: { ar: 'الكبر', en: 'arrogance' },
  faith: { ar: 'الإيمان', en: 'faith' },
  trust: { ar: 'التوكل', en: 'trust' },
  justice: { ar: 'العدل', en: 'justice' },
  mercy: { ar: 'الرحمة', en: 'mercy' },
  gratitude: { ar: 'الشكر', en: 'gratitude' },
  forgiveness: { ar: 'المغفرة', en: 'forgiveness' },
  sacrifice: { ar: 'التضحية', en: 'sacrifice' },
  wisdom: { ar: 'الحكمة', en: 'wisdom' },
  guidance: { ar: 'الهداية', en: 'guidance' },
  monotheism: { ar: 'التوحيد', en: 'monotheism' },
  prophethood: { ar: 'النبوة', en: 'prophethood' },
  resurrection: { ar: 'البعث', en: 'resurrection' },
  punishment: { ar: 'العذاب', en: 'punishment' },
  deliverance: { ar: 'النجاة', en: 'deliverance' },
  trial: { ar: 'الابتلاء', en: 'trial' },
  family: { ar: 'الأسرة', en: 'family' },
  brotherhood: { ar: 'الأخوة', en: 'brotherhood' },
  jealousy: { ar: 'الحسد', en: 'jealousy' },
  dreams: { ar: 'الأحلام', en: 'dreams' },
  power: { ar: 'القوة', en: 'power' },
  protection: { ar: 'الحماية', en: 'protection' },
  travel: { ar: 'السفر', en: 'travel' },
  wealth: { ar: 'المال', en: 'wealth' },
  knowledge: { ar: 'العلم', en: 'knowledge' },
  miracle: { ar: 'المعجزة', en: 'miracle' },
  miracles: { ar: 'المعجزات', en: 'miracles' },
  leadership: { ar: 'القيادة', en: 'leadership' },
  dawah: { ar: 'الدعوة', en: 'dawah' },
  perseverance: { ar: 'الثبات', en: 'perseverance' },
  submission: { ar: 'الاستسلام', en: 'submission' },
  healing: { ar: 'الشفاء', en: 'healing' },
  worship: { ar: 'العبادة', en: 'worship' },
  // Additional themes from database
  acceptance: { ar: 'القبول', en: 'acceptance' },
  answered_prayer: { ar: 'استجابة الدعاء', en: 'answered_prayer' },
  ascension: { ar: 'الصعود', en: 'ascension' },
  chastity: { ar: 'العفة', en: 'chastity' },
  confronting_tyranny: { ar: 'مواجهة الطغيان', en: 'confronting_tyranny' },
  courage: { ar: 'الشجاعة', en: 'courage' },
  destruction: { ar: 'الهلاك', en: 'destruction' },
  devotion: { ar: 'الإخلاص', en: 'devotion' },
  disobedience: { ar: 'العصيان', en: 'disobedience' },
  divine_mercy: { ar: 'الرحمة الإلهية', en: 'divine_mercy' },
  divine_planning: { ar: 'التدبير الإلهي', en: 'divine_planning' },
  divine_power: { ar: 'القدرة الإلهية', en: 'divine_power' },
  divine_protection: { ar: 'الحماية الإلهية', en: 'divine_protection' },
  divine_punishment: { ar: 'العقاب الإلهي', en: 'divine_punishment' },
  divine_support: { ar: 'التأييد الإلهي', en: 'divine_support' },
  father_of_prophets: { ar: 'أبو الأنبياء', en: 'father_of_prophets' },
  first_murder: { ar: 'أول جريمة قتل', en: 'first_murder' },
  hajj: { ar: 'الحج', en: 'hajj' },
  honesty: { ar: 'الصدق', en: 'honesty' },
  humility: { ar: 'التواضع', en: 'humility' },
  kaaba: { ar: 'الكعبة', en: 'kaaba' },
  kingdom: { ar: 'الملك', en: 'kingdom' },
  liberation: { ar: 'التحرير', en: 'liberation' },
  miraculous_birth: { ar: 'الولادة المعجزة', en: 'miraculous_birth' },
  morality: { ar: 'الأخلاق', en: 'morality' },
  parenting: { ar: 'التربية', en: 'parenting' },
  purity: { ar: 'الطهارة', en: 'purity' },
  questioning: { ar: 'التساؤل', en: 'questioning' },
  reconciliation: { ar: 'المصالحة', en: 'reconciliation' },
  righteousness: { ar: 'الصلاح', en: 'righteousness' },
  salvation: { ar: 'الخلاص', en: 'salvation' },
  signs: { ar: 'الآيات', en: 'signs' },
  time: { ar: 'الزمن', en: 'time' },
  trade_ethics: { ar: 'أخلاق التجارة', en: 'trade_ethics' },
  transformation: { ar: 'التحول', en: 'transformation' },
  trickery: { ar: 'المكر', en: 'trickery' },

  // ============================================================
  // COMPREHENSIVE SEMANTIC TAGS FROM STORY DATA (dhul_qarnayn_enhanced.json etc.)
  // ============================================================

  // Revelation and inquiry tags
  revelation: { ar: 'الوحي', en: 'revelation' },
  question: { ar: 'السؤال', en: 'question' },
  historical_inquiry: { ar: 'التساؤل التاريخي', en: 'historical_inquiry' },

  // Divine empowerment tags
  divine_empowerment: { ar: 'التمكين الإلهي', en: 'divine_empowerment' },
  tamkeen: { ar: 'التمكين', en: 'tamkeen' },
  authority: { ar: 'السلطة', en: 'authority' },
  resources: { ar: 'الموارد', en: 'resources' },

  // Journey and direction tags
  west: { ar: 'الغرب', en: 'west' },
  east: { ar: 'الشرق', en: 'east' },
  sun_setting: { ar: 'غروب الشمس', en: 'sun_setting' },
  sun_rising: { ar: 'شروق الشمس', en: 'sun_rising' },
  exploration: { ar: 'الاستكشاف', en: 'exploration' },
  primitive_people: { ar: 'شعوب بدائية', en: 'primitive_people' },

  // Test and moral decision tags
  test: { ar: 'الاختبار', en: 'test' },
  moral_decision: { ar: 'قرار أخلاقي', en: 'moral_decision' },
  restraint: { ar: 'ضبط النفس', en: 'restraint' },
  self_control: { ar: 'التحكم بالنفس', en: 'self_control' },

  // Service and generosity tags
  tawakkul: { ar: 'التوكل', en: 'tawakkul' },
  generosity: { ar: 'الكرم', en: 'generosity' },
  selfless_service: { ar: 'الخدمة بإخلاص', en: 'selfless_service' },
  refusing_payment: { ar: 'رفض الأجر', en: 'refusing_payment' },
  tribute: { ar: 'الخراج', en: 'tribute' },
  offer: { ar: 'العرض', en: 'offer' },
  service: { ar: 'الخدمة', en: 'service' },

  // Engineering and construction tags
  engineering: { ar: 'الهندسة', en: 'engineering' },
  construction: { ar: 'البناء', en: 'construction' },
  iron: { ar: 'الحديد', en: 'iron' },
  copper: { ar: 'النحاس', en: 'copper' },
  teamwork: { ar: 'العمل الجماعي', en: 'teamwork' },
  technology: { ar: 'التقنية', en: 'technology' },

  // Encounter and conflict tags
  encounter: { ar: 'اللقاء', en: 'encounter' },
  oppressed: { ar: 'المستضعفين', en: 'oppressed' },
  yajuj_majuj: { ar: 'يأجوج ومأجوج', en: 'yajuj_majuj' },
  corruption: { ar: 'الفساد', en: 'corruption' },
  plea_for_help: { ar: 'طلب النجدة', en: 'plea_for_help' },

  // Eschatology and divine tags
  eschatology: { ar: 'علم الآخرة', en: 'eschatology' },
  impermanence: { ar: 'الزوال', en: 'impermanence' },
  attribution_to_allah: { ar: 'نسب الفضل لله', en: 'attribution_to_allah' },
  divine_promise: { ar: 'الوعد الإلهي', en: 'divine_promise' },

  // Battle and conflict tags (Uhud, Badr, etc.)
  battle: { ar: 'المعركة', en: 'battle' },
  warfare: { ar: 'الحرب', en: 'warfare' },
  military: { ar: 'عسكري', en: 'military' },
  victory: { ar: 'النصر', en: 'victory' },
  defeat: { ar: 'الهزيمة', en: 'defeat' },
  martyrdom: { ar: 'الشهادة', en: 'martyrdom' },
  jihad: { ar: 'الجهاد', en: 'jihad' },
  defense: { ar: 'الدفاع', en: 'defense' },
  retreat: { ar: 'الانسحاب', en: 'retreat' },
  archers: { ar: 'الرماة', en: 'archers' },
  disobedience_battle: { ar: 'العصيان في المعركة', en: 'disobedience_battle' },

  // Hypocrisy and character tags
  hypocrisy: { ar: 'النفاق', en: 'hypocrisy' },
  munafiqun: { ar: 'المنافقون', en: 'munafiqun' },
  betrayal: { ar: 'الخيانة', en: 'betrayal' },
  cowardice: { ar: 'الجبن', en: 'cowardice' },
  treachery: { ar: 'الغدر', en: 'treachery' },
  doubt: { ar: 'الشك', en: 'doubt' },
  sincere_believers: { ar: 'المؤمنين الصادقين', en: 'sincere_believers' },

  // Lessons and reflection tags
  lessons: { ar: 'الدروس', en: 'lessons' },
  reflection: { ar: 'التأمل', en: 'reflection' },
  contemplation: { ar: 'التدبر', en: 'contemplation' },
  reminder: { ar: 'التذكير', en: 'reminder' },
  warning: { ar: 'التحذير', en: 'warning' },

  // Additional Islamic concepts
  taqwa: { ar: 'التقوى', en: 'taqwa' },
  iman: { ar: 'الإيمان', en: 'iman' },
  ihsan: { ar: 'الإحسان', en: 'ihsan' },
  shukr: { ar: 'الشكر', en: 'shukr' },
  sabr: { ar: 'الصبر', en: 'sabr' },
  tawbah: { ar: 'التوبة', en: 'tawbah' },
  istighfar: { ar: 'الاستغفار', en: 'istighfar' },
  dua: { ar: 'الدعاء', en: 'dua' },
  dhikr: { ar: 'الذكر', en: 'dhikr' },
  tawhid: { ar: 'التوحيد', en: 'tawhid' },
  shirk: { ar: 'الشرك', en: 'shirk' },
  kufr: { ar: 'الكفر', en: 'kufr' },
  nifaq: { ar: 'النفاق', en: 'nifaq' },

  // Place-related tags
  makkah: { ar: 'مكة', en: 'makkah' },
  madinah: { ar: 'المدينة', en: 'madinah' },
  uhud: { ar: 'أحد', en: 'uhud' },
  badr: { ar: 'بدر', en: 'badr' },
  jerusalem: { ar: 'القدس', en: 'jerusalem' },
  egypt: { ar: 'مصر', en: 'egypt' },
  sinai: { ar: 'سيناء', en: 'sinai' },

  // Prophetic mission tags
  risalah: { ar: 'الرسالة', en: 'risalah' },
  tabligh: { ar: 'التبليغ', en: 'tabligh' },
  hidayah: { ar: 'الهداية', en: 'hidayah' },
  inzar: { ar: 'الإنذار', en: 'inzar' },
  bashirah: { ar: 'البشارة', en: 'bashirah' },

  // Community and society tags
  ummah: { ar: 'الأمة', en: 'ummah' },
  jamaat: { ar: 'الجماعة', en: 'jamaat' },
  shura: { ar: 'الشورى', en: 'shura' },
  unity: { ar: 'الوحدة', en: 'unity' },
  division: { ar: 'الفرقة', en: 'division' },
  community: { ar: 'المجتمع', en: 'community' },

  // Additional moral qualities
  truthfulness: { ar: 'الصدق', en: 'truthfulness' },
  trustworthiness: { ar: 'الأمانة', en: 'trustworthiness' },
  sincerity: { ar: 'الإخلاص', en: 'sincerity' },
  modesty: { ar: 'الحياء', en: 'modesty' },
  kindness: { ar: 'اللطف', en: 'kindness' },
  compassion: { ar: 'الشفقة', en: 'compassion' },
  respect: { ar: 'الاحترام', en: 'respect' },
  honor: { ar: 'الشرف', en: 'honor' },

  // Timeline/narrative tags
  introduction: { ar: 'المقدمة', en: 'introduction' },
  development: { ar: 'التطور', en: 'development' },
  climax: { ar: 'الذروة', en: 'climax' },
  resolution: { ar: 'الحل', en: 'resolution' },
  conclusion: { ar: 'الخاتمة', en: 'conclusion' },
};

// Main figures translations
export const figureTranslations: Record<string, { ar: string; en: string }> = {
  // Prophets
  Adam: { ar: 'آدم', en: 'Adam' },
  Nuh: { ar: 'نوح', en: 'Nuh' },
  Ibrahim: { ar: 'إبراهيم', en: 'Ibrahim' },
  Ismail: { ar: 'إسماعيل', en: 'Ismail' },
  Ishaq: { ar: 'إسحاق', en: 'Ishaq' },
  Yaqub: { ar: 'يعقوب', en: 'Yaqub' },
  Yusuf: { ar: 'يوسف', en: 'Yusuf' },
  Musa: { ar: 'موسى', en: 'Musa' },
  Harun: { ar: 'هارون', en: 'Harun' },
  Dawud: { ar: 'داود', en: 'Dawud' },
  Sulayman: { ar: 'سليمان', en: 'Sulayman' },
  Isa: { ar: 'عيسى', en: 'Isa' },
  Zakariyya: { ar: 'زكريا', en: 'Zakariyya' },
  Yahya: { ar: 'يحيى', en: 'Yahya' },
  Lut: { ar: 'لوط', en: 'Lut' },
  Hud: { ar: 'هود', en: 'Hud' },
  Salih: { ar: 'صالح', en: 'Salih' },
  "Shu'ayb": { ar: 'شعيب', en: "Shu'ayb" },
  Ayyub: { ar: 'أيوب', en: 'Ayyub' },
  Yunus: { ar: 'يونس', en: 'Yunus' },
  // Righteous people
  Luqman: { ar: 'لقمان', en: 'Luqman' },
  'Dhul-Qarnayn': { ar: 'ذو القرنين', en: 'Dhul-Qarnayn' },
  Uzair: { ar: 'عزير', en: 'Uzair' },
  Maryam: { ar: 'مريم', en: 'Maryam' },
  // Family members
  Hawwa: { ar: 'حواء', en: 'Hawwa' },
  Sara: { ar: 'سارة', en: 'Sara' },
  Hajar: { ar: 'هاجر', en: 'Hajar' },
  Asiya: { ar: 'آسية', en: 'Asiya' },
  Zulaykha: { ar: 'زليخا', en: 'Zulaykha' },
  'Wife of Zakariyya': { ar: 'زوجة زكريا', en: 'Wife of Zakariyya' },
  // Villains/opponents
  Iblis: { ar: 'إبليس', en: 'Iblis' },
  Firawn: { ar: 'فرعون', en: 'Firawn' },
  Qarun: { ar: 'قارون', en: 'Qarun' },
  Namrud: { ar: 'نمرود', en: 'Namrud' },
  Abraha: { ar: 'أبرهة', en: 'Abraha' },
  'Jalut (Goliath)': { ar: 'جالوت', en: 'Jalut (Goliath)' },
  // Sons/relatives
  'Habil (Abel)': { ar: 'هابيل', en: 'Habil (Abel)' },
  'Qabil (Cain)': { ar: 'قابيل', en: 'Qabil (Cain)' },
  Brothers: { ar: 'الإخوة', en: 'Brothers' },
  'His son': { ar: 'ابنه', en: 'His son' },
  'His wife': { ar: 'زوجته', en: 'His wife' },
  'His daughters': { ar: 'بناته', en: 'His daughters' },
  'His people': { ar: 'قومه', en: 'His people' },
  'His army': { ar: 'جيشه', en: 'His army' },
  'His donkey': { ar: 'حماره', en: 'His donkey' },
  // Groups and nations
  'Bani Israel': { ar: 'بني إسرائيل', en: 'Bani Israel' },
  Disciples: { ar: 'الحواريون', en: 'Disciples' },
  Thamud: { ar: 'ثمود', en: 'Thamud' },
  "People of 'Ad": { ar: 'قوم عاد', en: "People of 'Ad" },
  'People of Madyan': { ar: 'أهل مدين', en: 'People of Madyan' },
  'Villagers by the sea': { ar: 'أصحاب القرية', en: 'Villagers by the sea' },
  'Youth of the Cave': { ar: 'أصحاب الكهف', en: 'Youth of the Cave' },
  // Creatures
  Jinn: { ar: 'الجن', en: 'Jinn' },
  Hoopoe: { ar: 'الهدهد', en: 'Hoopoe' },
  Elephant: { ar: 'الفيل', en: 'Elephant' },
  'The She-camel': { ar: 'الناقة', en: 'The She-camel' },
  'Their dog': { ar: 'كلبهم', en: 'Their dog' },
  // Others
  'Talut (Saul)': { ar: 'طالوت', en: 'Talut (Saul)' },
  'Queen of Sheba': { ar: 'ملكة سبأ', en: 'Queen of Sheba' },
  'The murdered man': { ar: 'القتيل', en: 'The murdered man' },
  Aziz: { ar: 'العزيز', en: 'Aziz' },
  'Yajuj and Majuj': { ar: 'يأجوج ومأجوج', en: 'Yajuj and Majuj' },
};

// Segment aspect/type translations
export const aspectTranslations: Record<string, { ar: string; en: string }> = {
  // Adam story aspects
  creation: { ar: 'الخلق', en: 'creation' },
  knowledge: { ar: 'العلم', en: 'knowledge' },
  iblis_refusal: { ar: 'رفض إبليس', en: 'iblis_refusal' },
  iblis_dialogue: { ar: 'حوار إبليس', en: 'iblis_dialogue' },
  iblis_arrogance: { ar: 'كبر إبليس', en: 'iblis_arrogance' },
  test_in_paradise: { ar: 'الاختبار في الجنة', en: 'test_in_paradise' },
  fall: { ar: 'الهبوط', en: 'fall' },
  repentance: { ar: 'التوبة', en: 'repentance' },
  // General aspects
  calling: { ar: 'الدعوة', en: 'calling' },
  rejection: { ar: 'الرفض', en: 'rejection' },
  deliverance: { ar: 'النجاة', en: 'deliverance' },
  punishment: { ar: 'العذاب', en: 'punishment' },
  trial: { ar: 'الابتلاء', en: 'trial' },
  miracle: { ar: 'المعجزة', en: 'miracle' },
  miracles: { ar: 'المعجزات', en: 'miracles' },
  dialogue: { ar: 'الحوار', en: 'dialogue' },
  confrontation: { ar: 'المواجهة', en: 'confrontation' },
  victory: { ar: 'النصر', en: 'victory' },
  journey: { ar: 'الرحلة', en: 'journey' },
  meeting: { ar: 'اللقاء', en: 'meeting' },
  revelation: { ar: 'الوحي', en: 'revelation' },
  command: { ar: 'الأمر', en: 'command' },
  sacrifice: { ar: 'التضحية', en: 'sacrifice' },
  blessing: { ar: 'البركة', en: 'blessing' },
  wisdom: { ar: 'الحكمة', en: 'wisdom' },
  advice: { ar: 'النصيحة', en: 'advice' },
  kingdom: { ar: 'الملك', en: 'kingdom' },
  destruction: { ar: 'الهلاك', en: 'destruction' },
  birth: { ar: 'الولادة', en: 'birth' },
  annunciation: { ar: 'البشارة', en: 'annunciation' },
  prayer: { ar: 'الدعاء', en: 'prayer' },
  healing: { ar: 'الشفاء', en: 'healing' },
  dream: { ar: 'الرؤيا', en: 'dream' },
  betrayal: { ar: 'الخيانة', en: 'betrayal' },
  temptation: { ar: 'الفتنة', en: 'temptation' },
  prison: { ar: 'السجن', en: 'prison' },
  interpretation: { ar: 'التفسير', en: 'interpretation' },
  reunion: { ar: 'اللقاء', en: 'reunion' },
  forgiveness: { ar: 'المغفرة', en: 'forgiveness' },
  building: { ar: 'البناء', en: 'building' },
  protection: { ar: 'الحماية', en: 'protection' },
  // Luqman story aspects
  given_wisdom: { ar: 'الحكمة المعطاة', en: 'given_wisdom' },
  avoid_shirk: { ar: 'اجتناب الشرك', en: 'avoid_shirk' },
  parents: { ar: 'الوالدين', en: 'parents' },
  accountability: { ar: 'المحاسبة', en: 'accountability' },
  prayer_character: { ar: 'الصلاة والأخلاق', en: 'prayer_character' },
  // Additional aspects
  warning: { ar: 'التحذير', en: 'warning' },
  promise: { ar: 'الوعد', en: 'promise' },
  guidance: { ar: 'الهداية', en: 'guidance' },
  patience: { ar: 'الصبر', en: 'patience' },
  gratitude: { ar: 'الشكر', en: 'gratitude' },
  trust: { ar: 'التوكل', en: 'trust' },
  salvation: { ar: 'الإنقاذ', en: 'salvation' },
  death: { ar: 'الموت', en: 'death' },
  resurrection: { ar: 'البعث', en: 'resurrection' },
  worship: { ar: 'العبادة', en: 'worship' },
  obedience: { ar: 'الطاعة', en: 'obedience' },
  disobedience: { ar: 'العصيان', en: 'disobedience' },
  ark: { ar: 'السفينة', en: 'ark' },
  flood: { ar: 'الطوفان', en: 'flood' },
  fire: { ar: 'النار', en: 'fire' },
  migration: { ar: 'الهجرة', en: 'migration' },
  test: { ar: 'الاختبار', en: 'test' },
  covenant: { ar: 'العهد', en: 'covenant' },
  // Extended aspects from all stories
  '100_years': { ar: 'مئة عام', en: '100_years' },
  advice_given: { ar: 'النصيحة المقدمة', en: 'advice_given' },
  angel_visit: { ar: 'زيارة الملاك', en: 'angel_visit' },
  angels_visit: { ar: 'زيارة الملائكة', en: 'angels_visit' },
  answer: { ar: 'الإجابة', en: 'answer' },
  ant_valley: { ar: 'وادي النمل', en: 'ant_valley' },
  arrogant_response: { ar: 'الرد المتكبر', en: 'arrogant_response' },
  awakening: { ar: 'الاستيقاظ', en: 'awakening' },
  becomes_minister: { ar: 'يصبح وزيرًا', en: 'becomes_minister' },
  believers_saved: { ar: 'نجاة المؤمنين', en: 'believers_saved' },
  birth_and_rescue: { ar: 'الولادة والإنقاذ', en: 'birth_and_rescue' },
  birth_narrative: { ar: 'قصة الولادة', en: 'birth_narrative' },
  breaking_idols: { ar: 'تحطيم الأصنام', en: 'breaking_idols' },
  brothers_return: { ar: 'عودة الإخوة', en: 'brothers_return' },
  building_ark: { ar: 'بناء السفينة', en: 'building_ark' },
  building_barrier: { ar: 'بناء السد', en: 'building_barrier' },
  building_kaaba: { ar: 'بناء الكعبة', en: 'building_kaaba' },
  burial: { ar: 'الدفن', en: 'burial' },
  calling_father: { ar: 'دعوة الأب', en: 'calling_father' },
  calling_to_hajj: { ar: 'الدعوة للحج', en: 'calling_to_hajj' },
  calling_to_lord: { ar: 'الدعاء إلى الله', en: 'calling_to_lord' },
  camel_killed: { ar: 'قتل الناقة', en: 'camel_killed' },
  childhood_dream: { ar: 'رؤيا الطفولة', en: 'childhood_dream' },
  chosen_purified: { ar: 'الاصطفاء والتطهير', en: 'chosen_purified' },
  complete_story: { ar: 'القصة الكاملة', en: 'complete_story' },
  confronting_firawn: { ar: 'مواجهة فرعون', en: 'confronting_firawn' },
  crossing_sea: { ar: 'عبور البحر', en: 'crossing_sea' },
  dawah: { ar: 'الدعوة', en: 'dawah' },
  departure: { ar: 'المغادرة', en: 'departure' },
  divine_gifts: { ar: 'الهبات الإلهية', en: 'divine_gifts' },
  faith: { ar: 'الإيمان', en: 'faith' },
  given_kingdom: { ar: 'إعطاء الملك', en: 'given_kingdom' },
  given_wealth: { ar: 'إعطاء المال', en: 'given_wealth' },
  giving_birth: { ar: 'الولادة', en: 'giving_birth' },
  golden_calf: { ar: 'العجل الذهبي', en: 'golden_calf' },
  habil_response: { ar: 'رد هابيل', en: 'habil_response' },
  hoopoe_news: { ar: 'خبر الهدهد', en: 'hoopoe_news' },
  humility: { ar: 'التواضع', en: 'humility' },
  introduction: { ar: 'المقدمة', en: 'introduction' },
  iron_gift: { ar: 'تليين الحديد', en: 'iron_gift' },
  journey_east: { ar: 'الرحلة شرقًا', en: 'journey_east' },
  journey_west: { ar: 'الرحلة غربًا', en: 'journey_west' },
  journey_with_khidr: { ar: 'الرحلة مع الخضر', en: 'journey_with_khidr' },
  landing: { ar: 'الرسو', en: 'landing' },
  lessons: { ar: 'الدروس', en: 'lessons' },
  magicians_convert: { ar: 'إسلام السحرة', en: 'magicians_convert' },
  miraculous_birth: { ar: 'الولادة المعجزة', en: 'miraculous_birth' },
  mother_vow: { ar: 'نذر الأم', en: 'mother_vow' },
  mount_sinai: { ar: 'جبل الطور', en: 'mount_sinai' },
  mountains_praise: { ar: 'تسبيح الجبال', en: 'mountains_praise' },
  murder: { ar: 'القتل', en: 'murder' },
  not_crucified: { ar: 'لم يُصلب', en: 'not_crucified' },
  offerings: { ar: 'القرابين', en: 'offerings' },
  passing_by: { ar: 'المرور', en: 'passing_by' },
  people_believe: { ar: 'إيمان القوم', en: 'people_believe' },
  praised: { ar: 'الثناء', en: 'praised' },
  queen_of_sheba: { ar: 'ملكة سبأ', en: 'queen_of_sheba' },
  questions: { ar: 'الأسئلة', en: 'questions' },
  receiving_prophethood: { ar: 'تلقي النبوة', en: 'receiving_prophethood' },
  rejected: { ar: 'الرفض', en: 'rejected' },
  reluctant_obedience: { ar: 'الطاعة المترددة', en: 'reluctant_obedience' },
  rescued: { ar: 'الإنقاذ', en: 'rescued' },
  returning_to_people: { ar: 'العودة للقوم', en: 'returning_to_people' },
  sacrifice_test: { ar: 'اختبار الذبح', en: 'sacrifice_test' },
  secret_prayer: { ar: 'الدعاء السري', en: 'secret_prayer' },
  seeking_truth: { ar: 'البحث عن الحق', en: 'seeking_truth' },
  she_camel: { ar: 'الناقة', en: 'she_camel' },
  showing_off: { ar: 'التفاخر', en: 'showing_off' },
  signs: { ar: 'الآيات', en: 'signs' },
  sleep: { ar: 'النوم', en: 'sleep' },
  sold_to_egypt: { ar: 'البيع إلى مصر', en: 'sold_to_egypt' },
  son_drowns: { ar: 'غرق الابن', en: 'son_drowns' },
  speaking_in_cradle: { ar: 'الكلام في المهد', en: 'speaking_in_cradle' },
  swallowed: { ar: 'الابتلاع', en: 'swallowed' },
  table_from_heaven: { ar: 'المائدة من السماء', en: 'table_from_heaven' },
  teaching_tawhid: { ar: 'تعليم التوحيد', en: 'teaching_tawhid' },
  the_test: { ar: 'الاختبار', en: 'the_test' },
  threat: { ar: 'التهديد', en: 'threat' },
  three_groups: { ar: 'الفرق الثلاث', en: 'three_groups' },
  throne_test: { ar: 'اختبار العرش', en: 'throne_test' },
  transformation: { ar: 'التحول', en: 'transformation' },
  transgression: { ar: 'العدوان', en: 'transgression' },
  upbringing: { ar: 'التنشئة', en: 'upbringing' },
  warning_people: { ar: 'تحذير القوم', en: 'warning_people' },
  wife_left_behind: { ar: 'ترك الزوجة', en: 'wife_left_behind' },
  with_talut: { ar: 'مع طالوت', en: 'with_talut' },
  yahya_qualities: { ar: 'صفات يحيى', en: 'yahya_qualities' },
  youth_and_exile: { ar: 'الشباب والنفي', en: 'youth_and_exile' },
  test_of_chastity: { ar: 'اختبار العفة', en: 'test_of_chastity' },
  // Uhud/Munafiqun story tags
  strategy: { ar: 'الإستراتيجية', en: 'strategy' },
  exposure: { ar: 'الانكشاف', en: 'exposure' },
  superiority: { ar: 'التفوق', en: 'superiority' },
  mortality: { ar: 'الفناء', en: 'mortality' },
  consultation: { ar: 'المشاورة', en: 'consultation' },
  joy: { ar: 'الفرح', en: 'joy' },
  messenger: { ar: 'الرسول', en: 'messenger' },
  divine_help: { ar: 'العون الإلهي', en: 'divine_help' },
  greed: { ar: 'الطمع', en: 'greed' },
  encouragement: { ar: 'التشجيع', en: 'encouragement' },
  afterlife: { ar: 'الآخرة', en: 'afterlife' },
  honor: { ar: 'الشرف', en: 'honor' },
};

export function t(key: string, language: Language): string {
  const translation = translations[key];
  if (!translation) {
    console.warn(`Missing translation for key: ${key}`);
    return key;
  }
  return translation[language];
}

// Helper function to translate category
export function translateCategory(category: string, language: Language): string {
  const trans = categoryTranslations[category];
  return trans ? trans[language] : category;
}

// Helper function to translate theme
export function translateTheme(theme: string, language: Language): string {
  const trans = themeTranslations[theme.toLowerCase()];
  return trans ? trans[language] : theme;
}

// Helper function to translate figure name
export function translateFigure(figure: string, language: Language): string {
  const trans = figureTranslations[figure];
  return trans ? trans[language] : figure;
}

// Helper function to translate aspect
export function translateAspect(aspect: string, language: Language): string {
  const trans = aspectTranslations[aspect.toLowerCase()];
  return trans ? trans[language] : aspect;
}

/**
 * Universal tag translation function.
 * Tries theme translation first, then aspect translation, then returns original with warning.
 * Returns: { text: string, isMissing: boolean }
 */
export function translateTag(tag: string, language: Language): { text: string; isMissing: boolean } {
  const normalized = tag.toLowerCase().replace(/\s+/g, '_');

  // Try theme translation first
  const themeResult = themeTranslations[normalized];
  if (themeResult) {
    return { text: themeResult[language], isMissing: false };
  }

  // Try aspect translation
  const aspectResult = aspectTranslations[normalized];
  if (aspectResult) {
    return { text: aspectResult[language], isMissing: false };
  }

  // If Arabic mode and tag has no Arabic translation, it's missing
  if (language === 'ar') {
    // Check if the tag itself is already Arabic (contains Arabic characters)
    const hasArabic = /[\u0600-\u06FF]/.test(tag);
    if (hasArabic) {
      return { text: tag, isMissing: false };
    }
    // Log warning for missing Arabic translation
    console.warn(`[i18n] Missing Arabic translation for tag: "${tag}"`);
    return { text: tag, isMissing: true };
  }

  // English mode - just return as-is (formatted)
  return { text: tag.replace(/_/g, ' '), isMissing: false };
}

/**
 * Simple tag translation that returns just the text (for simpler use cases).
 * Falls back to original tag if no translation found.
 */
export function translateTagSimple(tag: string, language: Language): string {
  const { text } = translateTag(tag, language);
  return text;
}
