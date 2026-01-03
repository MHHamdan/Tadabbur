import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Language } from '../i18n/translations';

interface LanguageState {
  language: Language;
  direction: 'ltr' | 'rtl';
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: 'en',
      direction: 'ltr',

      setLanguage: (lang: Language) => {
        const dir = lang === 'ar' ? 'rtl' : 'ltr';
        document.documentElement.dir = dir;
        document.documentElement.lang = lang;
        set({ language: lang, direction: dir });
      },

      toggleLanguage: () => {
        set((state) => {
          const newLang = state.language === 'en' ? 'ar' : 'en';
          const dir = newLang === 'ar' ? 'rtl' : 'ltr';
          document.documentElement.dir = dir;
          document.documentElement.lang = newLang;
          return { language: newLang, direction: dir };
        });
      },
    }),
    {
      name: 'tadabbur-language',
      onRehydrateStorage: () => (state) => {
        if (state) {
          document.documentElement.dir = state.direction;
          document.documentElement.lang = state.language;
        }
      },
    }
  )
);
