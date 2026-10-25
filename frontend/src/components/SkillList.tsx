import { useState, useEffect } from "react";
import { api, Skill, SkillListResponse, PlatformConfig } from "../api/client";

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

  // Platform config modal state
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [configModalSkill, setConfigModalSkill] = useState<Skill | null>(null);
  const [configModalPlatform, setConfigModalPlatform] = useState("");
  const [platformConfig, setPlatformConfig] = useState<PlatformConfig | null>(null);
  const [configLoading, setConfigLoading] = useState(false);
  const [configError, setConfigError] = useState<string | null>(null);

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

  async function handleGenerateConfig(skill: Skill, targetPlatform: string) {
    setConfigModalSkill(skill);
    setConfigModalPlatform(targetPlatform);
    setPlatformConfig(null);
    setConfigError(null);
    setConfigLoading(true);
    setShowConfigModal(true);

    try {
      const config = await api.getSkillPlatformConfig(skill.id, targetPlatform);
      setPlatformConfig(config);
    } catch (e) {
      setConfigError(e instanceof Error ? e.message : "Failed to generate config");
    } finally {
      setConfigLoading(false);
    }
  }

  function closeConfigModal() {
    setShowConfigModal(false);
    setConfigModalSkill(null);
    setConfigModalPlatform("");
    setPlatformConfig(null);
    setConfigError(null);
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
              <div className="skill-actions">
                <button
                  className="generate-config-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleGenerateConfig(skill, skill.platform);
                  }}
                  disabled={configLoading}
                >
                  Generate Config
                </button>
              </div>
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

      {showConfigModal && configModalSkill && (
        <div className="config-modal-overlay" onClick={closeConfigModal}>
          <div className="config-modal" onClick={(e) => e.stopPropagation()}>
            <div className="config-modal-header">
              <h3>Platform Configuration</h3>
              <p className="config-modal-skill">{configModalSkill.name} → {configModalPlatform}</p>
              <button className="config-modal-close" onClick={closeConfigModal} aria-label="Close">
                ×
              </button>
            </div>
            {configLoading && <div className="config-modal-loading">Generating configuration...</div>}
            {configError && (
              <div className="config-modal-error">
                <p>Error: {configError}</p>
                <button onClick={() => handleGenerateConfig(configModalSkill!, configModalPlatform)}>Retry</button>
              </div>
            )}
            {platformConfig && !configLoading && !configError && (
              <div className="config-modal-content">
                <pre className="config-json">{JSON.stringify(platformConfig, null, 2)}</pre>
                <div className="config-modal-actions">
                  <button
                    className="copy-config-btn"
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(platformConfig, null, 2));
                      alert("Configuration copied to clipboard!");
                    }}
                  >
                    Copy to Clipboard
                  </button>
                  <button
                    className="download-config-btn"
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(platformConfig, null, 2)], { type: "application/json" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `${configModalSkill.name}-${configModalPlatform}.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    Download JSON
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
