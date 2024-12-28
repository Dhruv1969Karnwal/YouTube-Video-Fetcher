'use client'

import { useState, useEffect } from 'react'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Pagination } from "@/components/ui/pagination"

interface Video {
  id: string
  title: string
  description: string
  publish_date: string
  thumbnail_url: string
  channel_name: string
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([])
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchVideos()
  }, [query, page])

  const fetchVideos = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/videos?query=${query}&page=${page}`)
      const data = await response.json()
      setVideos(data.videos)
      setTotalPages(data.pages)
    } catch (error) {
      console.error('Error fetching videos:', error)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">YouTube Video Fetcher</h1>
      <div className="flex mb-4">
        <Input
          type="text"
          placeholder="Search videos..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="mr-2"
        />
        <Button onClick={() => setPage(1)}>Search</Button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {videos.map((video) => (
          <Card key={video.id}>
            <CardHeader>
              <CardTitle className="text-lg">{video.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <img src={video.thumbnail_url} alt={video.title} className="w-full mb-2" />
              <p className="text-sm mb-2">{video.description}</p>
              <p className="text-xs text-gray-500">
                Published on: {new Date(video.publish_date).toLocaleDateString()}
              </p>
              <p className="text-xs text-gray-500">Channel: {video.channel_name}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <Pagination
        className="mt-4"
        currentPage={page}
        totalPages={totalPages}
        onPageChange={setPage}
      />
    </div>
  )
}

