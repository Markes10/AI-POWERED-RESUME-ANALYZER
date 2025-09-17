import { render, screen } from "@testing-library/react";
import AnalysisResult from "@/components/AnalysisResult";

const mockData = {
  score: 0.78,
  skills: ["Python", "Docker"],
  missing_keywords: ["API", "CI/CD"],
  suggestions: ["Consider including the keyword 'API' if relevant."]
};

describe("AnalysisResult", () => {
  it("displays score and suggestions", () => {
    render(<AnalysisResult result={mockData} />);
    expect(screen.getByText(/Match Score/i)).toBeInTheDocument();
    expect(screen.getByText(/0.78/)).toBeInTheDocument();
    expect(screen.getByText(/Python/)).toBeInTheDocument();
    expect(screen.getByText(/API/)).toBeInTheDocument();
  });
}); 
