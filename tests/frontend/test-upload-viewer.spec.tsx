import { render, screen, fireEvent } from "@testing-library/react";
import UploadViewer from "@/components/UploadViewer";

describe("UploadViewer", () => {
  it("renders upload button and handles file input", () => {
    render(<UploadViewer />);
    const uploadBtn = screen.getByText(/Upload Resume/i);
    expect(uploadBtn).toBeInTheDocument();

    const input = screen.getByLabelText(/Choose file/i);
    expect(input).toBeInTheDocument();

    fireEvent.change(input, {
      target: { files: [new File(["dummy"], "resume.pdf", { type: "application/pdf" })] },
    });

    expect(screen.getByText(/resume.pdf/i)).toBeInTheDocument();
  });
});