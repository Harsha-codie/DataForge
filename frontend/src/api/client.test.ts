import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiRequest, buildJobsEndpoint, buildVisualizationMetadataEndpoint } from './client';

describe('jobs API requests', () => {
  it('encodes dataset_id and limit as independent parameters', () => {
    expect(buildJobsEndpoint('dataset/with spaces', 5)).toBe(
      '/jobs/?dataset_id=dataset%2Fwith+spaces&limit=5'
    );
  });

  it('omits undefined job filters', () => {
    expect(buildJobsEndpoint(undefined, 5)).toBe('/jobs/?limit=5');
    expect(buildJobsEndpoint()).toBe('/jobs/');
    expect(buildJobsEndpoint('', 5)).toBe('/jobs/?limit=5');
  });
});

describe('apiRequest authentication', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('attaches the stored token as a bearer header', async () => {
    vi.stubGlobal('localStorage', { getItem: vi.fn(() => 'test-token') });
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );
    vi.stubGlobal('fetch', fetchMock);

    await apiRequest('/jobs/?limit=5');

    expect(fetchMock).toHaveBeenCalledWith('https://dataforge-a1fh.onrender.com/api/v1/jobs/?limit=5', {
      headers: {
        Authorization: 'Bearer test-token',
        'Content-Type': 'application/json',
      },
    });
  });
});

describe('visualization API routes', () => {
  it('builds a version-aware metadata endpoint', () => {
    expect(buildVisualizationMetadataEndpoint('dataset/1', 'version 2')).toBe(
      '/datasets/dataset%2F1/visualizations/metadata?version_id=version+2'
    );
  });
});
