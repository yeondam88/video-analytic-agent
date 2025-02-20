## SpecStory

## Video Detail Page Navigation Implementation (2/19/2025, 6:49:54 AM)

_**User**_

when the user is clicking a search result, then we should navigate to video detail page and use the query param to call an api to fetch video data. and also passing start and end timestamp to go to that section in that video

we already have all necessary components

---

_**Assistant**_

I'll help you implement the search result click navigation with timestamp parameters. Let me analyze the current codebase and plan the implementation.

---

_****_



---

_****_



Let me search more specifically for the search page component.

---

_****_



---

_****_



Let me check the current implementation of SearchPage.tsx.

---

_****_

Read file: src/web/src/pages/SearchPage.tsx

---

_****_



Now let me check the VideoGrid component since it's used in the search results.

---

_****_

Read file: src/web/src/components/VideoGrid.tsx

---

_****_



Let me check if we have a segment search implementation.

---

_****_



---

_****_



Let me try another search.

---

_****_

<details>
            <summary>Searched codebase "search segments API endpoint" • **25** results</summary>
        
| File | Lines |
|------|-------|
| `src/api/routers/search.py` | L117-136 |
| `src/api/routers/search.py` | L215-236 |
| `src/api/routers/search.py` | L180-215 |
| `src/api/routers/videos.py` | L357-410 |
| `src/api/routers/search.py` | L167-180 |
| `src/api/routers/videos.py` | L410-417 |
| `src/api/routers/search.py` | L49-87 |
| `src/api/routers/videos.py` | L417-471 |
| `src/api/routers/search.py` | L1-22 |
| `src/api/routers/videos.py` | L199-224 |
| `src/api/routers/search.py` | L87-117 |
| `src/api/routers/search.py` | L136-167 |
| `src/api/routers/videos.py` | L224-265 |
| `src/api/routers/search.py` | L236-261 |
| `src/api/routers/videos.py` | L324-357 |
| `src/api/routers/search.py` | L28-33 |
| `src/api/routers/search.py` | L22-28 |
| `src/api/routers/search.py` | L37-43 |
| `src/api/routers/videos.py` | L82-126 |
| `src/api/routers/__init__.py` | L1-16 |
| `src/api/routers/search.py` | L33-37 |
| `src/api/routers/videos.py` | L1-24 |
| `src/api/routers/search.py` | L43-49 |
| `src/api/routers/summaries.py` | L1-13 |
| `src/api/routers/video.py` | L117-141 |

</details>

---

_****_





Let me check the search service implementation.

---

_****_

Read file: src/api/services/search_service.py

---

_****_





Now I'll help implement the search result click navigation with timestamp parameters. Here's what we need to do:

1. Update the search page to handle segment search results
2. Add click handler to navigate to video detail with timestamps
3. Ensure the video detail page can handle timestamp parameters

Let me first check if we have a segment search component.

---

_****_



---

_****_



Let me create the necessary components and updates. I'll start with updating the SearchPage.tsx to handle segment search results.

---

_****_

