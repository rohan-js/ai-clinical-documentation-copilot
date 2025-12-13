'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import api, { ProcessingStatus, ProcessingResult } from '@/lib/api';

export type ProcessingState =
    | 'idle'
    | 'uploading'
    | 'processing'
    | 'completed'
    | 'error';

export interface UseProcessingReturn {
    state: ProcessingState;
    status: ProcessingStatus | null;
    result: ProcessingResult | null;
    error: string | null;
    sessionId: string | null;
    audioFile: File | null;
    notesFile: File | null;
    setAudioFile: (file: File | null) => void;
    setNotesFile: (file: File | null) => void;
    uploadFiles: () => Promise<void>;
    startProcessing: () => Promise<void>;
    reset: () => void;
}

export function useProcessing(): UseProcessingReturn {
    const [state, setState] = useState<ProcessingState>('idle');
    const [status, setStatus] = useState<ProcessingStatus | null>(null);
    const [result, setResult] = useState<ProcessingResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [audioFile, setAudioFile] = useState<File | null>(null);
    const [notesFile, setNotesFile] = useState<File | null>(null);

    const pollingRef = useRef<NodeJS.Timeout | null>(null);

    const stopPolling = useCallback(() => {
        if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
        }
    }, []);

    useEffect(() => {
        return () => stopPolling();
    }, [stopPolling]);

    const pollStatus = useCallback(async (sid: string) => {
        try {
            const statusResponse = await api.getProcessingStatus(sid);
            setStatus(statusResponse);

            if (statusResponse.status === 'completed') {
                stopPolling();
                const resultResponse = await api.getProcessingResult(sid);
                setResult(resultResponse);
                setState('completed');
            } else if (statusResponse.status === 'failed') {
                stopPolling();
                setError(statusResponse.message || 'Processing failed');
                setState('error');
            }
        } catch (err) {
            console.error('Polling error:', err);
        }
    }, [stopPolling]);

    const uploadFiles = useCallback(async () => {
        if (!audioFile && !notesFile) {
            setError('Please upload at least one file');
            return;
        }

        setState('uploading');
        setError(null);

        try {
            let currentSessionId = sessionId;

            // Upload audio file
            if (audioFile) {
                const audioResponse = await api.uploadAudio(audioFile, currentSessionId || undefined);
                if (!audioResponse.success) {
                    throw new Error('Audio upload failed');
                }
                currentSessionId = audioResponse.session_id;
                setSessionId(currentSessionId);
            }

            // Upload notes file
            if (notesFile) {
                const notesResponse = await api.uploadNotes(notesFile, currentSessionId || undefined);
                if (!notesResponse.success) {
                    throw new Error('Notes upload failed');
                }
                currentSessionId = notesResponse.session_id;
                setSessionId(currentSessionId);
            }

            setSessionId(currentSessionId);
            setState('idle');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Upload failed');
            setState('error');
        }
    }, [audioFile, notesFile, sessionId]);

    const startProcessing = useCallback(async () => {
        if (!sessionId) {
            // If no session yet, upload files first
            if (!audioFile && !notesFile) {
                setError('Please upload at least one file');
                return;
            }

            setState('uploading');
            setError(null);

            try {
                let currentSessionId: string | null = null;

                if (audioFile) {
                    const audioResponse = await api.uploadAudio(audioFile);
                    currentSessionId = audioResponse.session_id;
                }

                if (notesFile) {
                    const notesResponse = await api.uploadNotes(notesFile, currentSessionId || undefined);
                    currentSessionId = notesResponse.session_id;
                }

                if (!currentSessionId) {
                    throw new Error('Failed to create session');
                }

                setSessionId(currentSessionId);

                // Start processing
                setState('processing');
                const statusResponse = await api.startProcessing(currentSessionId);
                setStatus(statusResponse);

                // Start polling
                pollingRef.current = setInterval(() => {
                    pollStatus(currentSessionId!);
                }, 2000);

            } catch (err) {
                setError(err instanceof Error ? err.message : 'Processing failed');
                setState('error');
            }
            return;
        }

        // Session exists, start processing
        setState('processing');
        setError(null);

        try {
            const statusResponse = await api.startProcessing(sessionId);
            setStatus(statusResponse);

            // Start polling for status updates
            pollingRef.current = setInterval(() => {
                pollStatus(sessionId);
            }, 2000);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Processing failed');
            setState('error');
        }
    }, [sessionId, audioFile, notesFile, pollStatus]);

    const reset = useCallback(() => {
        stopPolling();
        setState('idle');
        setStatus(null);
        setResult(null);
        setError(null);
        setSessionId(null);
        setAudioFile(null);
        setNotesFile(null);
    }, [stopPolling]);

    return {
        state,
        status,
        result,
        error,
        sessionId,
        audioFile,
        notesFile,
        setAudioFile,
        setNotesFile,
        uploadFiles,
        startProcessing,
        reset,
    };
}
