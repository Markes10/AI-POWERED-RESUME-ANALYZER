import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { act } from "@testing-library/react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider, useAuth } from "@/context/AuthContext";

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

// Test component that uses useAuth
const TestAuthComponent = () => {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth();
  return (
    <div>
      <div data-testid="loading">{isLoading ? "loading" : "loaded"}</div>
      <div data-testid="authenticated">{isAuthenticated ? "yes" : "no"}</div>
      <div data-testid="user">{user?.username || "none"}</div>
      <button onClick={() => login("test", "pass")} data-testid="login-btn">Login</button>
      <button onClick={logout} data-testid="logout-btn">Logout</button>
    </div>
  );
};

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    (global.fetch as any).mockReset();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("initializes with no user when no token in localStorage", () => {
    render(<TestAuthComponent />, { wrapper: createWrapper() });
    
    expect(screen.getByTestId("loading")).toHaveTextContent("loaded");
    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
    expect(screen.getByTestId("user")).toHaveTextContent("none");
  });

  it("loads user from localStorage on init", () => {
    localStorageMock.getItem
      .mockReturnValueOnce("fake-token")
      .mockReturnValueOnce(JSON.stringify({ id: 1, username: "testuser", email: "test@test.com", role: "employee" }));

    render(<TestAuthComponent />, { wrapper: createWrapper() });
    
    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");
    expect(screen.getByTestId("user")).toHaveTextContent("testuser");
  });

  it("logs in successfully", async () => {
    const user = userEvent.setup();
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: "new-token",
        user_id: 1,
        username: "testuser",
        role: "employee",
      }),
    });

    render(<TestAuthComponent />, { wrapper: createWrapper() });
    
    await user.click(screen.getByTestId("login-btn"));
    
    await waitFor(() => {
      expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");
    });
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith("authToken", "new-token");
    expect(localStorageMock.setItem).toHaveBeenCalledWith("authUser", expect.stringContaining("testuser"));
  });

  it("logs out and clears localStorage", async () => {
    const user = userEvent.setup();
    
    // First login
    localStorageMock.getItem
      .mockReturnValueOnce("fake-token")
      .mockReturnValueOnce(JSON.stringify({ id: 1, username: "testuser", email: "test@test.com", role: "employee" }));

    render(<TestAuthComponent />, { wrapper: createWrapper() });
    
    expect(screen.getByTestId("authenticated")).toHaveTextContent("yes");
    
    // Then logout
    await user.click(screen.getByTestId("logout-btn"));
    
    expect(localStorageMock.removeItem).toHaveBeenCalledWith("authToken");
    expect(localStorageMock.removeItem).toHaveBeenCalledWith("authUser");
    expect(screen.getByTestId("authenticated")).toHaveTextContent("no");
  });
});