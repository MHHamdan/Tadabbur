import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { HomePage } from './pages/HomePage';
import { StoriesPage } from './pages/StoriesPage';
import { StoryDetailPage } from './pages/StoryDetailPage';
import { AskPage } from './pages/AskPage';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stories" element={<StoriesPage />} />
        <Route path="/stories/:storyId" element={<StoryDetailPage />} />
        <Route path="/ask" element={<AskPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
