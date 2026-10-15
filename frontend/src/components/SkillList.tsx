import { useState, useEffect } from "react";
import { api, Skill, SkillListResponse } from "../api/client";

interface SkillListProps {
  onSelect?: (skill: Skill) => void;
}

export function SkillList({ onSelect }: SkillListProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [platform, setPlatform] = useState("");
  const [capability, setCapability] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [platforms, setPlatforms] = useState<string[]>([]);
  const [capabilities, setCapabilities] = useState<string[]>([]);

  useEffect(() => {
    loadMeta();
  }, []);

  useEffect(() => {
    loadSkills();
  }, [page, pageSize, search, category, platform, capability]);

  async function loadMeta() {
    try {
      const [cats, plats, caps] = await Promise.all([
        api.getCategories(),
        api.getPlatforms(),
        api.getCapabilities(),
      ]);
      setCategories(cats);
      setPlatforms(plats);
      setCapabilities(caps);
    } catch (e) {
      console.error("Failed to load metadata", e);
    }
  }

  async function loadSkills() {
    setLoading(true);
    setError(null);
    try {
      const data: SkillListResponse = await api.getSkills({
        page,
        page_size: pageSize,
        search: search || undefined,
        category: category || undefined,
        platform: platform || undefined,
        capability: capability || undefined,
      });
      setSkills(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load skills");
    } finally {
      setLoading(false);
    }
  }

  function handleSearchChange(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setPage(1);
  }

  function handlePageChange(newPage: number) {
    setPage(newPage);
  }

  if (loading && skills.length === 0) {
    return <div className="skill-list-loading">Loading skills...</div>;
  }

  if (error) {
    return (
      <div className="skill-list-error">
        <p>Error: {error}</p>
        <button onClick={loadSkills}>Retry</button>
      </div>
    );
  }

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="skill-list">
      <form onSubmit={handleSearchChange} className="skill-list-filters">
        <input
          type="search"
          placeholder="Search skills..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="skill-search"
        />
        <select aria-label="Category" value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select aria-label="Platform" value={platform} onChange={(e) => { setPlatform(e.target.value); setPage(1); }}>
          <option value="">All Platforms</option>
          {platforms.map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <select aria-label="Capability" value={capability} onChange={(e) => { setCapability(e.target.value); setPage(1); }}>
          <option value="">All Capabilities</option>
          {capabilities.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </form>

      {skills.length === 0 ? (
        <div className="skill-list-empty">No skills found</div>
      ) : (
        <ul className="skill-list-items">
          {skills.map((skill) => (
            <li key={skill.id} className="skill-item" onClick={() => onSelect?.(skill)}>
              <div className="skill-item-header">
                <h3 className="skill-name">{skill.name}</h3>
                <span className="skill-platform">{skill.platform}</span>
              </div>
              <p className="skill-description">{skill.description}</p>
              <div className="skill-meta">
                <span className="skill-category">{skill.category}</span>
                {skill.capability && <span className="skill-capability">{skill.capability}</span>}
                <span className="skill-version">v{skill.version}</span>
              </div>
              {skill.tags.length > 0 && (
                <div className="skill-tags">
                  {skill.tags.map((tag) => <span key={tag} className="skill-tag">{tag}</span>)}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {totalPages > 1 && (
        <nav className="skill-pagination" aria-label="Pagination">
          <button
            onClick={() => handlePageChange(page - 1)}
            disabled={page <= 1}
            aria-label="Previous page"
          >
            Previous
          </button>
          <span className="page-info">
            Page {page} of {totalPages} ({total} total)
          </span>
          <button
            onClick={() => handlePageChange(page + 1)}
            disabled={page >= totalPages}
            aria-label="Next page"
          >
            Next
          </button>
        </nav>
      )}
    </div>
  );
}