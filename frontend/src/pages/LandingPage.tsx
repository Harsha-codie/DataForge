import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BarChart3,
  Database,
  GitBranch,
  LayoutGrid,
  Search,
  ShieldCheck,
  Sparkles,
  Wand2,
  CheckCircle2,
  ChevronRight,
  ArrowUpRight,
} from 'lucide-react';

const metrics = [
  {
    icon: BarChart3,
    title: 'Data Profiling',
    description: 'Explore dataset structure and quality through column statistics, distributions, and missing-value insights.',
  },
  {
    icon: GitBranch,
    title: 'Version Control',
    description: 'Track transformations and dataset changes with retained history and clear lineage between versions.',
  },
  {
    icon: ShieldCheck,
    title: 'ML Readiness',
    description: 'Assess preparation quality and build a reliable foundation for downstream model training and evaluation.',
  },
];

const featureCards = [
  {
    icon: BarChart3,
    title: 'Data Profiling',
    description: 'Understand your dataset with column statistics, data types, distributions, missing values, and data quality insights.',
  },
  {
    icon: LayoutGrid,
    title: 'Interactive Visualisation',
    description: 'Explore distributions, relationships, and data quality through meaningful charts and visual summaries.',
  },
  {
    icon: Wand2,
    title: 'Transformation Builder',
    description: 'Clean and transform datasets with configurable operations such as missing-value handling, type conversion, scaling, and filtering.',
  },
  {
    icon: ShieldCheck,
    title: 'Schema Validation',
    description: 'Check datasets against expected schemas and identify missing columns, incompatible types, and structural differences.',
  },
  {
    icon: Sparkles,
    title: 'ML Readiness',
    description: 'Assess dataset quality and prepare data for machine learning through structured preprocessing and validation.',
  },
  {
    icon: GitBranch,
    title: 'Dataset Versioning',
    description: 'Track dataset changes, preserve previous versions, and maintain transformation history and lineage.',
  },
];

const workflowSteps = [
  {
    id: 'upload',
    title: 'Upload & Explore',
    description: 'Import a dataset and understand its structure, schema, and initial quality signals.',
    icon: Database,
  },
  {
    id: 'clean',
    title: 'Clean & Transform',
    description: 'Handle missing values, duplicates, and data types with guided preparation operations.',
    icon: Wand2,
  },
  {
    id: 'validate',
    title: 'Validate & Track',
    description: 'Check data quality and retain project history across versioned dataset changes.',
    icon: CheckCircle2,
  },
  {
    id: 'ml',
    title: 'Prepare for ML',
    description: 'Review readiness and prepare structured inputs for model development and experimentation.',
    icon: Sparkles,
  },
];

const workflowPanels: Record<string, { tag: string; title: string; description: string }> = {
  upload: {
    tag: 'Dataset Profiling',
    title: 'Profile structures, distributions, and quality signals',
    description: 'Inspect columns, missing values, types, and variation to understand the dataset before transformation.',
  },
  clean: {
    tag: 'Transformation Builder',
    title: 'Apply guided cleaning and conversion steps',
    description: 'Create structured, repeatable changes to resolve missing data, normalize types, and improve quality.',
  },
  validate: {
    tag: 'Data Quality & Validation',
    title: 'Verify schema integrity and quality checks',
    description: 'Compare expected structure against real data and review versioned validation outcomes with confidence.',
  },
  ml: {
    tag: 'ML Readiness',
    title: 'Prepare a cleaner foundation for model workflows',
    description: 'Assess readiness and ensure datasets are consistent, structured, and usable for ML pipelines.',
  },
};

