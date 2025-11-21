import { writable } from 'svelte/store';

export const editorContent = writable("");
export const activeFile = writable("");
export const isSaving = writable(false);
export const notebookStatus = writable("checking");
export const notebookList = writable([]);
export const selectedNotebookId = writable("");
export const notebookLoading = writable(false);
export const notebookError = writable("");
export const notebookResult = writable(null);
