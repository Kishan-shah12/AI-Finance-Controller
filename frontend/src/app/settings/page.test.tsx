import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SettingsPage from './page';
import { api } from '@/lib/api';

jest.mock('@/lib/api', () => ({
  api: {
    getDependenciesHealth: jest.fn().mockResolvedValue({
      database: 'HEALTHY',
      synthetic_provider: 'HEALTHY',
      razorpay_provider: 'NOT_CONFIGURED',
      llm_provider: 'HEALTHY'
    }),
    getRazorpayStatus: jest.fn().mockResolvedValue({
      configured: false,
      message: 'Backend unreachable'
    })
  }
}));

describe('SettingsPage Tabs', () => {
  beforeEach(() => {
    // Reset hash before each test
    window.location.hash = '';
    jest.clearAllMocks();
  });

  test('A. Automation Policy opens by default', async () => {
    render(<SettingsPage />);
    expect(screen.getByText('Automation Policy', { selector: 'button' })).toBeInTheDocument();
    expect(screen.getByText('Safe Automation Visualization')).toBeInTheDocument();
  });

  test('B. Providers opens when clicked', async () => {
    render(<SettingsPage />);
    const btn = screen.getByText('Providers', { selector: 'button' });
    fireEvent.click(btn);
    
    expect(window.location.hash).toBe('#providers');
    await waitFor(() => {
      expect(screen.getByText('Connected Providers')).toBeInTheDocument();
      expect(screen.getByText('Razorpay (Test Mode)')).toBeInTheDocument();
    });
  });

  test('C. System Status opens when clicked', async () => {
    render(<SettingsPage />);
    const btn = screen.getByText('System Status', { selector: 'button' });
    fireEvent.click(btn);
    
    expect(window.location.hash).toBe('#system');
    await waitFor(() => {
      expect(screen.getByText('Real-time health of core dependencies and backend services.')).toBeInTheDocument();
      // Verifying API data is shown (H. provider/system data remains real)
      expect(screen.getByText('database')).toBeInTheDocument();
      expect(screen.getByText('synthetic provider')).toBeInTheDocument();
    });
  });

  test('D. Demo Mode opens when clicked', async () => {
    render(<SettingsPage />);
    const btn = screen.getByText('Demo Mode', { selector: 'button' });
    fireEvent.click(btn);
    
    expect(window.location.hash).toBe('#demo');
    await waitFor(() => {
      expect(screen.getByText('Demo Configuration')).toBeInTheDocument();
      expect(screen.getByText('Deterministic Seed')).toBeInTheDocument();
    });
  });

  test('E. active state updates', async () => {
    render(<SettingsPage />);
    const providersBtn = screen.getByText('Providers', { selector: 'button' });
    const automationBtn = screen.getByText('Automation Policy', { selector: 'button' });
    
    expect(automationBtn).toHaveClass('bg-muted text-foreground');
    expect(providersBtn).toHaveClass('text-muted-foreground');
    
    fireEvent.click(providersBtn);
    
    expect(providersBtn).toHaveClass('bg-muted text-foreground');
    expect(automationBtn).toHaveClass('text-muted-foreground');
  });

  test('F. direct URL/hash navigation opens the correct tab', async () => {
    window.location.hash = '#system';
    render(<SettingsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Real-time health of core dependencies and backend services.')).toBeInTheDocument();
    });
  });

  test('G. no tab creates an invalid "#"', async () => {
    render(<SettingsPage />);
    const providersBtn = screen.getByText('Providers', { selector: 'button' });
    fireEvent.click(providersBtn);
    
    expect(window.location.hash).toBe('#providers');
    expect(window.location.href.endsWith('/#')).toBe(false);
  });
});
