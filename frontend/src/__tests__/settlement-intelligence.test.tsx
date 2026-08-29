import "@testing-library/jest-dom";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import SettlementIntelligence from "../app/intelligence/settlement/page";
import { api } from "../lib/api";

const mockPush = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

jest.mock("../lib/api", () => ({
  api: {
    getLatestDemoRun: jest.fn(),
    getExceptions: jest.fn(),
    getHighestPriorityExceptionId: jest.fn(),
    getExceptionDetail: jest.fn(),
  },
}));

describe("Settlement Intelligence Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders live decision matrix and waterfall metrics truthfully", async () => {
    (api.getLatestDemoRun as jest.Mock).mockResolvedValue({
      run_id: "demo-run-uuid-12345",
      scenario_count: 1000,
      records_processed: 1000,
      verified_match: 920,
      explainable_variance: 50,
      review: 20,
      unresolved: 10,
    });
    (api.getExceptions as jest.Mock).mockResolvedValue([
      {
        id: "exc-uuid-999",
        decision: "UNRESOLVED",
        exception_type: "MISSING_SETTLEMENT",
        confidence: 0.15,
        variance_details: { amount_difference: 4848 }
      }
    ]);
    (api.getHighestPriorityExceptionId as jest.Mock).mockResolvedValue("exc-uuid-999");
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: "exc-uuid-999",
      decision: "UNRESOLVED",
      exception_type: "MISSING_SETTLEMENT",
      confidence: 0.15,
      variance_details: { amount_difference: 4848 }
    });

    render(<SettlementIntelligence />);

    await waitFor(() => {
      expect(screen.getByText("Decision Matrix Breakdown")).toBeInTheDocument();
    });

    // Check dynamic numbers
    expect(screen.getAllByText("1,000").length).toBeGreaterThan(0);
    expect(screen.getByText("920")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();

    // Check AI Analysis references top exception
    expect(screen.getByText(/exc-uuid-999/)).toBeInTheDocument();
  });

  it("triggers AI controller query flow when an Ask ReconAI question is clicked", async () => {
    (api.getLatestDemoRun as jest.Mock).mockResolvedValue(null);
    (api.getExceptions as jest.Mock).mockResolvedValue([]);

    render(<SettlementIntelligence />);

    await waitFor(() => {
      expect(screen.getByText("Why is today's settlement short?")).toBeInTheDocument();
    });

    const questionButton = screen.getByLabelText("Ask ReconAI: Why is today's settlement short?");
    fireEvent.click(questionButton);

    expect(mockPush).toHaveBeenCalledWith("/agent?q=Why%20is%20today's%20settlement%20short%3F");
  });
});
