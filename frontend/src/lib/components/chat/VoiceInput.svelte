<!--
  VoiceInput.svelte - Voice-to-text input using Web Speech API

  Cross-platform voice input:
  - macOS: Uses Apple's speech recognition
  - Windows: Uses Microsoft's speech recognition
  - Linux: Uses browser's implementation (Chrome recommended)

  All free, built into the browser/OS.
-->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { assistantSettings } from '$lib/stores';

  const dispatch = createEventDispatcher();

  export let disabled = false;

  let isListening = false;
  let isSupported = false;
  let recognition = null;
  let transcript = '';
  let error = null;

  // Get settings from store
  $: voiceEnabled = $assistantSettings.voiceEnabled ?? true;
  $: voiceLanguage = $assistantSettings.voiceLanguage ?? 'en-US';
  $: voiceContinuous = $assistantSettings.voiceContinuous ?? true;

  // Update recognition settings when they change
  $: if (recognition) {
    recognition.lang = voiceLanguage;
    recognition.continuous = voiceContinuous;
  }

  onMount(() => {
    // Check for Web Speech API support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      isSupported = true;
      recognition = new SpeechRecognition();

      // Configuration from settings
      recognition.continuous = voiceContinuous;
      recognition.interimResults = true;  // Show results as they come
      recognition.lang = voiceLanguage;

      // Event handlers
      recognition.onstart = () => {
        isListening = true;
        error = null;
        dispatch('start');
      };

      recognition.onend = () => {
        isListening = false;
        if (transcript.trim()) {
          dispatch('result', { transcript: transcript.trim() });
        }
        transcript = '';
        dispatch('end');
      };

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          if (result.isFinal) {
            finalTranscript += result[0].transcript;
          } else {
            interimTranscript += result[0].transcript;
          }
        }

        // Emit interim results for live preview
        if (interimTranscript) {
          dispatch('interim', { transcript: interimTranscript });
        }

        // Accumulate final transcript
        if (finalTranscript) {
          transcript += finalTranscript;
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);

        switch (event.error) {
          case 'not-allowed':
            error = 'Microphone access denied. Please allow microphone access in your browser settings.';
            break;
          case 'no-speech':
            error = 'No speech detected. Please try again.';
            break;
          case 'network':
            error = 'Network error. Please check your connection.';
            break;
          case 'aborted':
            // User cancelled - not an error to show
            break;
          default:
            error = `Speech recognition error: ${event.error}`;
        }

        isListening = false;
        dispatch('error', { error, code: event.error });
      };
    }
  });

  onDestroy(() => {
    if (recognition && isListening) {
      recognition.stop();
    }
  });

  function toggleListening() {
    if (!isSupported || disabled) return;

    if (isListening) {
      recognition.stop();
    } else {
      transcript = '';
      error = null;
      try {
        recognition.start();
      } catch (e) {
        // Already started - stop and restart
        recognition.stop();
      }
    }
  }

  function handleKeydown(e) {
    // Allow keyboard toggle with Space or Enter when focused
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      toggleListening();
    }
  }
</script>

{#if isSupported && voiceEnabled}
  <button
    class="voice-btn"
    class:listening={isListening}
    class:error={error}
    on:click={toggleListening}
    on:keydown={handleKeydown}
    disabled={disabled}
    title={isListening ? 'Stop listening' : 'Voice input'}
    aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
    aria-pressed={isListening}
  >
    {#if isListening}
      <!-- Listening indicator with animation -->
      <div class="listening-indicator">
        <span class="pulse"></span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2" fill="none" stroke="currentColor" stroke-width="2"></path>
          <line x1="12" y1="19" x2="12" y2="23" fill="none" stroke="currentColor" stroke-width="2"></line>
        </svg>
      </div>
    {:else}
      <!-- Default microphone icon -->
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
      </svg>
    {/if}
  </button>
{:else}
  <!-- Fallback for unsupported browsers -->
  <button
    class="voice-btn unsupported"
    disabled
    title="Voice input not supported in this browser"
  >
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="1" y1="1" x2="23" y2="23" stroke-width="2"></line>
    </svg>
  </button>
{/if}

<style>
  .voice-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
    position: relative;
  }

  .voice-btn:hover:not(:disabled) {
    background: var(--bg-tertiary, #252d38);
    border-color: var(--border-strong, #444c56);
    color: var(--text-secondary, #c9d1d9);
  }

  .voice-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .voice-btn.listening {
    background: rgba(248, 81, 73, 0.15);
    border-color: var(--error, #f85149);
    color: var(--error, #f85149);
  }

  .voice-btn.error {
    border-color: var(--warning, #d29922);
    color: var(--warning, #d29922);
  }

  .voice-btn.unsupported {
    opacity: 0.3;
  }

  .listening-indicator {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pulse {
    position: absolute;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--error, #f85149);
    opacity: 0.3;
    animation: pulse 1.5s ease-out infinite;
  }

  @keyframes pulse {
    0% {
      transform: scale(0.8);
      opacity: 0.4;
    }
    50% {
      transform: scale(1.2);
      opacity: 0.2;
    }
    100% {
      transform: scale(0.8);
      opacity: 0.4;
    }
  }
</style>
