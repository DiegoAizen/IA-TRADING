// frontend/src/components/News/NewsSection.tsx
import React, { useState, useEffect } from 'react';
import { NewsItem, newsApi } from '../../api/newsApi';
import NewsCard from './NewsCard';

const NewsSection: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('general');

  const categories = [
    { value: 'general', label: '📰 Todas' },
    { value: 'forex', label: '💱 Forex' },
    { value: 'crypto', label: '₿ Crypto' },
    { value: 'stocks', label: '📈 Stocks' },
  ];

  const loadNews = async (category: string = 'general') => {
    try {
      setLoading(true);
      setError(null);
      const newsData = await newsApi.getMarketNews(category);
      setNews(newsData);
    } catch (err) {
      console.error('Error loading news:', err);
      setError('Error cargando noticias');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNews(selectedCategory);
  }, [selectedCategory]);

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">📰 Noticias del Mercado</h3>
          <p className="text-sm text-gray-400 mt-1">
            Últimas noticias financieras en tiempo real
          </p>
        </div>
        <button
          onClick={() => loadNews(selectedCategory)}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 text-sm"
        >
          {loading ? '🔄' : '🔄 Actualizar'}
        </button>
      </div>

      {/* Filtros de categoría */}
      <div className="flex space-x-2 mb-6 overflow-x-auto pb-2">
        {categories.map((category) => (
          <button
            key={category.value}
            onClick={() => handleCategoryChange(category.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              selectedCategory === category.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* Estado de carga y error */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
          <p className="text-gray-400 mt-2">Cargando noticias...</p>
        </div>
      )}

      {error && !loading && (
        <div className="text-center py-8">
          <p className="text-red-400">{error}</p>
          <button
            onClick={() => loadNews(selectedCategory)}
            className="mt-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 text-sm"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Lista de noticias */}
      {!loading && !error && (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {news.length > 0 ? (
            news.map((item) => (
              <NewsCard key={item.id} news={item} />
            ))
          ) : (
            <div className="text-center py-8 text-gray-400">
              No hay noticias disponibles
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NewsSection;