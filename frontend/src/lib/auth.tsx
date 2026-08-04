"use client";

/**
 * AgriNova AI — Auth Context
 *
 * Manages JWT authentication state, login/logout, and route protection.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { authAPI, type UserData, type TokenData } from "@/lib/api";

interface AuthContextType {
  user: UserData | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; phone?: string }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("agrinova_token");
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const profile = await authAPI.getProfile();
      setUser(profile);
    } catch {
      localStorage.removeItem("agrinova_token");
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    const data: TokenData = await authAPI.login({ email, password });
    localStorage.setItem("agrinova_token", data.access_token);
    setUser(data.user);
    router.push("/dashboard");
  };

  const register = async (formData: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
  }) => {
    const data: TokenData = await authAPI.register(formData);
    localStorage.setItem("agrinova_token", data.access_token);
    setUser(data.user);
    router.push("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("agrinova_token");
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
