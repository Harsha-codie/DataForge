import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Database, Lock, Mail, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF7F2] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-[560px]">
        <div className="text-center mb-8">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-[1.4rem] border border-[#E7E5E4] bg-white shadow-[0_12px_32px_rgba(224,90,43,0.12)] text-[#E05A2B]">
            <Database className="h-7 w-7" />
          </div>
          <h2 className="mt-6 font-display text-4xl sm:text-5xl tracking-[-0.04em] text-[#1C1917]">
            Sign in to DataForge
          </h2>
          <p className="mt-4 text-lg text-[#78716C]">
            Intelligent Data Preparation & ML Readiness Platform
          </p>
        </div>

        <div className="rounded-[2rem] border border-[#E7E5E4] bg-white p-5 shadow-[0_24px_80px_rgba(28,25,23,0.08)] sm:p-8">
          {error && (
            <div className="mb-5 flex items-center gap-2 rounded-xl border border-[#F5C4B3] bg-[#FFF2ED] p-3 text-xs text-[#B45309]">
              <AlertCircle className="h-4 w-4 shrink-0 text-[#E05A2B]" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-semibold text-[#1C1917]">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3.5 h-4 w-4 text-[#78716C]" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@dataforge.io"
                  className="w-full rounded-xl border border-[#E7E5E4] bg-[#FAF7F2] py-3 pl-10 pr-3 text-sm text-[#1C1917] placeholder:text-[#A8A29E] focus:border-[#E05A2B] focus:outline-none focus:ring-2 focus:ring-[#E05A2B]/20"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-semibold text-[#1C1917]">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 h-4 w-4 text-[#78716C]" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-[#E7E5E4] bg-[#FAF7F2] py-3 pl-10 pr-3 text-sm text-[#1C1917] placeholder:text-[#A8A29E] focus:border-[#E05A2B] focus:outline-none focus:ring-2 focus:ring-[#E05A2B]/20"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-[#E05A2B] px-4 py-3.5 text-base font-semibold text-white shadow-[0_12px_28px_rgba(224,90,43,0.22)] transition-all duration-200 hover:-translate-y-0.5 hover:bg-[#d75229] disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 border-t border-[#E7E5E4] pt-6 text-center text-sm text-[#78716C]">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-[#E05A2B] transition-colors hover:text-[#d75229]">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
