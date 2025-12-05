<script>
    import { onMount, onDestroy } from 'svelte';
    import { writable } from 'svelte/store';

    export let apiBase = 'http://localhost:8000';
    export let pollInterval = 5000;

    let notifications = [];
    let pollTimer;
    let loading = false;

    async function fetchNotifications() {
        if (loading) return;
        loading = true;

        try {
            const response = await fetch(`${apiBase}/verification/notifications`);
            if (response.ok) {
                const data = await response.json();
                if (data.notifications && data.notifications.length > 0) {
                    // Add new notifications (avoiding duplicates)
                    const existingIds = new Set(notifications.map(n => n.id));
                    const newNotifications = data.notifications.filter(n => !existingIds.has(n.id));
                    notifications = [...notifications, ...newNotifications];
                }
            }
        } catch (e) {
            console.error('Failed to fetch verification notifications:', e);
        } finally {
            loading = false;
        }
    }

    function dismissNotification(id) {
        notifications = notifications.filter(n => n.id !== id);
    }

    function dismissAll() {
        notifications = [];
    }

    function severityColor(severity) {
        switch(severity) {
            case 'critical': return 'bg-red-50 border-red-500 text-red-800';
            case 'warning': return 'bg-yellow-50 border-yellow-500 text-yellow-800';
            case 'info': return 'bg-blue-50 border-blue-500 text-blue-800';
            default: return 'bg-gray-50 border-gray-500 text-gray-800';
        }
    }

    function severityIcon(severity) {
        switch(severity) {
            case 'critical': return 'X';
            case 'warning': return '!';
            case 'info': return 'i';
            default: return '?';
        }
    }

    function severityBadgeColor(severity) {
        switch(severity) {
            case 'critical': return 'bg-red-500';
            case 'warning': return 'bg-yellow-500';
            case 'info': return 'bg-blue-500';
            default: return 'bg-gray-500';
        }
    }

    onMount(() => {
        fetchNotifications();
        pollTimer = setInterval(fetchNotifications, pollInterval);
    });

    onDestroy(() => {
        if (pollTimer) clearInterval(pollTimer);
    });
</script>

{#if notifications.length > 0}
<div class="fixed bottom-4 right-4 z-50 max-w-sm space-y-2">
    <!-- Header with dismiss all -->
    <div class="flex justify-between items-center px-2 text-xs text-gray-500">
        <span>Verification ({notifications.length})</span>
        <button
            on:click={dismissAll}
            class="hover:text-gray-700 underline"
        >
            Dismiss all
        </button>
    </div>

    <!-- Notifications -->
    {#each notifications as notif (notif.id)}
        <div
            class="p-3 rounded-lg border-l-4 shadow-lg animate-slide-in {severityColor(notif.severity)}"
            role="alert"
        >
            <div class="flex justify-between items-start gap-2">
                <!-- Severity badge -->
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold {severityBadgeColor(notif.severity)}">
                    {severityIcon(notif.severity)}
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                    <p class="font-semibold text-sm">
                        {notif.check_name.replace(/_/g, ' ')}
                    </p>
                    <p class="text-sm mt-1 break-words">{notif.message}</p>
                    {#if notif.suggestion}
                        <p class="text-xs mt-2 opacity-75 italic">
                            Tip: {notif.suggestion}
                        </p>
                    {/if}
                    {#if notif.scene_id && notif.scene_id !== 'unknown'}
                        <p class="text-xs mt-1 opacity-60">
                            Scene: {notif.scene_id}
                        </p>
                    {/if}
                </div>

                <!-- Dismiss button -->
                <button
                    on:click={() => dismissNotification(notif.id)}
                    class="flex-shrink-0 text-gray-400 hover:text-gray-600 text-lg leading-none"
                    aria-label="Dismiss notification"
                >
                    &times;
                </button>
            </div>
        </div>
    {/each}
</div>
{/if}

<style>
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
</style>
