"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { useParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Map, Car, Clock, Eye, ThumbsUp, Calendar, PlayCircle } from "lucide-react";
import Link from "next/link";
import React from "react"; // Ensure React is in scope for use

export default function VideoDetailPage() {
  const { id } = useParams();

  const { data: video, isLoading, isError } = useQuery({
    queryKey: ["video", id],
    queryFn: async () => {
      const res = await api.get(`/videos/${id}`);
      return res.data;
    }
  });

  const { data: relatedVideos = [] } = useQuery({
    queryKey: ["related-videos", video?.map_id, video?.car_id],
    queryFn: async () => {
      const res = await api.get(`/videos?map_id=${video.map_id}&car_id=${video.car_id}&limit=5`);
      return res.data.filter((v: any) => v.id !== id);
    },
    enabled: !!video
  });

  const formatMsToTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  };

  const renderVideoPlayer = (url: string) => {
    try {
      const urlObj = new URL(url);
      if (urlObj.hostname.includes("youtube.com") || urlObj.hostname.includes("youtu.be")) {
        let videoId = "";
        if (urlObj.hostname.includes("youtu.be")) {
          videoId = urlObj.pathname.slice(1);
        } else {
          videoId = urlObj.searchParams.get("v") || "";
        }
        if (videoId) {
          return (
            <iframe
              className="w-full h-full absolute top-0 left-0"
              src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          );
        }
      }
    } catch (e) {
      // Not a valid URL or not youtube
    }
    
    // Fallback to standard video tag or just a link if it's drive
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 border border-white/10 text-gray-400 p-8">
        <PlayCircle size={64} className="mb-4 opacity-50" />
        <p>Video cannot be embedded directly.</p>
        <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline mt-2">
          Open Video Link
        </a>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <Skeleton className="w-full aspect-video rounded-3xl" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-10 w-2/3" />
            <Skeleton className="h-20 w-full" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (isError || !video) {
    return (
      <div className="text-center py-20 bg-red-900/20 rounded-xl border border-red-900/50 text-red-400">
        Video not found or failed to load.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Video Player Section */}
      <div className="relative w-full aspect-video rounded-3xl overflow-hidden bg-black shadow-2xl border border-white/10 ring-1 ring-white/5">
        {renderVideoPlayer(video.video_url)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex flex-col gap-4">
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">
              {video.map.name} - {video.car.name}
            </h1>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 bg-gray-900/50 p-4 rounded-xl border border-white/5 backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <Avatar className="h-10 w-10 border border-white/10">
                  <AvatarImage src={video.user.avatar} />
                  <AvatarFallback className="bg-gray-800 text-white font-bold">{video.user.username.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="text-gray-200 font-medium">Uploaded by</span>
                  <span className="font-bold text-white">{video.user.username}</span>
                </div>
              </div>
              <div className="h-8 w-px bg-white/10 hidden md:block mx-2"></div>
              <div className="flex items-center gap-2">
                <Calendar size={18} className="text-gray-500" />
                <span>{new Date(video.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Eye size={18} className="text-gray-500" />
                <span>{video.views} views</span>
              </div>
              <div className="flex items-center gap-2">
                <ThumbsUp size={18} className="text-gray-500" />
                <span>{video.likes} likes</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/30 p-6 rounded-2xl border border-white/5">
            <h2 className="text-xl font-bold mb-4 text-gray-200">Description</h2>
            <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
              {video.description || "No description provided."}
            </p>
          </div>
        </div>

        {/* Sidebar Info */}
        <div className="space-y-6">
          <Card className="bg-gradient-to-br from-gray-900/80 to-black/80 border-white/10 shadow-xl backdrop-blur-md">
            <CardContent className="p-6 space-y-6">
              <div className="text-center space-y-2 pb-6 border-b border-white/10">
                <p className="text-sm text-gray-400 font-medium uppercase tracking-wider">Record Time</p>
                <div className="text-5xl font-mono font-black text-transparent bg-clip-text bg-gradient-to-br from-green-400 to-emerald-600 drop-shadow-sm">
                  {formatMsToTime(video.record_ms)}
                </div>
              </div>

              <div className="space-y-4 pt-2">
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2 text-gray-400"><Map size={18} /> Map</span>
                  <Badge variant="secondary" className="bg-blue-900/30 text-blue-300 hover:bg-blue-900/40 text-sm">
                    {video.map.name}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2 text-gray-400"><Car size={18} /> Car</span>
                  <Badge variant="secondary" className="bg-orange-900/30 text-orange-300 hover:bg-orange-900/40 text-sm">
                    {video.car.name}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="flex items-center gap-2 text-gray-400">🐾 Pet</span>
                  {video.pet?.name && video.pet.name !== "None" ? (
                    <Badge variant="secondary" className="bg-purple-900/30 text-purple-300 hover:bg-purple-900/40 text-sm">
                      {video.pet.name}
                    </Badge>
                  ) : (
                    <span className="text-sm text-gray-600 italic">None</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Related Records */}
          {relatedVideos.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-200">Related Records (Same Map & Car)</h3>
              <div className="space-y-3">
                {relatedVideos.map((rv: any) => (
                  <Link href={`/video/${rv.id}`} key={rv.id} className="block group">
                    <div className="flex items-center gap-4 p-3 rounded-xl bg-gray-900/40 border border-white/5 hover:bg-gray-800/60 hover:border-white/20 transition-all">
                      <div className="w-24 aspect-video rounded-md overflow-hidden relative flex-shrink-0">
                         <img 
                            src={rv.map.image || `https://placehold.co/600x400/1e1b4b/fff?text=${rv.map.name}`}
                            alt={rv.map.name}
                            className="object-cover w-full h-full opacity-80 group-hover:opacity-100 group-hover:scale-110 transition-all"
                          />
                          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                             <PlayCircle size={20} className="text-white" />
                          </div>
                      </div>
                      <div className="flex flex-col overflow-hidden">
                        <span className="text-green-400 font-mono font-bold">{formatMsToTime(rv.record_ms)}</span>
                        <span className="text-sm text-gray-300 truncate">{rv.user.username}</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
