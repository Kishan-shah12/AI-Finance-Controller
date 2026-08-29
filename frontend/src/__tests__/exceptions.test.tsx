import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ExceptionsPage from '../app/exceptions/page';
import { api } from '../lib/api';

// Mock the API module
jest.mock('../lib/api', () => ({
  api: {
    getExceptions: jest.fn(),
  },
}));

const mockExceptions = [
  {
    id: 'exc-123',
    decision: 'REVIEW',
    exception_type: 'PARTIAL_SETTLEMENT',
    confidence: 0.85,
    evidence: [],
    variance_details: { amount_difference: 500 },
  },
  {
    id: 'exc-456',
    decision: 'UNRESOLVED',
    exception_type: 'MISSING_BANK_ENTRY',
    confidence: 0.60,
    evidence: [],
    variance_details: {}, // Missing variance amount
  },
  {
    id: 'exc-789',
    decision: 'ESCALATED',
    exception_type: 'FEE_VARIANCE',
    confidence: 0.45,
    evidence: [],
    variance_details: { amount_difference: 0 }, // Zero variance
  },
];

describe('Exceptions Page', () => {
  beforeEach(() => {
    (api.getExceptions as jest.Mock).mockResolvedValue(mockExceptions);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders exceptions and correctly displays variance amounts', async () => {
    render(<ExceptionsPage />);
    
    // Wait for the exceptions to load
    await waitFor(() => {
      expect(screen.getByText('exc-123')).toBeInTheDocument();
    });

    // Real variance displays real value
    expect(screen.getByText(/500/)).toBeInTheDocument();
    
    // Missing variance displays "—"
    expect(screen.getByText('—')).toBeInTheDocument();

    // Zero variance remains zero
    // Since currency formatting will format it as "₹0.00" or similar depending on Intl
    const tableCells = screen.getAllByRole('cell');
    const zeroCell = tableCells.find(cell => cell.textContent?.includes('0'));
    expect(zeroCell).toBeDefined();
  });

  it('filters exceptions by search query (exception ID)', async () => {
    render(<ExceptionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('exc-123')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search ID or reason...');
    fireEvent.change(searchInput, { target: { value: 'exc-123' } });

    expect(screen.getByText('exc-123')).toBeInTheDocument();
    expect(screen.queryByText('exc-456')).not.toBeInTheDocument();
    expect(screen.queryByText('exc-789')).not.toBeInTheDocument();
  });

  it('filters exceptions by search query (exception type)', async () => {
    render(<ExceptionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('exc-123')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search ID or reason...');
    // Type lowercase partial match
    fireEvent.change(searchInput, { target: { value: 'missing' } });

    expect(screen.queryByText('exc-123')).not.toBeInTheDocument();
    expect(screen.getByText('exc-456')).toBeInTheDocument();
    expect(screen.queryByText('exc-789')).not.toBeInTheDocument();
  });

  it('filters exceptions by decision', async () => {
    render(<ExceptionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('exc-123')).toBeInTheDocument();
    });

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'UNRESOLVED' } });

    expect(screen.queryByText('exc-123')).not.toBeInTheDocument();
    expect(screen.getByText('exc-456')).toBeInTheDocument();
    expect(screen.queryByText('exc-789')).not.toBeInTheDocument();
  });

  it('displays no-match state when filter yields no results', async () => {
    render(<ExceptionsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('exc-123')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search ID or reason...');
    fireEvent.change(searchInput, { target: { value: 'nonexistent-id-1234' } });

    expect(screen.getByText('No matching exceptions.')).toBeInTheDocument();
    expect(screen.queryByText('exc-123')).not.toBeInTheDocument();
  });
});
