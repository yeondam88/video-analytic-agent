import { useQuery } from '@tanstack/react-query';
import { Video } from '@/types/video';

interface SearchFilters {
  source?: string[];
  status?: string[];
  created_after?: string;
  created_before?: string;
}

interface SearchOptions extends SearchFilters {
  enabled?: boolean;
}

interface SearchResponse {
  results: Video[];
  count: number;
  query: string;
}

async function searchVideos(query: string, filters?: SearchFilters): Promise<SearchResponse> {
  const response = await fetch('/api/search/basic', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      filters,
      limit: 20,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to search videos');
  }

  return response.json();
}

export function useSearch(query: string, options: SearchOptions = {}) {
  const { enabled = true, ...filters } = options;

  return useQuery<SearchResponse>({
    queryKey: ['search', query, filters],
    queryFn: () => searchVideos(query, filters),
    enabled: enabled && query.length > 0,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
} 