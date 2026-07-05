"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, PlayCircle, Heart } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

type VideoDetail = {
  id: string;
  user_id: string;
  record_ms: number;
  video_url: string;
  thumbnail?: string | null;
  description?: string | null;
  visibility: "PUBLIC" | "PRIVATE";
  views: number;
  likes: number;
  created_at: string;
  user: { id: string; username: string; avatar?: string | null };
  map: { id: string; name: string };
  car: { id: string; name: string; car_class: string };
  pet?: { id: string; name: string } | null;
};

function formatMsToTime(ms: number) {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const milliseconds = ms % 1000;
  return `${minutes}:${seconds.toString().padStart(2, "0")}.${milliseconds
    .toString()
    .padStart(3, "0")}`;
}

export default function VideoPage() {
  const params = useParams<{ video_id: string }>();
  const router = useRouter();
  const videoId = params?.video_id;

  const [data, setData] = useState<VideoDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [forbidden, setForbidden] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isLiking, setIsLiking] = useState(false);

  const handleLike = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        toast.error("Vui lòng đăng nhập để thích record này");
        router.push("/login");
        return;
      }
      setIsLiking(true);
      const res = await api.post(`/videos/${videoId}/like`);
      setData((prev) => prev ? { ...prev, likes: res.data.likes } : prev);
      toast.success("Đã thích!");
    } catch (e: any) {
      if (e?.response?.status === 401) {
        toast.error("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại");
        router.push("/login");
      } else {
        toast.error("Lỗi khi thích video");
      }
    } finally {
      setIsLiking(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!videoId) return;

      // Removed redirect so guests can view


      setLoading(true);
      setForbidden(false);
      setError(null);

      try {
        const res = await api.get(`/videos/${videoId}`);
        if (cancelled) return;
        setData(res.data as VideoDetail);
      } catch (e: any) {
        if (cancelled) return;

        const status = e?.response?.status;
        if (status === 401) {
          toast.error("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại");
          localStorage.removeItem("token");
          router.push("/login");
          return;
        }
        if (status === 403) {
          setForbidden(true);
          return;
        }

        setError(e?.response?.data?.detail || e?.message || "Tải dữ liệu thất bại");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [videoId, router]);

  if (loading) {
    return (
      <div className="p-6 md:p-10 space-y-4">
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (forbidden) {
    return (
      <div className="p-6 md:p-10">
        <Card className="border-yellow-500/30 bg-yellow-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="text-yellow-400" />
              Không có quyền xem
            </CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">
            Record này ở chế độ <span className="text-yellow-300 font-semibold">PRIVATE</span>. Chỉ người đăng hoặc ADMIN mới được xem.
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 md:p-10">
        <Card className="border-red-500/30 bg-red-500/5">
          <CardHeader>
            <CardTitle className="text-red-300">Tải dữ liệu thất bại</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-300">{error}</CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  const petName = data.pet?.name;

  return (
    <div className="p-6 md:p-10 space-y-6">
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Record Detail</h1>
          <p className="text-gray-400 mt-2">
            {data.user.username} • {data.map.name}
          </p>
        </div>

        <div className="flex gap-3">
          <Badge variant="outline" className="bg-gray-900/40 text-gray-200 border-white/10">
            {data.visibility}
          </Badge>
          <Badge variant="outline" className="bg-green-900/20 text-green-300 border-green-900/50">
            {formatMsToTime(data.record_ms)}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-gray-900/30 border-white/10">
          <CardHeader>
            <CardTitle className="flex items-center justify-between gap-3">
              <span>Video</span>
              <Link href={data.video_url || "#"} target="_blank" rel="noreferrer">
                <Button variant="ghost" className="text-blue-400 hover:text-blue-300 hover:bg-blue-900/20">
                  <PlayCircle className="mr-2" size={18} />
                  Mở video
                </Button>
              </Link>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {data.thumbnail ? (
              // thumbnail as image fallback (video_url might be youtube)
              // eslint-disable-next-line @next/next/no-img-element
              <img src={data.thumbnail} alt="thumbnail" className="w-full rounded-xl border border-white/10" />
            ) : (
              <div className="h-64 rounded-xl border border-white/10 flex items-center justify-center text-gray-500">
                Chưa có thumbnail
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-gray-900/30 border-white/10">
          <CardHeader>
            <CardTitle>Thông tin</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-gray-200">
            <div className="flex items-center justify-between gap-3">
              <span className="text-gray-400">Player</span>
              <span className="font-semibold">{data.user.username}</span>
            </div>

            <div className="flex items-center justify-between gap-3">
              <span className="text-gray-400">Car</span>
              <span className="font-semibold">{data.car.name}</span>
            </div>

            <div className="flex items-center justify-between gap-3">
              <span className="text-gray-400">Pet</span>
              <span className="font-semibold">
                {petName && petName !== "None" ? petName : "-"}
              </span>
            </div>

            <div className="flex items-center justify-between gap-3">
              <span className="text-gray-400">Views</span>
              <span className="font-semibold">{data.views}</span>
            </div>

            <div className="flex items-center justify-between gap-3">
              <span className="text-gray-400">Likes</span>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{data.likes}</span>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleLike} 
                  disabled={isLiking}
                  className="h-8 w-8 p-0 text-pink-500 hover:text-pink-400 hover:bg-pink-500/10"
                >
                  <Heart size={18} className={isLiking ? "animate-pulse" : ""} />
                </Button>
              </div>
            </div>

            {data.description ? (
              <div className="pt-3 text-gray-300">
                <span className="text-gray-400 block mb-1">Mô tả</span>
                {data.description}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
