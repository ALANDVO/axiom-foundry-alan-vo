import { describe, it, expect, vi, beforeEach, type Mock } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { SkillList } from "../components/SkillList";

// Mock the API module
vi.mock("../api/client", () => {
  const mockApi = {
    getSkills: vi.fn(),
    getCategories: vi.fn(),
    getPlatforms: vi.fn(),
    getCapabilities: vi.fn(),
    getSupportedPlatformConfigs: vi.fn(),
    getSkillPlatformConfig: vi.fn(),
    getSkillPlatformConfigByName: vi.fn(),
  };
  return { api: mockApi };
});

// Import the mocked api
import { api } from "../api/client";

const mockSkills = [
  {
    id: 1,
    name: "tdd-workflow",
    description: "Test-driven development workflow",
    category: "workflow",
    platform: "claude",
    capability: "tdd",
    tags: ["testing", "workflow"],
    config: {},
    version: "1.0.0",
    author: "ECC",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "security-review",
    description: "Security code review skill",
    category: "security",
    platform: "claude",
    capability: "security",
    tags: ["security", "review"],
    config: {},
    version: "1.0.0",
    author: "ECC",
    created_at: "2024-01-02T00:00:00Z",
    updated_at: "2024-01-02T00:00:00Z",
  },
];

describe("SkillList", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders loading state initially", () => {
    const { promise } = Promise.withResolvers<void>();
    api.getSkills.mockReturnValue(promise);
    api.getCategories.mockReturnValue(promise);
    api.getPlatforms.mockReturnValue(promise);
    api.getCapabilities.mockReturnValue(promise);
    api.getSupportedPlatformConfigs.mockReturnValue(promise);

    render(<SkillList />);
    expect(screen.getByText("Loading skills...")).toBeInTheDocument();
  });

  it("renders skill list after loading", async () => {
    api.getSkills.mockResolvedValue({
      items: mockSkills,
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    });
    api.getCategories.mockResolvedValue(["workflow", "security"]);
    api.getPlatforms.mockResolvedValue(["claude"]);
    api.getCapabilities.mockResolvedValue(["tdd", "security"]);
    api.getSupportedPlatformConfigs.mockResolvedValue(["claude", "cursor"]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("tdd-workflow")).toBeInTheDocument();
      expect(screen.getByText("security-review")).toBeInTheDocument();
    });
  });

  it("shows empty state when no skills", async () => {
    api.getSkills.mockResolvedValue({ items: [], total: 0, page: 1, page_size: 20, total_pages: 1 });
    api.getCategories.mockResolvedValue([]);
    api.getPlatforms.mockResolvedValue([]);
    api.getCapabilities.mockResolvedValue([]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("No skills found")).toBeInTheDocument();
    });
  });

  it("filters by search term", async () => {
    api.getSkills.mockResolvedValue({
      items: [mockSkills[0]],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    });
    api.getCategories.mockResolvedValue(["workflow"]);
    api.getPlatforms.mockResolvedValue(["claude"]);
    api.getCapabilities.mockResolvedValue(["tdd"]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("tdd-workflow")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText("Search skills...");
    fireEvent.change(searchInput, { target: { value: "security" } });
    fireEvent.submit(searchInput.closest("form")!);

    await waitFor(() => {
      expect(api.getSkills).toHaveBeenCalledWith(
        expect.objectContaining({ search: "security" })
      );
    });
  });

  it("filters by category", async () => {
    api.getSkills.mockResolvedValue({
      items: [mockSkills[1]],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    });
    api.getCategories.mockResolvedValue(["workflow", "security"]);
    api.getPlatforms.mockResolvedValue(["claude"]);
    api.getCapabilities.mockResolvedValue(["tdd", "security"]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("security-review")).toBeInTheDocument();
    });

    const categorySelect = screen.getByRole("combobox", { name: /category/i });
    fireEvent.change(categorySelect, { target: { value: "security" } });

    await waitFor(() => {
      expect(api.getSkills).toHaveBeenCalledWith(
        expect.objectContaining({ category: "security" })
      );
    });
  });

  it("calls onSelect when skill clicked", async () => {
    const onSelect = vi.fn();
    api.getSkills.mockResolvedValue({
      items: mockSkills,
      total: 2,
      page: 1,
      page_size: 20,
      total_pages: 1,
    });
    api.getCategories.mockResolvedValue(["workflow", "security"]);
    api.getPlatforms.mockResolvedValue(["claude"]);
    api.getCapabilities.mockResolvedValue(["tdd", "security"]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList onSelect={onSelect} />);

    await waitFor(() => {
      expect(screen.getByText("tdd-workflow")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("tdd-workflow"));

    expect(onSelect).toHaveBeenCalledWith(mockSkills[0]);
  });

  it("shows pagination when multiple pages", async () => {
    api.getSkills.mockResolvedValue({
      items: mockSkills,
      total: 50,
      page: 1,
      page_size: 20,
      total_pages: 3,
    });
    api.getCategories.mockResolvedValue(["workflow", "security"]);
    api.getPlatforms.mockResolvedValue(["claude"]);
    api.getCapabilities.mockResolvedValue(["tdd", "security"]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("Page 1 of 3 (50 total)")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /next page/i })).toBeInTheDocument();
    });
  });

  it("displays error state on API failure", async () => {
    api.getSkills.mockRejectedValue(new Error("Network error"));
    api.getCategories.mockResolvedValue([]);
    api.getPlatforms.mockResolvedValue([]);
    api.getCapabilities.mockResolvedValue([]);
    api.getSupportedPlatformConfigs.mockResolvedValue([]);

    render(<SkillList />);

    await waitFor(() => {
      expect(screen.getByText("Error: Network error")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    });
  });
});
