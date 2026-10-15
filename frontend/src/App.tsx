import { useState } from "react";
import { SkillList } from "./components/SkillList";
import { Skill } from "./api/client";
import "./App.css";

function App() {
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Axiom Foundry</h1>
        <p className="subtitle">Agent Harness Performance Optimization</p>
      </header>
      <main className="app-main">
        <section className="skill-registry">
          <h2>Skill Registry</h2>
          <SkillList onSelect={setSelectedSkill} />
        </section>
        {selectedSkill && (
          <aside className="skill-detail">
            <h3>{selectedSkill.name}</h3>
            <p>{selectedSkill.description}</p>
            <dl>
              <dt>Category</dt>
              <dd>{selectedSkill.category}</dd>
              <dt>Platform</dt>
              <dd>{selectedSkill.platform}</dd>
              {selectedSkill.capability && (
                <>
                  <dt>Capability</dt>
                  <dd>{selectedSkill.capability}</dd>
                </>
              )}
              <dt>Version</dt>
              <dd>{selectedSkill.version}</dd>
              {selectedSkill.author && (
                <>
                  <dt>Author</dt>
                  <dd>{selectedSkill.author}</dd>
                </>
              )}
              <dt>Tags</dt>
              <dd>{selectedSkill.tags.join(", ") || "—"}</dd>
            </dl>
            <button onClick={() => setSelectedSkill(null)}>Close</button>
          </aside>
        )}
      </main>
    </div>
  );
}

export default App;