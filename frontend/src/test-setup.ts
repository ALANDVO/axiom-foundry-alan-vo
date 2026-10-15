import { vi } from "vitest";
import "@testing-library/jest-dom";

vi.mock("./api/client", () => ({
  api: {
    getSkills: vi.fn(),
    getSkill: vi.fn(),
    createSkill: vi.fn(),
    updateSkill: vi.fn(),
    deleteSkill: vi.fn(),
    getCategories: vi.fn(),
    getPlatforms: vi.fn(),
    getCapabilities: vi.fn(),
  },
}));