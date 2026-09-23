import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { Toaster } from 'sonner';

import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { AuthModal } from '@/components/layout/AuthModal';

import { HomePage } from '@/pages/HomePage';
import { RecipeDetailPage } from '@/pages/RecipeDetailPage';
import { SearchPage } from '@/pages/SearchPage';
import { RecommendPage } from '@/pages/RecommendPage';
import { MealPlanPage } from '@/pages/MealPlanPage';
import { SavedRecipesPage } from '@/pages/SavedRecipesPage';
import { AdminPage } from '@/pages/AdminPage';

export function App() {
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const handleOpenAuth = (mode: 'login' | 'register' = 'login') => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-slate-50/50 text-neutral-900 font-sans">
          {/* Navbar */}
          <Navbar onOpenAuth={handleOpenAuth} />

          {/* Main content */}
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/recipes/:id" element={<RecipeDetailPage />} />
              <Route path="/search-ingredients" element={<SearchPage />} />
              <Route path="/recommend" element={<RecommendPage />} />
              <Route path="/meal-planner" element={<MealPlanPage />} />
              <Route path="/saved" element={<SavedRecipesPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </main>

          {/* Footer */}
          <Footer />

          {/* Auth Modal */}
          <AuthModal
            isOpen={authModalOpen}
            onClose={() => setAuthModalOpen(false)}
            initialMode={authMode}
          />

          {/* Toast notifications */}
          <Toaster richColors position="top-right" />
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
