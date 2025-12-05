/**
 * Toast notification store
 *
 * Usage:
 * import { addToast, dismissToast } from '$lib/toastStore';
 * addToast({ type: 'success', message: 'Settings saved!' });
 * addToast({ type: 'error', message: 'Failed to save', duration: 5000 });
 */

import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastAction {
  label: string;
  onClick: () => void;
}

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  action: ToastAction | null;
}

export interface ToastOptions {
  type?: ToastType;
  message: string;
  duration?: number;
  action?: ToastAction | null;
}

// Store for active toasts
export const toasts = writable<Toast[]>([]);

let toastId = 0;

/**
 * Add a new toast notification
 *
 * Usage:
 * addToast({ type: 'success', message: 'Settings saved!' });
 * addToast('Settings saved!', 'success');
 * addToast('Error occurred', 'error', 5000);
 */
export function addToast(
  options: ToastOptions | string,
  typeArg: ToastType = 'info',
  durationArg: number = 3000
): number {
  const id = ++toastId;

  // Support both object and string signatures
  let type: ToastType;
  let message: string;
  let duration: number;
  let action: ToastAction | null;

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

  const toast: Toast = {
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
 */
export function dismissToast(id: number): void {
  toasts.update(t => t.filter(toast => toast.id !== id));
}

/**
 * Dismiss all toasts
 */
export function clearToasts(): void {
  toasts.set([]);
}
