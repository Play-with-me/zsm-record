"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import Link from "next/link";
import { UserPlus } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Mật khẩu xác nhận không khớp");
      return;
    }

    if (password.length < 6) {
      toast.error("Mật khẩu phải có ít nhất 6 ký tự");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/register", {
        username,
        email,
        password,
      });

      toast.success("Đăng ký thành công! Đang đăng nhập...");

      // Auto-login after register
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const loginRes = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("token", loginRes.data.access_token);
      // Full reload to refresh all data with the new user's permissions
      window.location.replace("/");
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      toast.error(detail || "Đăng ký thất bại, vui lòng thử lại");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <Card className="w-full max-w-md bg-gray-900/40 border-white/10 backdrop-blur-md shadow-2xl">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center mb-2">
            <UserPlus size={28} className="text-white" />
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight">Đăng ký tài khoản</CardTitle>
          <CardDescription className="text-gray-400">
            Tạo tài khoản để bắt đầu chia sẻ record của bạn
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleRegister} className="space-y-5">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Tên đăng nhập</label>
              <Input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="bg-black/50 border-white/10 focus:border-purple-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Email</label>
              <Input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-black/50 border-white/10 focus:border-purple-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Mật khẩu</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-black/50 border-white/10 focus:border-purple-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">Xác nhận mật khẩu</label>
              <Input
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="bg-black/50 border-white/10 focus:border-purple-500"
              />
            </div>
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 font-semibold text-white shadow-lg shadow-purple-500/20"
              disabled={loading}
            >
              {loading ? "Đang đăng ký..." : "Đăng ký"}
            </Button>
          </form>
          <p className="text-center text-sm text-gray-400 mt-6">
            Đã có tài khoản?{" "}
            <Link href="/login" className="text-purple-400 hover:text-purple-300 font-medium transition">
              Đăng nhập
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
