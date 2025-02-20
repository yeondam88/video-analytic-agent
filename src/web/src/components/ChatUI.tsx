import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { InstantSearch, SearchBox, Hits } from 'react-instantsearch';
import type { Hit as InstantSearchHit } from 'instantsearch.js';
import { instantMeiliSearch } from '@meilisearch/instant-meilisearch';
import { formatDistance } from 'date-fns/formatDistance';
import { cn } from '../lib/utils';
import type { SearchClient } from 'instantsearch.js';

interface SegmentHit {
  id: string;
  video_id: string;
  start_time: number;
  end_time: number;
  text: string;
  display_text: string;
  created_at: string;
  speaker_id: string;
  metadata: string;
}

interface ChatUIProps {
  onSearch?: (query: string) => void;
}

const { searchClient } = instantMeiliSearch(
  'https://ms-bfd491088e40-19061.sfo.meilisearch.io',
  '068ff2bdf382c2e93dd632e883beb05291d921db',
  {
    keepZeroFacets: true,
    primaryKey: 'id',
  }
);

const PlayIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const SegmentCard = ({ hit }: { hit: InstantSearchHit<SegmentHit> }) => {
  const metadata = JSON.parse(hit.metadata || '{}');
  const duration = metadata.duration || (hit.end_time - hit.start_time);
  const confidence = metadata.confidence || 1;
  const videoTitle = metadata.title || 'Video';
  
  // Calculate end timestamp for the segment
  const endTime = hit.end_time;
  
  return (
    <Link 
      to={`/videos/${hit.video_id}?start=${hit.start_time}&end=${endTime}`}
      className="block group"
    >
      <div className="p-4 bg-white rounded-lg shadow-sm group-hover:shadow-md transition-all border border-gray-100 group-hover:border-blue-200">
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5">
              <PlayIcon className="w-4 h-4 text-blue-600 group-hover:text-blue-800" />
              <span className="text-sm font-medium text-blue-600 group-hover:text-blue-800">
                {formatTime(hit.start_time)} - {formatTime(endTime)}
              </span>
            </div>
            <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full flex items-center gap-1">
              <span>Play segment</span>
              <span className="text-blue-400">•</span>
              <span>{formatDuration(duration)}</span>
            </span>
          </div>
          <span className="text-xs text-gray-500">
            {formatDistance(new Date(hit.created_at), new Date(), { addSuffix: true })}
          </span>
        </div>
        
        <div className="mb-2">
          <p className="text-xs text-gray-500 mb-1">{videoTitle}</p>
          <p className="text-gray-800 group-hover:text-gray-900">{hit.display_text || hit.text}</p>
        </div>
        
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <UserIcon className="w-3 h-3" />
            Speaker {hit.speaker_id}
          </span>
          <span className={cn(
            "px-1.5 py-0.5 rounded",
            confidence > 0.8 ? "bg-green-100 text-green-800" :
            confidence > 0.6 ? "bg-yellow-100 text-yellow-800" :
            "bg-red-100 text-red-800"
          )}>
            {Math.round(confidence * 100)}% conf.
          </span>
        </div>
      </div>
    </Link>
  );
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s`;
};

const UserIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

export function ChatUI({ onSearch }: ChatUIProps) {
  const [showSearch, setShowSearch] = useState(false);

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    // Check if the related target is within the search results
    const searchResults = document.querySelector('.ais-Hits');
    if (searchResults && searchResults.contains(e.relatedTarget as Node)) {
      return; // Don't hide if clicking within results
    }
    setShowSearch(false);
  };

  const handleResultClick = () => {
    // Close search after a small delay to ensure navigation occurs
    setTimeout(() => {
      setShowSearch(false);
    }, 100);
  };

  return (
    <div className="relative bg-gray-50 flex justify-end flex-wrap ml-auto w-full">
      <InstantSearch
        indexName="segments"
        searchClient={searchClient}
      >
        <div className="py-4 w-full">
          <SearchBox 
            placeholder="Search transcripts..."
            classNames={{
              root: "relative",
              form: "block",
              input: "w-full px-4 py-2 text-gray-900 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
              submit: "hidden",
              reset: "hidden",
              loadingIndicator: "hidden"
            }}
            onClick={() => setShowSearch(true)}
            onBlur={handleBlur}
          />
        </div>
        {showSearch && (
          <div 
            className="absolute top-full left-0 right-0 bg-white border-t border-gray-200 shadow-lg max-h-96 overflow-y-auto z-10"
            onClick={handleResultClick}
          >
            <Hits 
              hitComponent={({ hit }) => (
                <SegmentCard 
                  hit={hit as InstantSearchHit<SegmentHit>}
                />
              )}
              classNames={{
                root: "p-4",
                list: "space-y-4",
                item: "!block"
              }}
            />
          </div>
        )}
      </InstantSearch>
    </div>
  );
} 