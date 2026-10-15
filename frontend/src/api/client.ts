/// <reference types="vite/client" />
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export interface Skill {
  id: number;
  name: string;
  description: string;
  category: string;
  platform: string;
  capability: string | null;
  tags: string[];
  config: Record<string, unknown>;
  version: string;
  author: string | null;
  created_at: string;
  updated_at: string;
}

export interface SkillListResponse {
  items: Skill[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SkillCreate {
  name: string;
  description: string;
  category: string;
  platform: string;
  capability?: string;
  tags?: string[];
  config?: Record<string, unknown>;
  version?: string;
  author?: string;
}

export interface SkillUpdate {
  description?: string;
  category?: string;
  platform?: string;
  capability?: string;
  tags?: string[];
  config?: Record<string, unknown>;
  version?: string;
  author?: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = {
  getSkills: (params: {
    page?: number;
    page_size?: number;
    search?: string;
    category?: string;
    platform?: string;
    capability?: string;
    sort?: string;
    order?: string;
  } = {}): Promise<SkillListResponse> => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) query.append(key, String(value));
    });
    return request(`/skills?${query.toString()}`);
  },

  getSkill: (id: number): Promise<Skill> => request(`/skills/${id}`),

  getSkillByName: (name: string): Promise<Skill> => request(`/skills/name/${encodeURIComponent(name)}`),

  createSkill: (skill: SkillCreate): Promise<Skill> =>
    request("/skills", { method: "POST", body: JSON.stringify(skill) }),

  updateSkill: (id: number, skill: SkillUpdate): Promise<Skill> =>
    request(`/skills/${id}`, { method: "PATCH", body: JSON.stringify(skill) }),

  deleteSkill: (id: number): Promise<void> => request(`/skills/${id}`, { method: "DELETE" }),

  getCategories: (): Promise<string[]> => request("/skills/meta/categories"),
  getPlatforms: (): Promise<string[]> => request("/skills/meta/platforms"),
  getCapabilities: (): Promise<string[]> => request("/skills/meta/capabilities"),
};