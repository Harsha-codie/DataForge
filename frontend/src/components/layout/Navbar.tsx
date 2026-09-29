import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useDataset } from '../../context/DatasetContext';
import { 
  Database, 
  GitBranch, 
  LogOut, 
  User, 
  Layers, 
  Clock, 
  Sparkles,
  ChevronDown
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { dataset, selectedVersionId, versions, setSelectedVersionId } = useDataset();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      navigate('/login');
    }
  };

  const currentVer = versions.find(v => v.id === selectedVersionId) || dataset?.current_version;

  return (
    <header className="sticky top-0 z-40 border-b border-[#E7E5E4] bg-[#FFFDFB]/90 backdrop-blur-md text-[#1C1917] shadow-[0_10px_30px_rgba(28,25,23,0.04)]">
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        <div className="flex items-center gap-4">
          <Link to="/dashboard" className="group flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-[#E7E5E4] bg-[#F8E5DD] text-[#E05A2B] shadow-[0_8px_24px_rgba(224,90,43,0.12)] transition-all group-hover:bg-[#E05A2B] group-hover:text-white">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 text-lg font-extrabold tracking-tight text-[#1C1917]">
                DATAFORGE
                <span className="rounded border border-[#E7E5E4] bg-[#F8E5DD] px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-[#E05A2B]">ML READY</span>
              </div>
            </div>
          </Link>

          {dataset && (
            <div className="hidden items-center gap-3 border-l border-[#E7E5E4] pl-4 text-sm md:flex">
              <div className="flex items-center gap-2 rounded-md border border-[#E7E5E4] bg-[#FAF7F2] px-2.5 py-1">
                <span className="font-medium text-[#78716C]">Dataset:</span>
                <Link to={`/datasets/${dataset.id}/overview`} className="max-w-[180px] truncate font-semibold text-[#1C1917] transition-colors hover:text-[#E05A2B]">
                  {dataset.name}
                </Link>
              </div>

              <div className="flex items-center gap-1.5 rounded-md border border-[#E7E5E4] bg-[#F8E5DD] px-2.5 py-1 text-[#E05A2B]">
                <GitBranch className="h-3.5 w-3.5" />
                <span className="text-xs font-semibold">
                  v{currentVer?.version_number || 1} ({currentVer?.branch_name || 'main'})
                </span>
                {versions.length > 1 && (
                  <select
                    className="cursor-pointer border-none bg-transparent pr-1 text-xs text-[#1C1917] outline-none"
                    value={selectedVersionId || ''}
                    onChange={(e) => setSelectedVersionId(e.target.value)}
                  >
                    {versions.map((v) => (
                      <option key={v.id} value={v.id} className="bg-white text-[#1C1917]">
                        v{v.version_number} - {v.transformation_operation} ({v.row_count} rows)
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="flex items-center gap-2 text-xs text-[#78716C]">
                <span>{currentVer?.row_count?.toLocaleString() || 0} rows</span>
                <span>•</span>
                <span>{currentVer?.column_count || 0} cols</span>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/jobs"
            className="flex items-center gap-1.5 rounded-lg border border-[#E7E5E4] bg-[#FAF7F2] px-3 py-1.5 text-xs font-medium text-[#1C1917] transition-colors hover:border-[#E05A2B] hover:text-[#E05A2B]"
          >
            <Clock className="h-3.5 w-3.5 text-[#E05A2B]" />
            <span>Jobs</span>
          </Link>

          {user && (
            <div className="flex items-center gap-3 border-l border-[#E7E5E4] pl-3">
              <div className="flex items-center gap-2 text-sm text-[#1C1917]">
                <div className="flex h-7 w-7 items-center justify-center rounded-full border border-[#E7E5E4] bg-[#F8E5DD] text-xs font-bold text-[#E05A2B]">
                  {user.full_name ? user.full_name[0].toUpperCase() : user.email[0].toUpperCase()}
                </div>
                <span className="hidden text-xs font-medium text-[#1C1917] sm:inline">
                  {user.full_name || user.email.split('@')[0]}
                </span>
              </div>

              <button
                onClick={handleLogout}
                title="Log out"
                className="rounded-lg p-1.5 text-[#78716C] transition-colors hover:bg-[#F8E5DD] hover:text-[#E05A2B]"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
