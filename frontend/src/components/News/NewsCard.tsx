// frontend/src/components/News/NewsCard.tsx
import React from 'react';
import { NewsItem } from '../../api/newsApi';

interface NewsCardProps {
  news: NewsItem;
}

const NewsCard: React.FC<NewsCardProps> = ({ news }) => {
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400 border-green-400';
      case 'negative': return 'text-red-400 border-red-400';
      default: return 'text-gray-400 border-gray-400';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'forex': return 'bg-blue-500/20 text-blue-400';
      case 'crypto': return 'bg-purple-500/20 text-purple-400';
      case 'stocks': return 'bg-green-500/20 text-green-400';
      case 'economy': return 'bg-yellow-500/20 text-yellow-400';
      case 'commodities': return 'bg-orange-500/20 text-orange-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`text-xs px-2 py-1 rounded ${getCategoryColor(news.category)}`}>
              {news.category.toUpperCase()}
            </span>
            <span className={`text-xs border px-2 py-1 rounded ${getSentimentColor(news.sentiment)}`}>
              {news.sentiment}
            </span>
          </div>
          <h3 className="text-white font-medium text-sm leading-tight mb-2">
            {news.title}
          </h3>
          <p className="text-gray-400 text-xs leading-relaxed mb-3">
            {news.summary}
          </p>
        </div>
        {news.image_url && (
          <div className="ml-4 flex-shrink-0">
            <img 
              src={news.image_url} 
              alt={news.title}
              className="w-16 h-16 rounded object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        )}
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-3">
          <span>📰 {news.source}</span>
          <span>🕒 {news.time}</span>
        </div>
        <a 
          href={news.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-400 hover:text-blue-300 transition-colors"
        >
          Leer más →
        </a>
      </div>
    </div>
  );
};

export default NewsCard;