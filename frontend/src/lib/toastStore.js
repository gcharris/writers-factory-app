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
 * @param {Object|string} options Toast options or message string
 * @param {string} [typeArg] - Type if first arg is message string: 'success' | 'error' | 'warning' | 'info'
 * @param {number} [durationArg] - Duration if using string signature
 * @returns {number} The toast ID
 *
 * Usage:
 * addToast({ type: 'success', message: 'Settings saved!' });
 * addToast('Settings saved!', 'success');
 * addToast('Error occurred', 'error', 5000);
 */
export function addToast(options, typeArg = 'info', durationArg = 3000) {
  const id = ++toastId;

  // Support both object and string signatures
  let type, message, duration, action;
  if (typeof options === 'string') {
    message = options;
    type = typeArg;
    duration = durationArg;
    action = null;
  } else {
    type = options.type || 'info';
    message = options.message;
    duration = options.duration ?? 3000;
    action = options.action || null;
  }

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
