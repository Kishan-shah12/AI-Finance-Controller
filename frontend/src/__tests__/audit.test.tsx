import "@testing-library/jest-dom";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import AuditTrailPage from "../app/audit/page";
import { api } from "../lib/api";

jest.mock("../lib/api", () => ({
  api: {
    getAuditEvents: jest.fn(),
  },
}));

describe("Audit Trail Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders real audit events from API", async () => {
    (api.getAuditEvents as jest.Mock).mockResolvedValue([
      {
        id: "evt-uuid-001",
        run_id: "run-999",
        action: "RECORDS_PROCESSED",
        entity_type: "Batch",
        entity_id: "run-999",
        actor: "System",
        metadata_json: { records: 1000 },
        created_at: "2026-08-29T10:00:00Z"
      },
      {
        id: "evt-uuid-002",
        run_id: "run-999",
        action: "MATCH_DECISION",
        entity_type: "Transaction",
        entity_id: "tx-555",
        actor: "Finance Controller",
        metadata_json: { decision: "VERIFIED_MATCH" },
        created_at: "2026-08-29T10:05:00Z"
      }
    ]);

    render(<AuditTrailPage />);

    await waitFor(() => {
      expect(screen.getAllByText("RECORDS PROCESSED").length).toBeGreaterThan(0);
      expect(screen.getAllByText("MATCH DECISION").length).toBeGreaterThan(0);
    });

    expect(screen.getByText(/System/)).toBeInTheDocument();
    expect(screen.getByText(/Finance Controller/)).toBeInTheDocument();
  });

  it("handles empty audit events state", async () => {
    (api.getAuditEvents as jest.Mock).mockResolvedValue([]);

    render(<AuditTrailPage />);

    await waitFor(() => {
      expect(screen.getByText("No audit events yet.")).toBeInTheDocument();
    });
  });

  it("filters audit events by search query", async () => {
    (api.getAuditEvents as jest.Mock).mockResolvedValue([
      {
        id: "evt-uuid-001",
        run_id: "run-999",
        action: "RECORDS_PROCESSED",
        entity_type: "Batch",
        entity_id: "run-999",
        actor: "System",
        metadata_json: { records: 1000 },
        created_at: "2026-08-29T10:00:00Z"
      },
      {
        id: "evt-uuid-002",
        run_id: "run-999",
        action: "MATCH_DECISION",
        entity_type: "Transaction",
        entity_id: "tx-555",
        actor: "Finance Controller",
        metadata_json: { decision: "VERIFIED_MATCH" },
        created_at: "2026-08-29T10:05:00Z"
      }
    ]);

    render(<AuditTrailPage />);

    await waitFor(() => {
      expect(screen.getAllByText("RECORDS PROCESSED").length).toBeGreaterThan(0);
    });

    const searchInput = screen.getByPlaceholderText("Search event, actor, or entity...");
    fireEvent.change(searchInput, { target: { value: "Finance Controller" } });

    expect(screen.getAllByText("MATCH DECISION").length).toBeGreaterThan(0);
    expect(screen.queryByText("System")).not.toBeInTheDocument();
  });
});
