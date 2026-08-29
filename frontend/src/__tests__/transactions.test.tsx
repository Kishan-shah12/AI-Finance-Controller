import "@testing-library/jest-dom";
import { render, screen, fireEvent } from "@testing-library/react";
import TransactionsPage from "../app/transactions/page";

describe("Transactions Page Filter & Search", () => {
  it("renders all initial transactions", () => {
    render(<TransactionsPage />);

    expect(screen.getByText("TX-9021")).toBeInTheDocument();
    expect(screen.getByText("TX-9022")).toBeInTheDocument();
    expect(screen.getByText("TX-9023")).toBeInTheDocument();
    expect(screen.getByText("TX-9024")).toBeInTheDocument();
    expect(screen.getByText("TX-9025")).toBeInTheDocument();
  });

  it("filters transactions by search query (transaction ID)", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    fireEvent.change(searchInput, { target: { value: "TX-9025" } });

    expect(screen.getByText("TX-9025")).toBeInTheDocument();
    expect(screen.getByText("ORD-127")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9022")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9023")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9024")).not.toBeInTheDocument();
  });

  it("filters transactions by search query (order ID)", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    fireEvent.change(searchInput, { target: { value: "ORD-127" } });

    expect(screen.getByText("TX-9025")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9022")).not.toBeInTheDocument();
  });

  it("filters transactions by search query (decision name)", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    fireEvent.change(searchInput, { target: { value: "UNRESOLVED" } });

    expect(screen.getByText("TX-9025")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();
  });

  it("filters transactions by decision dropdown (VERIFIED_MATCH)", () => {
    render(<TransactionsPage />);

    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "VERIFIED_MATCH" } });

    expect(screen.getByText("TX-9021")).toBeInTheDocument();
    expect(screen.getByText("TX-9024")).toBeInTheDocument();
    expect(screen.queryByText("TX-9022")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9023")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9025")).not.toBeInTheDocument();
  });

  it("filters transactions by decision dropdown (REVIEW)", () => {
    render(<TransactionsPage />);

    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "REVIEW" } });

    expect(screen.getByText("TX-9023")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9025")).not.toBeInTheDocument();
  });

  it("filters transactions by decision dropdown (UNRESOLVED)", () => {
    render(<TransactionsPage />);

    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "UNRESOLVED" } });

    expect(screen.getByText("TX-9025")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();
    expect(screen.queryByText("TX-9023")).not.toBeInTheDocument();
  });

  it("combines search and decision filter correctly", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    const select = screen.getByRole("combobox");

    // Decision = VERIFIED_MATCH, Search = ORD-126
    fireEvent.change(select, { target: { value: "VERIFIED_MATCH" } });
    fireEvent.change(searchInput, { target: { value: "ORD-126" } });

    expect(screen.getByText("TX-9024")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();

    // Mismatched search with decision -> empty state
    fireEvent.change(searchInput, { target: { value: "ORD-125" } });
    expect(screen.getByText("No matching transactions found.")).toBeInTheDocument();
  });

  it("shows empty state when no transactions match search", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    fireEvent.change(searchInput, { target: { value: "NONEXISTENT-999" } });

    expect(screen.getByText("No matching transactions found.")).toBeInTheDocument();
  });

  it("resets list when filter is set back to ALL and search is cleared", () => {
    render(<TransactionsPage />);

    const searchInput = screen.getByPlaceholderText("Search Order ID, Payment ID, UTR...");
    const select = screen.getByRole("combobox");

    fireEvent.change(select, { target: { value: "UNRESOLVED" } });
    fireEvent.change(searchInput, { target: { value: "TX-9025" } });
    expect(screen.getByText("TX-9025")).toBeInTheDocument();
    expect(screen.queryByText("TX-9021")).not.toBeInTheDocument();

    fireEvent.change(select, { target: { value: "ALL" } });
    fireEvent.change(searchInput, { target: { value: "" } });

    expect(screen.getByText("TX-9021")).toBeInTheDocument();
    expect(screen.getByText("TX-9022")).toBeInTheDocument();
    expect(screen.getByText("TX-9023")).toBeInTheDocument();
    expect(screen.getByText("TX-9024")).toBeInTheDocument();
    expect(screen.getByText("TX-9025")).toBeInTheDocument();
  });

  it("ensures exception_id remains the only navigation identifier and does not generate invalid exception links", () => {
    render(<TransactionsPage />);

    // Since mock transactions have exception_id: null, no link with href /exceptions/TX-... or /exceptions/null should exist
    const links = screen.queryAllByRole("link");
    for (const link of links) {
      const href = link.getAttribute("href");
      expect(href).not.toContain("TX-");
      expect(href).not.toContain("ORD-");
      expect(href).not.toContain("null");
      expect(href).not.toContain("undefined");
    }
  });
});
