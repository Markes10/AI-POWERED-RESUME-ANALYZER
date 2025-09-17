import { render, screen, fireEvent } from "@testing-library/react";
import FeedbackForm from "@/components/FeedbackForm";

describe("FeedbackForm", () => {
  it("submits feedback with rating and comment", () => {
    render(<FeedbackForm analysisId={42} />);
    const ratingInput = screen.getByLabelText(/Rating/i);
    const commentInput = screen.getByPlaceholderText(/Your comments/i);
    const submitBtn = screen.getByText(/Submit Feedback/i);

    fireEvent.change(ratingInput, { target: { value: "5" } });
    fireEvent.change(commentInput, { target: { value: "Great match!" } });
    fireEvent.click(submitBtn);

    expect(screen.getByText(/Thank you for your feedback/i)).toBeInTheDocument();
  });
}); 
