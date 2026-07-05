"use client";

import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { PlayCircle, Clock, Eye, ThumbsUp, Car, Map, User } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const { data: videos, isLoading, isError } = useQuery({
    queryKey: ["latest-videos", token],
    queryFn: async () => {
      const res = await api.get("/videos?limit=8");
      return res.data;
    }
  });

  const formatMsToTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <section className="text-center py-20 bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden backdrop-blur-xl">
        <div className="absolute inset-0 bg-[url('https://placehold.co/1920x1080/000000/111111?text=ZSM')] opacity-10 bg-cover bg-center mix-blend-overlay"></div>
        <div className="relative z-10 space-y-6">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
            Thư viện Record <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-blue-500">
              ZingSpeed Mobile
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Khám phá, chia sẻ và so sánh các kỹ năng đỉnh cao từ cộng đồng người chơi ZSM.
          </p>
          <div className="flex justify-center gap-4 pt-4">
            <Link href="/board" className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full font-semibold shadow-lg shadow-blue-500/20 transition-all hover:scale-105">
              Xem Bảng Xếp Hạng
            </Link>
            <Link href="/upload" className="bg-white/10 hover:bg-white/20 text-white px-8 py-3 rounded-full font-semibold border border-white/10 transition-all hover:scale-105 backdrop-blur-sm">
              Đăng Record
            </Link>
          </div>
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold tracking-tight">Latest Records</h2>
          <Link href="/board" className="text-blue-400 hover:text-blue-300 font-medium">View all &rarr;</Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <Card key={i} className="bg-gray-900/50 border-gray-800 overflow-hidden">
                <Skeleton className="h-48 w-full rounded-none" />
                <CardContent className="p-4 space-y-3">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-4 w-1/2" />
                  <div className="flex gap-2 pt-2">
                    <Skeleton className="h-6 w-16 rounded-full" />
                    <Skeleton className="h-6 w-16 rounded-full" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : isError ? (
          <div className="text-center py-10 bg-red-900/20 rounded-xl border border-red-900/50 text-red-400">
            Failed to load records. Please try again later.
          </div>
        ) : videos && videos.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {videos.map((video: any) => (
              <Link href={`/video/${video.id}`} key={video.id}>
                <Card className="bg-gray-900/40 border-white/5 hover:border-purple-500/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(168,85,247,0.2)] hover:-translate-y-1 group overflow-hidden cursor-pointer backdrop-blur-sm">
                  <div className="relative aspect-video overflow-hidden">
                    <img 
                      src={video.map.image || `https://placehold.co/600x400/1e1b4b/fff?text=${video.map.name}`}
                      alt={video.map.name}
                      className="object-cover w-full h-full opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                    <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md px-2 py-1 rounded text-sm font-mono font-bold text-blue-400 flex items-center gap-1">
                      <Clock size={14} />
                      {formatMsToTime(video.record_ms)}
                    </div>
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <PlayCircle size={48} className="text-white drop-shadow-lg" />
                    </div>
                  </div>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-lg truncate pr-2 flex items-center gap-2">
                        <Map size={16} className="text-gray-400" />
                        {video.map.name}
                      </h3>
                    </div>
                    
                    <div className="space-y-1 mb-4 text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <Car size={14} />
                        <span className="truncate">{video.car.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <User size={14} />
                        <span className="truncate text-gray-300">{video.user.username}</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-center text-xs text-gray-500 pt-3 border-t border-white/10">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1"><Eye size={14} /> {video.views}</span>
                        <span className="flex items-center gap-1"><ThumbsUp size={14} /> {video.likes}</span>
                      </div>
                      <span>{new Date(video.created_at).toLocaleDateString()}</span>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-gray-900/20 rounded-xl border border-white/5 text-gray-400">
            <p>No records found. Be the first to upload one!</p>
          </div>
        )}
      </section>
    </div>
  );
}
