import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChatUI } from '@/components/ChatUI';
import { VideoGrid } from '@/components/VideoGrid';
import { useSearch } from '@/hooks/useSearch';
import { useDebounce } from '@/hooks/useDebounce';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function ChatPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, 300);
  const navigate = useNavigate();

  const { data: searchResults, isLoading } = useSearch(debouncedQuery);

  return (
    <div className="container mx-auto py-6 space-y-6">
      <h1 className="text-3xl font-bold">Video Assistant</h1>
      
      <Tabs defaultValue="chat" className="w-full">
        <TabsList>
          <TabsTrigger value="chat">Chat & Segment Search</TabsTrigger>
          <TabsTrigger value="search">Video Search</TabsTrigger>
        </TabsList>
        
        <TabsContent value="chat" className="mt-6">
          <ChatUI 
            onSearch={setSearchQuery}
          />
        </TabsContent>
        
        <TabsContent value="search" className="mt-6">
          {searchResults && (
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground">
                Found {searchResults.count} videos
              </div>
              <VideoGrid 
                videos={searchResults.results || []} 
                isLoading={isLoading} 
              />
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
} 