// frontend/src/api/newsApi.ts
import api from './newsAxiosConfig';

export interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  url: string;
  image_url: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  category: string;
}

export const newsApi = {
  // Obtener noticias del mercado
  getMarketNews: async (category?: string): Promise<NewsItem[]> => {
    const response = await api.get(`/news/market-news${category ? `?category=${category}` : ''}`);
    return response.data;
  },

  // Obtener noticias de criptomonedas
  getCryptoNews: async (): Promise<NewsItem[]> => {
    const response = await api.get('/news/crypto-news');
    return response.data;
  },

  // Obtener noticias de Forex
  getForexNews: async (): Promise<NewsItem[]> => {
    const response = await api.get('/news/forex-news');
    return response.data;
  },
};