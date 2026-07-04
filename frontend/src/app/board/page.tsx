"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { FormCombobox } from "@/components/form-combobox";
import { ExternalLink, Trophy, Clock, PlayCircle } from "lucide-react";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";

export default function RecordBoardPage() {
  const [mapId, setMapId] = useState("");
  const [carId, setCarId] = useState("");
  const [petId, setPetId] = useState("");

  const { data: maps = [] } = useQuery({ queryKey: ["maps"], queryFn: async () => (await api.get("/maps")).data });
  const { data: cars = [] } = useQuery({ queryKey: ["cars"], queryFn: async () => (await api.get("/cars")).data });
  const { data: pets = [] } = useQuery({ queryKey: ["pets"], queryFn: async () => (await api.get("/pets")).data });

  const { data: board = [], isLoading } = useQuery({
    queryKey: ["record-board", mapId, carId, petId],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (mapId) params.append("map_id", mapId);
      if (carId) params.append("car_id", carId);
      if (petId) params.append("pet_id", petId);
      const res = await api.get(`/record-board?${params.toString()}`);
      return res.data;
    },
    enabled: true // Always fetch, even without filters (shows overall fastest across all maps/cars which might be chaotic, but let's encourage map filtering)
  });

  const formatMsToTime = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;
    return `${minutes}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
  };

  const mapOptions = maps.map((m: any) => ({ label: m.name, value: m.id }));
  const carOptions = cars.map((c: any) => ({ label: c.name, value: c.id }));
  const petOptions = pets.map((p: any) => ({ label: p.name, value: p.id }));

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
            <Trophy className="text-yellow-500" size={36} />
            Record Board
          </h1>
          <p className="text-gray-400 mt-2">Bảng vàng vinh danh những tay đua kiệt xuất nhất.</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-900/50 p-6 rounded-2xl border border-white/10 backdrop-blur-md">
        <h2 className="text-lg font-semibold mb-4 text-gray-200">Bộ lọc tìm kiếm</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Map (Bản đồ)</label>
            <FormCombobox options={mapOptions} value={mapId} onChange={setMapId} placeholder="All Maps..." />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Car (Xe)</label>
            <FormCombobox options={carOptions} value={carId} onChange={setCarId} placeholder="All Cars..." />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Pet (Thú cưng)</label>
            <FormCombobox options={petOptions} value={petId} onChange={setPetId} placeholder="All Pets..." />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-gray-900/40 rounded-2xl border border-white/10 overflow-hidden backdrop-blur-md">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-black/40">
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="w-[100px] text-center font-bold text-gray-300">Rank</TableHead>
                <TableHead className="font-bold text-gray-300">Player</TableHead>
                <TableHead className="font-bold text-gray-300">Car</TableHead>
                <TableHead className="font-bold text-gray-300">Pet</TableHead>
                <TableHead className="font-bold text-gray-300">Record</TableHead>
                <TableHead className="text-right font-bold text-gray-300">Video</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i} className="border-white/5">
                    <TableCell><Skeleton className="h-6 w-8 mx-auto" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-20" /></TableCell>
                    <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto" /></TableCell>
                  </TableRow>
                ))
              ) : board.length === 0 ? (
                <TableRow className="border-white/5 hover:bg-transparent">
                  <TableCell colSpan={6} className="h-32 text-center text-gray-500">
                    Chưa có kỷ lục nào thỏa mãn điều kiện.
                  </TableCell>
                </TableRow>
              ) : (
                board.map((entry: any) => (
                  <TableRow key={entry.video_id} className="border-white/5 hover:bg-white/5 transition-colors">
                    <TableCell className="text-center">
                      {entry.rank === 1 ? (
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-yellow-500/20 text-yellow-500 font-bold border border-yellow-500/50 shadow-[0_0_10px_rgba(234,179,8,0.5)]">1</span>
                      ) : entry.rank === 2 ? (
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-300/20 text-gray-300 font-bold border border-gray-300/50">2</span>
                      ) : entry.rank === 3 ? (
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-orange-700/20 text-orange-400 font-bold border border-orange-700/50">3</span>
                      ) : (
                        <span className="font-mono text-gray-400">{entry.rank}</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8 border border-white/10">
                          <AvatarImage src={entry.player.avatar} />
                          <AvatarFallback className="bg-gray-800 text-xs">{entry.player.username.charAt(0).toUpperCase()}</AvatarFallback>
                        </Avatar>
                        <span className="font-semibold">{entry.player.username}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-blue-900/20 text-blue-300 border-blue-900/50">
                        {entry.car.name}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {entry.pet?.name && entry.pet.name !== "None" ? (
                        <Badge variant="outline" className="bg-purple-900/20 text-purple-300 border-purple-900/50">
                          {entry.pet.name}
                        </Badge>
                      ) : <span className="text-gray-600 text-sm italic">-</span>}
                    </TableCell>
                    <TableCell>
                      <div className="font-mono font-bold text-lg tracking-wider text-green-400 flex items-center gap-2">
                        <Clock size={16} className="text-gray-500" />
                        {formatMsToTime(entry.record_ms)}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/video/${entry.video_id}`}>
                        <Button variant="ghost" size="icon" className="text-blue-400 hover:text-blue-300 hover:bg-blue-900/20">
                          <PlayCircle size={20} />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
