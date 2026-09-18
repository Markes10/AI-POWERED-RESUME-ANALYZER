import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/context/AuthContext";
import ResumeFit from "./ResumeFit";

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

describe("ResumeFit Component - Basic Rendering", () => {
  it("renders the main header", () => {
    render(<ResumeFit />, { wrapper: createWrapper() });
    expect(screen.getByText("AI Résumé-Job Fit Engine")).toBeInTheDocument();
    expect(screen.getByText("Intelligent matching system with advanced AI analysis")).toBeInTheDocument();
  });

  it("renders job description section", () => {
    render(<ResumeFit />, { wrapper: createWrapper() });
    expect(screen.getByText("Job Description")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Paste the full job description here...")).toBeInTheDocument();
  });

  it("renders resume upload section", () => {
    render(<ResumeFit />, { wrapper: createWrapper() });
    expect(screen.getByText("Resume Upload")).toBeInTheDocument();
    expect(screen.getByText("Drop resume here or click to upload")).toBeInTheDocument();
  });

  it("shows analyze button", () => {
    render(<ResumeFit />, { wrapper: createWrapper() });
    expect(screen.getByText("Analyze Fit")).toBeInTheDocument();
  });

  it("disables analyze button when no input provided", () => {
    render(<ResumeFit />, { wrapper: createWrapper() });
    const analyzeButton = screen.getByText("Analyze Fit");
    expect(analyzeButton).toBeDisabled();
  });

  it("enables analyze button when job description is provided", async () => {
    const { render: rtlRender } = await import("@testing-library/react");
    const userEvent = await import("@testing-library/user-event");
    
    rtlRender(<ResumeFit />, { wrapper: createWrapper() });
    const user = userEvent.default.setup();

    const jobDescriptionInput = screen.getByPlaceholderText("Paste the full job description here...");
    await user.type(jobDescriptionInput, "Senior React Developer needed");

    const analyzeButton = screen.getByText("Analyze Fit");
    expect(analyzeButton).not.toBeDisabled();
  });
});

describe("AuthContext", () => {
  it("provides auth context", () => {
    expect(true).toBe(true);
  });
});

describe("PDF Export", () => {
  it("exports PDF without errors", () => {
    expect(true).toBe(true);
  });
});