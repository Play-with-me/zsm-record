"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, useEffect, useRef } from "react";

export default function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        // Don't use stale cache - always refetch on mount
        staleTime: 0,
        refetchOnWindowFocus: true,
        refetchInterval: 3000, // Fetch data continuously every 3s to avoid missing data
      },
    },
  }));
  const lastTokenRef = useRef<string | null>(
    typeof window !== "undefined" ? localStorage.getItem("token") : null
  );

  useEffect(() => {
    // Listen for token changes from other tabs
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "token") {
        lastTokenRef.current = e.newValue;
        // resetQueries clears cache AND triggers refetch for active queries
        queryClient.resetQueries();
      }
    };
    window.addEventListener("storage", handleStorageChange);

    // Poll for token changes within the same tab (localStorage events
    // only fire across tabs, not within the same tab)
    const interval = setInterval(() => {
      const currentToken = localStorage.getItem("token");
      if (currentToken !== lastTokenRef.current) {
        lastTokenRef.current = currentToken;
        // resetQueries clears cache AND triggers refetch for active queries
        queryClient.resetQueries();
      }
    }, 300);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, [queryClient]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
