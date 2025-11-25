/**
 * Toast notification store
 *
 * Usage:
 * import { addToast, dismissToast } from '$lib/toastStore';
 * addToast({ type: 'success', message: 'Settings saved!' });
 * addToast({ type: 'error', message: 'Failed to save', duration: 5000 });
 */

import { writable } from 'svelte/store';

// Store for active toasts
export const toasts = writable([]);

let toastId = 0;

/**
 * Add a new toast notification
 * @param {Object} options Toast options
 * @param {string} options.type - 'success' | 'error' | 'warning' | 'info'
 * @param {string} options.message - The message to display
 * @param {number} [options.duration=3000] - Auto-dismiss time in ms (0 for no auto-dismiss)
 * @param {Object} [options.action] - Optional action button
 * @param {string} options.action.label - Button label
 * @param {Function} options.action.handler - Click handler
 * @returns {number} The toast ID
 */
export function addToast({ type = 'info', message, duration = 3000, action = null }) {
  const id = ++toastId;

  const toast = {
    id,
    type,
    message,
    action
  };

  toasts.update(t => [...t, toast]);

  // Auto-dismiss if duration > 0
  if (duration > 0) {
    setTimeout(() => {
      dismissToast(id);
    }, duration);
  }

  return id;
}

/**
 * Dismiss a toast by ID
 * @param {number} id The toast ID to dismiss
 */
export function dismissToast(id) {
  toasts.update(t => t.filter(toast => toast.id !== id));
}

/**
 * Dismiss all toasts
 */
export function clearToasts() {
  toasts.set([]);
}
