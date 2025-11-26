/**
 * Frontend API Key Validation Tests
 *
 * Tests the API key validation functionality in SettingsAgents.svelte component.
 * Validates UI logic, error handling, and integration with backend validation endpoint.
 *
 * Related Backend Tests: backend/tests/test_api_key_validation.py
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import SettingsAgents from '$lib/components/Settings/SettingsAgents.svelte';

// =============================================================================
// Test Setup
// =============================================================================

const BASE_URL = 'http://localhost:8000';

const mockFetch = (response: any, ok: boolean = true) => {
  global.fetch = vi.fn().mockResolvedValue({
    ok,
    json: async () => response,
    status: ok ? 200 : 400,
  });
};

const mockFetchError = (error: Error) => {
  global.fetch = vi.fn().mockRejectedValue(error);
};

// =============================================================================
// Test Suite: API Key Validation Success Cases
// =============================================================================

describe('API Key Validation - Success Cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should validate DeepSeek API key successfully', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'deepseek' });

    render(SettingsAgents);

    // Find DeepSeek input (first provider)
    const inputs = screen.getAllByPlaceholderText('sk-...');
    const deepseekInput = inputs[0]; // DeepSeek is first in the list

    // Enter API key
    await user.type(deepseekInput, 'sk-valid-deepseek-key');

    // Click test button
    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Wait for API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            provider: 'deepseek',
            api_key: 'sk-valid-deepseek-key',
          }),
        })
      );
    });

    // Check for success indicator (green checkmark)
    await waitFor(() => {
      expect(screen.queryByText('✓')).toBeInTheDocument();
    });
  });

  it('should validate OpenAI API key successfully', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'openai' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    const openaiInput = inputs[1]; // OpenAI is second

    await user.type(openaiInput, 'sk-valid-openai-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[1]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'openai',
            api_key: 'sk-valid-openai-key',
          }),
        })
      );
    });
  });

  it('should validate Anthropic (Claude) API key successfully', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'anthropic' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-ant-...');
    await user.type(inputs[0], 'sk-ant-valid-claude-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[2]); // Anthropic is 3rd provider

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'anthropic',
            api_key: 'sk-ant-valid-claude-key',
          }),
        })
      );
    });
  });

  it('should validate Google Gemini API key successfully', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'google' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('AIza...');
    await user.type(inputs[0], 'AIzaSyValid_Google_Key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[3]); // Google is 4th provider

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'google',
            api_key: 'AIzaSyValid_Google_Key',
          }),
        })
      );
    });
  });
});

// =============================================================================
// Test Suite: API Key Validation Error Cases
// =============================================================================

describe('API Key Validation - Error Cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show error for invalid DeepSeek API key', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: false, error: '401: Unauthorized' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-invalid-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('✗')).toBeInTheDocument();
    });
  });

  it('should handle empty API key gracefully', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: false, error: 'API key is empty' });

    render(SettingsAgents);

    // Click test without entering a key
    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Should not make API call for empty key
    await waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  it('should handle network errors gracefully', async () => {
    const user = userEvent.setup();
    mockFetchError(new Error('Network connection failed'));

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-some-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('✗')).toBeInTheDocument();
    });
  });

  it('should handle 401 Unauthorized errors', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: false, error: '401: Unauthorized' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-unauthorized-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
      expect(screen.queryByText('✗')).toBeInTheDocument();
    });
  });

  it('should handle whitespace-only API keys', async () => {
    const user = userEvent.setup();

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], '   '); // Just spaces

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Should not make API call for whitespace
    await waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });
});

// =============================================================================
// Test Suite: UI State Management
// =============================================================================

describe('API Key UI State Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show loading state during validation', async () => {
    const user = userEvent.setup();

    // Mock delayed response
    let resolvePromise: any;
    global.fetch = vi.fn().mockReturnValue(
      new Promise((resolve) => {
        resolvePromise = resolve;
      })
    );

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-test-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Check for loading indicator
    await waitFor(() => {
      expect(screen.queryByText('Testing...')).toBeInTheDocument();
    });

    // Resolve the promise
    resolvePromise({
      ok: true,
      json: async () => ({ valid: true, provider: 'deepseek' }),
    });

    // Loading should disappear
    await waitFor(() => {
      expect(screen.queryByText('Testing...')).not.toBeInTheDocument();
    });
  });

  it('should clear previous test results when testing again', async () => {
    const user = userEvent.setup();

    // First test - success
    mockFetch({ valid: true, provider: 'deepseek' });
    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-first-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('✓')).toBeInTheDocument();
    });

    // Second test - failure
    vi.clearAllMocks();
    mockFetch({ valid: false, error: 'Invalid key' });

    await user.clear(inputs[0]);
    await user.type(inputs[0], 'sk-second-key');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('✗')).toBeInTheDocument();
      expect(screen.queryByText('✓')).not.toBeInTheDocument();
    });
  });

  it('should disable test button while testing', async () => {
    const user = userEvent.setup();

    let resolvePromise: any;
    global.fetch = vi.fn().mockReturnValue(
      new Promise((resolve) => {
        resolvePromise = resolve;
      })
    );

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-test-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Button should be disabled
    await waitFor(() => {
      expect(testButtons[0]).toBeDisabled();
    });

    // Resolve promise
    resolvePromise({
      ok: true,
      json: async () => ({ valid: true, provider: 'deepseek' }),
    });

    // Button should be enabled again
    await waitFor(() => {
      expect(testButtons[0]).not.toBeDisabled();
    });
  });
});

// =============================================================================
// Test Suite: Multiple Provider Testing
// =============================================================================

describe('Multiple Provider API Key Validation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should test multiple providers independently', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'deepseek' });

    render(SettingsAgents);

    // Test DeepSeek
    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-deepseek-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'deepseek',
            api_key: 'sk-deepseek-key',
          }),
        })
      );
    });

    // Test OpenAI independently
    vi.clearAllMocks();
    mockFetch({ valid: true, provider: 'openai' });

    await user.type(inputs[1], 'sk-openai-key');
    await user.click(testButtons[1]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'openai',
            api_key: 'sk-openai-key',
          }),
        })
      );
    });
  });

  it('should handle mixed success/failure across providers', async () => {
    const user = userEvent.setup();

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    const testButtons = screen.getAllByText('Test');

    // DeepSeek - Success
    mockFetch({ valid: true, provider: 'deepseek' });
    await user.type(inputs[0], 'sk-valid-deepseek');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(screen.queryAllByText('✓').length).toBeGreaterThan(0);
    });

    // OpenAI - Failure
    vi.clearAllMocks();
    mockFetch({ valid: false, error: 'Invalid key' });
    await user.type(inputs[1], 'sk-invalid-openai');
    await user.click(testButtons[1]);

    await waitFor(() => {
      expect(screen.queryAllByText('✗').length).toBeGreaterThan(0);
    });

    // Both results should coexist
    expect(screen.queryByText('✓')).toBeInTheDocument();
    expect(screen.queryByText('✗')).toBeInTheDocument();
  });
});

// =============================================================================
// Test Suite: Edge Cases
// =============================================================================

describe('API Key Validation - Edge Cases', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle very long API keys', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'deepseek' });

    render(SettingsAgents);

    const longKey = 'sk-' + 'x'.repeat(500);
    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], longKey);

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'deepseek',
            api_key: longKey,
          }),
        })
      );
    });
  });

  it('should handle special characters in API keys', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'deepseek' });

    render(SettingsAgents);

    const specialKey = 'sk-!@#$%^&*()_+-=[]{}|;:,.<>?';
    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], specialKey);

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `${BASE_URL}/api-keys/test`,
        expect.objectContaining({
          body: JSON.stringify({
            provider: 'deepseek',
            api_key: specialKey,
          }),
        })
      );
    });
  });

  it('should handle rapid successive test clicks', async () => {
    const user = userEvent.setup();
    mockFetch({ valid: true, provider: 'deepseek' });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-test-key');

    const testButtons = screen.getAllByText('Test');

    // Click multiple times rapidly
    await user.click(testButtons[0]);
    await user.click(testButtons[0]);
    await user.click(testButtons[0]);

    // Should only make one API call (button disabled during test)
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  it('should handle malformed JSON response gracefully', async () => {
    const user = userEvent.setup();

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => {
        throw new Error('Invalid JSON');
      },
    });

    render(SettingsAgents);

    const inputs = screen.getAllByPlaceholderText('sk-...');
    await user.type(inputs[0], 'sk-test-key');

    const testButtons = screen.getAllByText('Test');
    await user.click(testButtons[0]);

    // Should show error state
    await waitFor(() => {
      expect(screen.queryByText('✗')).toBeInTheDocument();
    });
  });
});