```diff
  import React, { useState } from 'react'
  import { useQuery } from '@tanstack/react-query'
+ import { useNavigate } from 'react-router-dom'
  import { Input } from '@/components/ui/input'
  import { VideoGrid } from '@/components/VideoGrid'
  import { useDebounce } from '@/lib/hooks'
  import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
+ import { Card, CardContent } from '@/components/ui/card'
+ 
+ interface SegmentResult {
+   id: string
+   video_id: string
+   text: string
+   start_time: number
+   end_time: number
+   similarity: number
+ }
  
  export function SearchPage() {
+   const navigate = useNavigate()
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedSource, setSelectedSource] = useState<string>('')
+   const [searchType, setSearchType] = useState<'videos' | 'segments'>('videos')
    const debouncedQuery = useDebounce(searchQuery, 500)
  
      refetch
    } = useQuery({
-     queryKey: ['search', debouncedQuery, selectedSource],
+     queryKey: ['search', searchType, debouncedQuery, selectedSource],
      queryFn: async () => {
        if (!debouncedQuery) return { results: [], count: 0, query: '' }
        
-       const response = await fetch('/api/search/basic', {
-         method: 'POST',
-         headers: {
-           'Content-Type': 'application/json'
-         },
-         body: JSON.stringify({
-           query: debouncedQuery,
-           limit: 20,
-           filters: {
-             ...(selectedSource && { source: selectedSource })
-           }
-         })
-       })
-       
-       if (!response.ok) {
-         throw new Error('Failed to search videos')
-       }
-       return response.json()
+       if (searchType === 'videos') {
+         const response = await fetch('/api/search/basic', {
+           method: 'POST',
+           headers: {
+             'Content-Type': 'application/json'
+           },
+           body: JSON.stringify({
+             query: debouncedQuery,
+             limit: 20,
+             filters: {
+               ...(selectedSource && { source: selectedSource })
+             }
+           })
+         })
+         
+         if (!response.ok) {
+           throw new Error('Failed to search videos')
+         }
+         return response.json()
+       } else {
+         const response = await fetch(`/api/search/segments?query=${encodeURIComponent(debouncedQuery)}&limit=20&threshold=0.5`)
+         
+         if (!response.ok) {
+           throw new Error('Failed to search segments')
+         }
+         const segments = await response.json()
+         return {
+           results: segments,
+           count: segments.length,
+           query: debouncedQuery
+         }
+       }
      },
      enabled: Boolean(debouncedQuery)
    })
+ 
+   const handleSegmentClick = (segment: SegmentResult) => {
+     navigate(`/videos/${segment.video_id}?start=${segment.start_time}&end=${segment.end_time}`)
+   }
  
    if (isError) {
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
-             {error instanceof Error ? error.message : 'Failed to search videos'}
+             {error instanceof Error ? error.message : 'Failed to search'}
            </AlertDescription>
          </Alert>
            className="max-w-sm"
          />
-         <Select value={selectedSource} onValueChange={setSelectedSource}>
+         <Select value={searchType} onValueChange={(value: 'videos' | 'segments') => setSearchType(value)}>
            <SelectTrigger className="w-[180px]">
-             <SelectValue placeholder="All Sources" />
-           </SelectTrigger>
-           <SelectContent>
-             <SelectItem value="ALL">All Sources</SelectItem>
-             <SelectItem value="YOUTUBE">YouTube</SelectItem>
-             <SelectItem value="LOOM">Loom</SelectItem>
-           </SelectContent>
-         </Select>
+             <SelectValue placeholder="Search Type" />
+           </SelectTrigger>
+           <SelectContent>
+             <SelectItem value="videos">Videos</SelectItem>
+             <SelectItem value="segments">Segments</SelectItem>
+           </SelectContent>
+         </Select>
+         {searchType === 'videos' && (
+           <Select value={selectedSource} onValueChange={setSelectedSource}>
+             <SelectTrigger className="w-[180px]">
+               <SelectValue placeholder="All Sources" />
+             </SelectTrigger>
+             <SelectContent>
+               <SelectItem value="ALL">All Sources</SelectItem>
+               <SelectItem value="YOUTUBE">YouTube</SelectItem>
+               <SelectItem value="LOOM">Loom</SelectItem>
+             </SelectContent>
+           </Select>
+         )}
        </div>
  
              Found {searchResults.count} results for "{searchResults.query}"
            </div>
-           <VideoGrid videos={searchResults.results || []} isLoading={isLoading} />
+           {searchType === 'videos' ? (
+             <VideoGrid videos={searchResults.results || []} isLoading={isLoading} />
+           ) : (
+             <div className="grid grid-cols-1 gap-4">
+               {searchResults.results.map((segment: SegmentResult) => (
+                 <Card
+                   key={segment.id}
+                   className="cursor-pointer hover:shadow-md transition-shadow"
+                   onClick={() => handleSegmentClick(segment)}
+                 >
+                   <CardContent className="p-4">
+                     <div className="flex justify-between items-start mb-2">
+                       <div className="text-sm text-muted-foreground">
+                         {Math.floor(segment.start_time / 60)}:{String(Math.floor(segment.start_time % 60)).padStart(2, '0')} - {Math.floor(segment.end_time / 60)}:{String(Math.floor(segment.end_time % 60)).padStart(2, '0')}
+                       </div>
+                       <div className="text-sm text-muted-foreground">
+                         {Math.round(segment.similarity * 100)}% match
+                       </div>
+                     </div>
+                     <p className="text-sm">{segment.text}</p>
+                   </CardContent>
+                 </Card>
+               ))}
+             </div>
+           )}
          </>
        )}
```

---

_****_

Now let me check if we need to update the video detail page to handle the timestamp parameters. Let me search for the video detail page component.

---

_****_



---

_****_

Now let me check if we need to update the video detail page to handle the timestamp parameters. Let me search for the video detail page component.

---

_****_



---

_****_



---



---