export const LandingPage: React.FC = () => {
  const [activeWorkflow, setActiveWorkflow] = useState('upload');

  const activePanel = useMemo(() => workflowPanels[activeWorkflow], [activeWorkflow]);

  return (
    <div className="min-h-screen bg-[#FAF7F2] text-[#1C1917] antialiased">
      <header className="sticky top-0 z-40 border-b border-[#E7E5E4] bg-[#FAF7F2]/90 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E05A2B] text-white shadow-sm shadow-[#E05A2B]/25">
                <Database className="h-5 w-5" />
              </div>
              <span className="font-display text-2xl tracking-tight text-[#1C1917]">DataForge</span>
            </div>

            <div className="hidden items-center gap-8 text-sm font-medium text-[#78716C] md:flex">
              <a href="#" className="relative text-[#1C1917] after:absolute after:-bottom-2 after:left-0 after:h-[2px] after:w-full after:rounded-full after:bg-[#E05A2B]">
                Home
              </a>
              <a href="#features" className="transition-colors hover:text-[#1C1917]">Features</a>
              <a href="#platform" className="transition-colors hover:text-[#1C1917]">Platform</a>
              <a href="#docs" className="transition-colors hover:text-[#1C1917]">Documentation</a>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Search"
                className="hidden h-10 w-10 items-center justify-center rounded-full border border-[#E7E5E4] bg-white text-[#78716C] transition-colors hover:border-[#E05A2B] hover:text-[#E05A2B] sm:flex"
              >
                <Search className="h-4 w-4" />
              </button>
              <Link
                to="/register"
                className="inline-flex items-center justify-center rounded-full bg-[#E05A2B] px-5 py-2.5 text-sm font-semibold text-white transition-transform duration-200 hover:-translate-y-0.5 hover:bg-[#d6522a]"
              >
                Get Started
              </Link>
            </div>
          </nav>
        </div>
      </header>

      <main>
        <section id="platform" className="mx-auto max-w-7xl px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-20 lg:pt-16">
          <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
            <div>
              <div className="mb-6 inline-flex items-center rounded-full border border-[#E7E5E4] bg-white px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#E05A2B] shadow-sm">
                Intelligent Data Preparation
              </div>
              <h1 className="font-display text-5xl leading-[0.95] tracking-[-0.04em] text-[#1C1917] sm:text-6xl lg:text-7xl">
                Turn Raw Data
                <span className="block">Into ML-Ready Data.</span>
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-8 text-[#78716C]">
                DataForge helps you explore, clean, transform, validate, and prepare datasets for machine learning through a unified, intelligent data preparation platform.
              </p>

              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-[#E05A2B] px-6 py-3 text-base font-semibold text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-[#d6522a]"
                >
                  Start Preparing Data
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a
                  href="#features"
                  className="inline-flex items-center justify-center rounded-full border border-[#D6D3D1] bg-white px-6 py-3 text-base font-semibold text-[#1C1917] transition-all duration-200 hover:border-[#E05A2B] hover:text-[#E05A2B]"
                >
                  Explore Features
                </a>
              </div>

              <p className="mt-6 text-sm text-[#78716C]">
                From raw datasets to structured, validated, ML-ready data.
              </p>
            </div>

            <div className="relative">
              <div className="absolute -inset-6 rounded-[2rem] bg-[#F1E4D8] blur-3xl opacity-80" />
              <div className="relative overflow-hidden rounded-[2rem] border border-[#E7E5E4] bg-[#FFFDFB] p-4 shadow-[0_30px_80px_rgba(28,25,23,0.08)]">
                <div className="rounded-[1.5rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                  <div className="flex items-center justify-between border-b border-[#E7E5E4] pb-4">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-[#78716C]">Dataset overview</p>
                      <h2 className="mt-2 font-display text-2xl text-[#1C1917]">Customer Churn</h2>
                    </div>
                    <div className="rounded-full border border-[#E7E5E4] bg-white px-2.5 py-1 text-xs font-medium text-[#E05A2B]">
                      11 columns
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 sm:grid-cols-3">
                    <div className="rounded-2xl border border-[#E7E5E4] bg-white p-3">
                      <p className="text-[10px] uppercase tracking-[0.12em] text-[#78716C]">Quality</p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="font-display text-2xl text-[#1C1917]">92%</span>
                        <span className="rounded-full bg-[#F7E7DF] px-2 py-1 text-[10px] font-medium text-[#E05A2B]">Strong</span>
                      </div>
                    </div>
                    <div className="rounded-2xl border border-[#E7E5E4] bg-white p-3">
                      <p className="text-[10px] uppercase tracking-[0.12em] text-[#78716C]">Missing</p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="font-display text-2xl text-[#1C1917]">8.4%</span>
                        <span className="text-[10px] text-[#78716C]">Values</span>
                      </div>
                    </div>
                    <div className="rounded-2xl border border-[#E7E5E4] bg-white p-3">
                      <p className="text-[10px] uppercase tracking-[0.12em] text-[#78716C]">Readiness</p>
                      <div className="mt-2 flex items-center justify-between">
                        <span className="font-display text-2xl text-[#1C1917]">Ready</span>
                        <span className="rounded-full bg-[#E5F4ED] px-2 py-1 text-[10px] font-medium text-[#0F766E]">ML</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
                    <div className="rounded-2xl border border-[#E7E5E4] bg-white p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#78716C]">Missing values</p>
                        <span className="text-[10px] uppercase tracking-[0.12em] text-[#E05A2B]">Profile</span>
                      </div>

                      <div className="mt-4 flex h-24 items-end gap-2">
                        {[28, 35, 22, 52, 40, 70, 46, 62].map((value, index) => (
                          <div key={index} className="flex-1 rounded-t-xl bg-gradient-to-t from-[#E05A2B]/70 to-[#F5C9B4]" style={{ height: `${value}%` }} />
                        ))}
                      </div>
                    </div>

                    <div className="rounded-2xl border border-[#E7E5E4] bg-white p-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#78716C]">Data quality</p>
                      <div className="mt-4 space-y-3">
                        {[
                          { label: 'Nulls', value: '6.2%' },
                          { label: 'Duplicates', value: '0.4%' },
                          { label: 'Type mismatches', value: '1' },
                          { label: 'Outliers', value: '3' },
                        ].map((item) => (
                          <div key={item.label} className="flex items-center justify-between text-sm text-[#1C1917]">
                            <span>{item.label}</span>
                            <span className="font-medium text-[#78716C]">{item.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 rounded-2xl border border-[#E7E5E4] bg-white p-4">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[#78716C]">Transformation workflow</p>
                      <span className="rounded-full bg-[#F8E5DD] px-2 py-1 text-[10px] font-medium text-[#E05A2B]">Draft</span>
                    </div>

                    <div className="mt-4 space-y-3">
                      {['Normalize missing values', 'Convert tenure to integer', 'Validate schema', 'Prepare for modeling'].map((step, index) => (
                        <div key={step} className="flex items-center gap-3 text-sm text-[#1C1917]">
                          <div className={`flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-semibold ${index === 3 ? 'bg-[#E05A2B] text-white' : 'bg-[#F5EFEA] text-[#E05A2B]'}`}>
                            {index + 1}
                          </div>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-y border-[#E7E5E4] bg-[#F5F1EA]">
          <div className="mx-auto grid max-w-7xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-3 lg:px-8">
            {metrics.map(({ icon: Icon, title, description }) => (
              <div key={title} className="rounded-[1.5rem] border border-[#E7E5E4] bg-white p-5 shadow-sm transition-transform duration-200 hover:-translate-y-1">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F8E5DD] text-[#E05A2B]">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 font-display text-2xl text-[#1C1917]">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-[#78716C]">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="features" className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center rounded-full border border-[#E7E5E4] bg-white px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#E05A2B]">
              Core Capabilities
            </div>
            <h2 className="mt-6 font-display text-4xl tracking-[-0.03em] text-[#1C1917] sm:text-5xl">
              Everything You Need to Prepare Better Data
            </h2>
            <p className="mt-5 text-lg leading-8 text-[#78716C]">
              Discover the tools that help turn raw datasets into reliable, structured data ready for analysis and machine learning.
            </p>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {featureCards.map(({ icon: Icon, title, description }) => (
              <article
                key={title}
                className="group rounded-[1.75rem] border border-[#E7E5E4] bg-white p-6 transition-all duration-200 hover:-translate-y-1 hover:border-[#E05A2B]/40 hover:shadow-[0_18px_40px_rgba(224,90,43,0.08)]"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#F8E5DD] text-[#E05A2B]">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="mt-5 font-display text-2xl text-[#1C1917]">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-[#78716C]">{description}</p>
                <div className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#E05A2B]">
                  Explore feature
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="border-t border-[#E7E5E4] bg-[#FAF7F2]">
          <div className="mx-auto grid max-w-7xl gap-10 px-4 py-20 sm:px-6 lg:grid-cols-[0.9fr_1.1fr] lg:px-8">
            <div>
              <div className="inline-flex items-center rounded-full border border-[#E7E5E4] bg-white px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#E05A2B]">
                The Workflow
              </div>
              <h2 className="mt-6 font-display text-4xl tracking-[-0.03em] text-[#1C1917] sm:text-5xl">
                From Raw Data to Reliable Machine Learning Inputs
              </h2>
              <p className="mt-5 max-w-lg text-lg leading-8 text-[#78716C]">
                Follow a structured workflow to inspect, improve, validate, and prepare your datasets.
              </p>

              <div className="mt-8 space-y-4">
                {workflowSteps.map(({ id, title, description, icon: Icon }) => {
                  const isActive = activeWorkflow === id;

                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setActiveWorkflow(id)}
                      className={`group w-full rounded-[1.5rem] border p-4 text-left transition-all duration-200 ${
                        isActive
                          ? 'border-[#E05A2B] bg-[#FFFDFB] shadow-[0_15px_30px_rgba(224,90,43,0.08)]'
                          : 'border-[#E7E5E4] bg-white hover:border-[#D6D3D1]'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div
                          className={`flex h-11 w-11 items-center justify-center rounded-full ${
                            isActive ? 'bg-[#E05A2B] text-white' : 'bg-[#F8E5DD] text-[#E05A2B]'
                          }`}
                        >
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between gap-3">
                            <h3 className="font-display text-2xl text-[#1C1917]">{title}</h3>
                            {isActive && <ChevronRight className="h-5 w-5 text-[#E05A2B]" />}
                          </div>
                          <p className="mt-2 text-sm leading-6 text-[#78716C]">{description}</p>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div className="rounded-[1.75rem] border border-[#E7E5E4] bg-white p-4 shadow-sm sm:col-span-2">
                <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                  <div className="flex items-center justify-between">
                    <span className="rounded-full bg-[#F8E5DD] px-2 py-1 text-[10px] font-medium uppercase tracking-[0.14em] text-[#E05A2B]">
                      {activePanel.tag}
                    </span>
                    <ArrowUpRight className="h-4 w-4 text-[#78716C]" />
                  </div>
                  <h3 className="mt-4 font-display text-3xl leading-tight text-[#1C1917]">{activePanel.title}</h3>
                  <p className="mt-3 text-sm leading-6 text-[#78716C]">{activePanel.description}</p>

                  <div className="mt-5 flex h-28 items-end gap-2">
                    {[25, 38, 50, 64, 48, 70, 58, 82].map((value, index) => (
                      <div key={index} className="flex-1 rounded-t-xl bg-gradient-to-t from-[#E05A2B] to-[#F3C7B2]" style={{ height: `${value}%` }} />
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-[1.75rem] border border-[#E7E5E4] bg-white p-4 shadow-sm">
                <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#78716C]">Transformation</p>
                  <div className="mt-4 space-y-3">
                    {['Normalize nulls', 'Type conversion', 'Filter invalid rows', 'Prepare schema'].map((item, index) => (
                      <div key={item} className="flex items-center gap-3 text-sm text-[#1C1917]">
                        <span className={`h-2.5 w-2.5 rounded-full ${index % 2 === 0 ? 'bg-[#E05A2B]' : 'bg-[#D6D3D1]'}`} />
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-[1.75rem] border border-[#E7E5E4] bg-white p-4 shadow-sm">
                <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#78716C]">Validation</p>
                  <div className="mt-4 space-y-4">
                    {[
                      { label: 'Schema match', value: '97%' },
                      { label: 'Type mismatches', value: '2' },
                      { label: 'Missing values', value: '6.2%' },
                    ].map((item) => (
                      <div key={item.label}>
                        <div className="flex items-center justify-between text-sm text-[#1C1917]">
                          <span>{item.label}</span>
                          <span className="font-medium text-[#78716C]">{item.value}</span>
                        </div>
                        <div className="mt-2 h-2 overflow-hidden rounded-full bg-[#F3E9E2]">
                          <div className="h-full rounded-full bg-[#E05A2B]" style={{ width: item.label === 'Schema match' ? '97%' : item.label === 'Type mismatches' ? '18%' : '62%' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-[1.75rem] border border-[#E7E5E4] bg-white p-4 shadow-sm sm:col-span-2">
                <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                  <div className="flex items-center justify-between">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#78716C]">ML readiness</p>
                    <span className="text-sm font-medium text-[#E05A2B]">Ready</span>
                  </div>
                  <div className="mt-5 grid gap-3 sm:grid-cols-3">
                    {[
                      { label: 'Features', value: '14' },
                      { label: 'Completeness', value: '92%' },
                      { label: 'Target Quality', value: 'High' },
                    ].map((item) => (
                      <div key={item.label} className="rounded-2xl border border-[#E7E5E4] bg-white p-3">
                        <p className="text-[10px] uppercase tracking-[0.12em] text-[#78716C]">{item.label}</p>
                        <p className="mt-3 font-display text-2xl text-[#1C1917]">{item.value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="rounded-[2.25rem] border border-[#E7E5E4] bg-white p-8 shadow-[0_25px_60px_rgba(28,25,23,0.06)] lg:p-12">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="font-display text-4xl tracking-[-0.03em] text-[#1C1917] sm:text-5xl">
                A Clearer View of Your Data
              </h2>
              <p className="mt-5 text-lg leading-8 text-[#78716C]">
                Explore your datasets, understand data quality, and manage transformations through a clean and intuitive workspace.
              </p>
            </div>

            <div className="mt-10 overflow-hidden rounded-[2rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4 lg:p-6">
              <div className="rounded-[1.6rem] border border-[#E7E5E4] bg-white p-5">
                <div className="flex flex-col gap-5 border-b border-[#E7E5E4] pb-5 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.14em] text-[#78716C]">Dataset workspace</p>
                    <h3 className="mt-2 font-display text-3xl text-[#1C1917]">Customer Churn</h3>
                  </div>
                  <div className="flex flex-wrap gap-3 text-xs font-medium">
                    <span className="rounded-full border border-[#E7E5E4] bg-[#FAF7F2] px-2.5 py-1 text-[#78716C]">Profiling</span>
                    <span className="rounded-full border border-[#E7E5E4] bg-[#FAF7F2] px-2.5 py-1 text-[#78716C]">Quality</span>
                    <span className="rounded-full border border-[#E7E5E4] bg-[#FAF7F2] px-2.5 py-1 text-[#78716C]">Version 2</span>
                  </div>
                </div>

                <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                  <div className="space-y-4">
                    <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-[10px] uppercase tracking-[0.14em] text-[#78716C]">Column profiling</p>
                        <span className="text-[10px] uppercase tracking-[0.14em] text-[#E05A2B]">Insights</span>
                      </div>
                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        {[
                          { title: 'Age', value: '28-64' },
                          { title: 'Tenure', value: '3.2 yrs' },
                          { title: 'Churn', value: '18%' },
                        ].map((item) => (
                          <div key={item.title} className="rounded-2xl border border-[#E7E5E4] bg-white p-3">
                            <p className="text-[10px] uppercase tracking-[0.12em] text-[#78716C]">{item.title}</p>
                            <p className="mt-3 font-display text-2xl text-[#1C1917]">{item.value}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                      <p className="text-[10px] uppercase tracking-[0.14em] text-[#78716C]">Distribution</p>
                      <div className="mt-4 flex h-28 items-end gap-2">
                        {[16, 22, 18, 38, 44, 54, 68, 56, 44, 30].map((value, index) => (
                          <div key={index} className="flex-1 rounded-t-xl bg-gradient-to-t from-[#D6D3D1] via-[#E9BBA1] to-[#E05A2B]" style={{ height: `${value}%` }} />
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                      <p className="text-[10px] uppercase tracking-[0.14em] text-[#78716C]">Quality overview</p>
                      <div className="mt-4 space-y-4">
                        {[
                          { label: 'Validity', value: '92%' },
                          { label: 'Completeness', value: '86%' },
                          { label: 'Consistency', value: '94%' },
                        ].map((item) => (
                          <div key={item.label}>
                            <div className="flex items-center justify-between text-sm text-[#1C1917]">
                              <span>{item.label}</span>
                              <span className="font-medium text-[#78716C]">{item.value}</span>
                            </div>
                            <div className="mt-2 h-2 overflow-hidden rounded-full bg-[#F3E9E2]">
                              <div className="h-full rounded-full bg-[#E05A2B]" style={{ width: item.value }} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-[1.25rem] border border-[#E7E5E4] bg-[#FAF7F2] p-4">
                      <p className="text-[10px] uppercase tracking-[0.14em] text-[#78716C]">Transformation history</p>
                      <div className="mt-4 space-y-3">
                        {['Type conversion', 'Missing value cleanup', 'Schema validation'].map((item) => (
                          <div key={item} className="flex items-center justify-between rounded-2xl border border-[#E7E5E4] bg-white px-3 py-2 text-sm text-[#1C1917]">
                            <span>{item}</span>
                            <span className="rounded-full bg-[#E5F4ED] px-2 py-1 text-[10px] font-medium text-[#0F766E]">Applied</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-4 pb-20 pt-6 sm:px-6 lg:px-8">
          <div className="rounded-[2.2rem] border border-[#E7E5E4] bg-gradient-to-br from-[#F8F2EC] via-[#FFFDFB] to-[#F5F1EA] px-6 py-12 text-center shadow-[0_25px_60px_rgba(28,25,23,0.05)] sm:px-8 lg:px-12">
            <div className="inline-flex items-center rounded-full bg-[#F8E5DD] px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-[#E05A2B]">
              Get Started
            </div>
            <h2 className="mt-6 font-display text-4xl tracking-[-0.03em] text-[#1C1917] sm:text-5xl">
              Ready to Make Your Data ML-Ready?
            </h2>
            <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-[#78716C]">
              Start exploring your datasets, improve data quality, and build a more reliable foundation for machine learning.
            </p>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 rounded-full bg-[#E05A2B] px-6 py-3 text-base font-semibold text-white transition-transform duration-200 hover:-translate-y-0.5 hover:bg-[#d6522a]"
              >
                Start Preparing Data
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center justify-center rounded-full border border-[#D6D3D1] bg-white px-6 py-3 text-base font-semibold text-[#1C1917] transition-all duration-200 hover:border-[#E05A2B] hover:text-[#E05A2B]"
              >
                Explore Documentation
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-[#E7E5E4] bg-[#FAF7F2]">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-md">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#E05A2B] text-white">
                  <Database className="h-5 w-5" />
                </div>
                <span className="font-display text-2xl text-[#1C1917]">DataForge</span>
              </div>
              <p className="mt-4 text-sm leading-6 text-[#78716C]">
                Intelligent data preparation and ML readiness, in one unified platform.
              </p>
            </div>

            <div className="flex flex-col gap-6 sm:flex-row sm:gap-12">
              <div className="space-y-3 text-sm text-[#78716C]">
                <a href="#features" className="block transition-colors hover:text-[#1C1917]">Features</a>
                <a href="#platform" className="block transition-colors hover:text-[#1C1917]">Platform</a>
                <a href="#docs" className="block transition-colors hover:text-[#1C1917]">Documentation</a>
                <a href="#contact" className="block transition-colors hover:text-[#1C1917]">Contact</a>
              </div>

              <div className="space-y-3 text-sm text-[#78716C]">
                <a href="https://www.linkedin.com" target="_blank" rel="noreferrer" className="block transition-colors hover:text-[#1C1917]">LinkedIn</a>
                <a href="https://www.x.com" target="_blank" rel="noreferrer" className="block transition-colors hover:text-[#1C1917]">X</a>
                <a href="https://www.github.com" target="_blank" rel="noreferrer" className="block transition-colors hover:text-[#1C1917]">GitHub</a>
              </div>
            </div>
          </div>

          <div className="mt-8 border-t border-[#E7E5E4] pt-6 text-sm text-[#78716C]">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p>© 2026 DataForge. All rights reserved.</p>
              <div className="flex items-center gap-5">
                <a href="#privacy" className="transition-colors hover:text-[#1C1917]">Privacy</a>
                <a href="#terms" className="transition-colors hover:text-[#1C1917]">Terms</a>
                <a href="#contact" className="transition-colors hover:text-[#1C1917]">Contact</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
