// src/components/NewsList.tsx
import React from 'react';
import { NewsItem } from '../types';

interface Props {
  newsItems: NewsItem[];
}

const NewsList: React.FC<Props> = ({ newsItems }) => {
  return (
    <div className="max-w-4xl mx-auto mt-10 px-4">
      {newsItems.map(newsItem => (
        <div key={newsItem.id} className="border-b border-gray-200 py-4 mb-4">
          <h2 className="text-lg md:text-xl font-semibold text-blue-800 mb-2">{newsItem.title}</h2>
          <p className="text-sm md:text-base text-gray-600 mb-2">출처: {newsItem.source} | {newsItem.published_at}</p>
          <a href={newsItem.link} className="text-blue-600 hover:text-blue-800 visited:text-purple-600">Read more...</a>
        </div>
      ))}
    </div>
  );
};

export default NewsList;

