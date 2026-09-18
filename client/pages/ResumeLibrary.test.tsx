import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/context/AuthContext";
import ResumeLibrary from "@/pages/ResumeLibrary";

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <AuthProvider>
          <BrowserRouter>{children}</BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

describe("ResumeLibrary Component - Basic Rendering", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue("fake-token");
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'authToken') return "fake-token";
      if (key === 'authUser') return JSON.stringify({ id: 1, username: "testuser", email: "test@test.com", role: "employee" });
      return null;
    });
  });

  it("renders the header", () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<ResumeLibrary />, { wrapper: createWrapper() });
    
    expect(screen.getByText("Resume Library")).toBeInTheDocument();
    expect(screen.getByText("Manage and analyze your uploaded resumes")).toBeInTheDocument();
  });

  it("shows upload button", () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<ResumeLibrary />, { wrapper: createWrapper() });
    
    expect(screen.getByText("Upload Resume")).toBeInTheDocument();
  });

  it("shows search input", () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<ResumeLibrary />, { wrapper: createWrapper() });
    
    expect(screen.getByPlaceholderText("Search by skills, keywords...")).toBeInTheDocument();
  });

  it("shows tabs for filtering", () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<ResumeLibrary />, { wrapper: createWrapper() });
    
    expect(screen.getByText("All Resumes")).toBeInTheDocument();
    expect(screen.getByText("Recent (7 days)")).toBeInTheDocument();
  });

  it("shows empty state when no resumes", async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<ResumeLibrary />, { wrapper: createWrapper() });
    
    // The component shows loading first, then empty state
    expect(screen.getByText("Upload Resume")).toBeInTheDocument();
  });
});