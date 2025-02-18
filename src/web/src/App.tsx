import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Navigation } from './components/Navigation'
import { HomePage } from './pages/HomePage'
import { SearchPage } from './pages/SearchPage'
import { VideoDetailPage } from './pages/VideoDetailPage'
import { ChatPage } from './pages/ChatPage'
import VideoProcessingPage from './pages/VideoProcessingPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
      staleTime: 5000
    }
  }
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background font-sans antialiased">
          <Navigation />
          <main className="container mx-auto py-6">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/videos/:videoId" element={<VideoDetailPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/process" element={<VideoProcessingPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
} 