import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ExceptionDetail from '../app/exceptions/[id]/page';
import { api } from '../lib/api';

jest.mock('../lib/api', () => ({
  api: {
    getExceptionDetail: jest.fn(),
  },
}));

jest.mock('next/navigation', () => ({
  useParams: () => ({ id: 'exc-123' }),
  useRouter: () => ({ push: jest.fn() }),
}));

describe('Exception Detail Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('displays correct variance and labels', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { amount_difference: 1372 },
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText('EXCEPTION exc-123')).toBeInTheDocument();
    });

    // Label should be Variance
    expect(screen.getByText('Variance')).toBeInTheDocument();
    
    // Real variance displays correctly
    expect(screen.getByText(/1,372/)).toBeInTheDocument();
    
    // No hardcoded 50000
    expect(screen.queryByText(/50,000/)).not.toBeInTheDocument();
  });

  it('displays "—" when variance is missing', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: {}, // no difference
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText('EXCEPTION exc-123')).toBeInTheDocument();
    });

    // The header variance should be "—"
    const varianceContainers = screen.getAllByText('—');
    expect(varianceContainers.length).toBeGreaterThan(0);
  });

  it('preserves zero variance', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { difference: 0 },
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText('EXCEPTION exc-123')).toBeInTheDocument();
    });

    // Zero variance remains 0
    expect(screen.getAllByText(/0/)).toBeDefined();
  });

  it('does not show fabricated financial chain amounts', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { }, // no expected or actual
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText('EXCEPTION exc-123')).toBeInTheDocument();
    });

    expect(screen.queryByText(/50,000/)).not.toBeInTheDocument();
    expect(screen.queryByText(/48,500/)).not.toBeInTheDocument();
    // Chain amounts are unavailable, meaning they should render "—"
    const dashes = screen.getAllByText('—');
    expect(dashes.length).toBeGreaterThanOrEqual(4); // 4 nodes with no amounts
    
    const unavailables = screen.getAllByText('Unavailable');
    expect(unavailables.length).toBeGreaterThanOrEqual(4); // 4 nodes with no IDs
  });

  it('shows actual financial chain amounts if provided', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { expected: 1000, actual: 900 },
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText('EXCEPTION exc-123')).toBeInTheDocument();
    });

    // PAYMENT has expected amount
    expect(screen.getByText(/1,000/)).toBeInTheDocument();
    // SETTLEMENT has actual amount
    expect(screen.getByText(/900/)).toBeInTheDocument();
  });

  it('renders AI explanation correctly based on backend evidence', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { explanation: 'This is a test backend explanation.' },
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText(/This is a test backend explanation./)).toBeInTheDocument();
    });

    expect(screen.queryByText(/1,500/)).not.toBeInTheDocument();
  });

  it('renders honest unavailable state for AI explanation if missing', async () => {
    (api.getExceptionDetail as jest.Mock).mockResolvedValue({
      id: 'exc-123',
      decision: 'REVIEW',
      exception_type: 'PARTIAL_SETTLEMENT',
      confidence: 0.85,
      variance_details: { }, // no explanation
      evidence: [],
    });

    render(<ExceptionDetail />);

    await waitFor(() => {
      expect(screen.getByText(/No additional explanation provided by the AI Engine./)).toBeInTheDocument();
    });
  });
});
