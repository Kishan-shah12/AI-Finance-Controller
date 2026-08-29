import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AgentPage from './page';
import { api } from '@/lib/api';

jest.mock('@/lib/api', () => ({
  api: {
    queryAgent: jest.fn()
  }
}));

jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(),
}));

describe('Agent Page AI Evidence Rendering', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('Render evidence correctly with valid exception_id', async () => {
    (api.queryAgent as jest.Mock).mockResolvedValue({
      status: 'SUCCESS',
      answer: 'Test variance found.',
      confidence: 0.95,
      evidence: [
        { exception_id: '123e4567-e89b-12d3-a456-426614174000', explanation: 'Missing fee' }
      ]
    });

    render(<AgentPage />);
    const input = screen.getByPlaceholderText('Ask your Finance Controller...');
    fireEvent.change(input, { target: { value: 'Why is it short?' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Test variance found.')).toBeInTheDocument();
      // Link should exist and have proper href
      const link = screen.getByText('Missing fee').closest('a');
      expect(link).toHaveAttribute('href', '/exceptions/123e4567-e89b-12d3-a456-426614174000');
    });
  });

  test('Render empty evidence state correctly', async () => {
    (api.queryAgent as jest.Mock).mockResolvedValue({
      status: 'SUCCESS',
      answer: 'Hello.',
      confidence: null,
      evidence: []
    });

    render(<AgentPage />);
    const input = screen.getByPlaceholderText('Ask your Finance Controller...');
    fireEvent.change(input, { target: { value: 'hi' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    await waitFor(() => {
      expect(screen.getByText('Hello.')).toBeInTheDocument();
      expect(screen.getByText('No supporting evidence found for this query.')).toBeInTheDocument();
      // Confidence should not be shown
      expect(screen.queryByText('Confidence')).not.toBeInTheDocument();
    });
  });
});
