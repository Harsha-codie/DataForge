import React, { useEffect } from 'react';
import { Outlet, useParams, useLocation } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { DatasetSubNav } from './DatasetSubNav';
import { useDataset } from '../../context/DatasetContext';

export const AppLayout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const { dataset, loadDataset } = useDataset();

  const isDatasetRoute = location.pathname.includes('/datasets/') && id;

  useEffect(() => {
    if (id && (!dataset || dataset.id !== id)) {
      loadDataset(id);
    }
  }, [id]);

  return (
    <div className="min-h-screen bg-[#FAF7F2] text-[#1C1917] flex flex-col font-sans">
      <Navbar />
      <div className="min-h-0 flex-1 flex bg-[#FAF7F2]">
        <Sidebar />
        <main className="min-h-0 flex-1 flex flex-col min-w-0 overflow-y-auto bg-[#FAF7F2]">
          {isDatasetRoute && <DatasetSubNav />}
          <div className="flex-1 p-6 max-w-7xl w-full mx-auto">
            {children ?? <Outlet />}
          </div>
        </main>
      </div>
    </div>
  );
};
