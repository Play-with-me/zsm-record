"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useEffect, useState } from "react";
import api from "@/lib/api";

export default function Navbar() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const res = await api.get("/auth/me");
          setUser(res.data);
        }
      } catch (err) {
        console.error("Failed to fetch user");
      }
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/";
  };

  return (
    <nav className="border-b bg-black text-white/90 sticky top-0 z-50 backdrop-blur-md bg-black/80">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
          ZSM Record
        </Link>

        <div className="flex gap-6 items-center">
          <Link href="/board" className="text-sm font-medium hover:text-white transition">
            Record Board
          </Link>
          <Link href="/upload" className="text-sm font-medium hover:text-white transition">
            Upload
          </Link>

          {user ? (
            <div className="flex items-center gap-4">
              {user.role === "ADMIN" && (
                <Link href="/admin" className="text-sm font-medium text-orange-400 hover:text-orange-300 transition">
                  Admin Panel
                </Link>
              )}
              <Avatar className="h-8 w-8">
                <AvatarImage src={user.avatar} />
                <AvatarFallback className="bg-gray-800 text-white">{user.username.charAt(0).toUpperCase()}</AvatarFallback>
              </Avatar>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="text-red-400 hover:text-red-300 hover:bg-red-900/20">
                Logout
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login">
                <Button variant="ghost" size="sm">Login</Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-white">Register</Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
