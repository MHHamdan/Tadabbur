import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { StoriesPage } from './pages/StoriesPage';
import { StoryDetailPage } from './pages/StoryDetailPage';
import { StoryAtlasPage } from './pages/StoryAtlasPage';
import { StoryAtlasDetailPage } from './pages/StoryAtlasDetailPage';
import { QuranPage } from './pages/QuranPage';
import { AskPage } from './pages/AskPage';
import { SourcesPage } from './pages/SourcesPage';
import { ToolsPage } from './pages/ToolsPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stories" element={<StoriesPage />} />
        <Route path="/stories/:storyId" element={<StoryDetailPage />} />
        <Route path="/story-atlas" element={<StoryAtlasPage />} />
        <Route path="/story-atlas/:clusterId" element={<StoryAtlasDetailPage />} />
        <Route path="/quran/:suraNo" element={<QuranPage />} />
        <Route path="/ask" element={<AskPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route path="/tools" element={<ToolsPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
