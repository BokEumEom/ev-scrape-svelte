// src/services/apiService.ts
import axios from 'axios';
import { NewsItem, CommunityPost, CommunityPostCreate } from '../types';

const PAGE_SIZE = 10;

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
// export const PUBLIC_API_BASE_URL = 'https://fastapi.watercharging.com';

export const fetchNewsItems = async (page: number = 1, limit: number = 10): Promise<NewsItem[]> => {
  const skip = (page - 1) * limit; // Calculate the correct skip value
  const url = `${API_BASE_URL}/news?skip=${skip}&limit=${limit}`;
  
  try {
      const response = await fetch(url);
      
      if (!response.ok) {
          // Provide a more specific message with status code and status text
          throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
      
  } catch (error) {
      console.error("Failed to fetch news items:", error.message);
      // Depending on how you want to handle errors,
      // you might want to re-throw the error or handle it accordingly
      throw error;
  }
};

export const fetchAnnouncements = async (endpoint: string) => {
    const url = `${API_BASE_URL}/announcements/${endpoint}/`;
    try {
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch announcements for ${endpoint}:`, error);
      throw error;
    }
  };

export const searchNewsItems = async (query: string, page: number): Promise<NewsItem[]> => {
  const limit = 10;
  const skip = (page - 1) * limit;
  const url = `${API_BASE_URL}/news/search/?query=${encodeURIComponent(query)}&skip=${skip}&limit=${limit}`;
  console.log("Requesting URL:", url); // Add this line to log the URL
  try {
    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    console.error("Search API error:", error);
    throw error;
  }
};  

export const fetchCommunityPosts = async (page: number, limit: number = PAGE_SIZE): Promise<CommunityPost[]> => {
  const skip = (page - 1) * limit;
  const url = `${API_BASE_URL}/community/?skip=${skip}&limit=${limit}`;
  const response = await axios.get<CommunityPost[]>(url);
  return response.data;
};

// In your apiService.ts
export const createCommunityPost = async (post: CommunityPostCreate): Promise<void> => {
  const url = `${API_BASE_URL}/community/`;
  try {
    await axios.post(url, post);
    // You might want to handle the response here if needed
  } catch (error) {
    console.error('Failed to create community post:', error);
    throw error; // It's good practice to re-throw the error so that it can be caught and handled by the caller
  }
};


export const submitVote = async (newsId: number, voteValue: number): Promise<NewsItem> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/news/${newsId}/vote`, {
      vote_value: voteValue,
    });
    // Assuming the response data is a NewsItem object
    return response.data;
  } catch (error) {
    console.error(`Error submitting vote to ${API_BASE_URL}/news/${newsId}/vote:`, error);
    throw error;
  }
};