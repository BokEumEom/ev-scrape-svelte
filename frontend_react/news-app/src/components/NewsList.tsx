// src/components/NewsList.tsx
import React from 'react';
import { NewsItem } from '../types';

interface Props {
  newsItems: NewsItem[];
}

const NewsList: React.FC<Props> = ({ newsItems }) => {
  return (
    <div className="max-w-4xl mx-auto mt-2 px-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {newsItems.map(newsItem => (
        <div
          key={newsItem.id}
          className="border border-gray-200 p-4 flex flex-col"
        >
          <a href={newsItem.link} target="_blank" rel="noopener noreferrer" className="hover:underline">
            <h2 className="text-lg font-semibold text-gray-900">
              {newsItem.title}
            </h2>
          </a>
          <p className="text-xs text-gray-500 mt-2">
            {newsItem.source} - {newsItem.published_at}
          </p>
        </div>
      ))}
    </div>
  );
};

export default NewsList;
