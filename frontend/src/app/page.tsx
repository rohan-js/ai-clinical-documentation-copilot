'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import AudioUploader from '@/components/AudioUploader';
import NotesUploader from '@/components/NotesUploader';
import ProcessingStatusComponent from '@/components/ProcessingStatus';
import { useProcessing } from '@/hooks/useProcessing';

export default function UploadPage() {
    const router = useRouter();
    const {
        state,
        status,
        result,
        error,
        sessionId,
        audioFile,
        notesFile,
        setAudioFile,
        setNotesFile,
        startProcessing,
        reset,
    } = useProcessing();

    const isProcessing = state === 'processing' || state === 'uploading';
    const hasFiles = audioFile !== null || notesFile !== null;

    // Navigate to results when completed
    React.useEffect(() => {
        if (state === 'completed' && sessionId) {
            router.push(`/results/${sessionId}`);
        }
    }, [state, sessionId, router]);

    return (
        <div className="container">
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{
                    background: 'linear-gradient(135deg, var(--primary-400) 0%, var(--accent-teal) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    marginBottom: '1rem'
                }}>
                    AI Clinical Documentation Copilot
                </h1>
                <p style={{
                    fontSize: '1.125rem',
                    color: 'var(--text-secondary)',
                    maxWidth: '600px',
                    margin: '0 auto'
                }}>
                    Upload audio recordings or clinical notes to automatically generate
                    structured medical documentation powered by AI.
                </p>
            </div>

            {/* Processing Status */}
            {(isProcessing || state === 'completed' || error) && (
                <div style={{ marginBottom: '2rem' }} className="animate-slide-in">
                    <ProcessingStatusComponent status={status} error={error} />
                </div>
            )}

            {/* Upload Section */}
            {!isProcessing && state !== 'completed' && (
                <>
                    <div className="grid-2" style={{ marginBottom: '2rem' }}>
                        <AudioUploader
                            file={audioFile}
                            onFileChange={setAudioFile}
                            disabled={isProcessing}
                        />
                        <NotesUploader
                            file={notesFile}
                            onFileChange={setNotesFile}
                            disabled={isProcessing}
                        />
                    </div>

                    {/* Action Buttons */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'center',
                        gap: '1rem',
                        marginTop: '2rem'
                    }}>
                        {error && (
                            <button
                                className="btn btn-secondary btn-lg"
                                onClick={reset}
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
                                    <path d="M21 3v5h-5" />
                                    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
                                    <path d="M3 21v-5h5" />
                                </svg>
                                Reset
                            </button>
                        )}

                        <button
                            className="btn btn-primary btn-lg"
                            disabled={!hasFiles || isProcessing}
                            onClick={startProcessing}
                        >
                            {isProcessing ? (
                                <>
                                    <div className="animate-spin">
                                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                                        </svg>
                                    </div>
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polygon points="5 3 19 12 5 21 5 3" />
                                    </svg>
                                    Generate Documentation
                                </>
                            )}
                        </button>
                    </div>
                </>
            )}

            {/* Features Section */}
            <div style={{ marginTop: '4rem' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--text-secondary)' }}>
                    How It Works
                </h2>
                <div className="grid-3">
                    <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{
                            width: 64,
                            height: 64,
                            margin: '0 auto 1rem',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, rgba(13, 122, 156, 0.3) 0%, rgba(13, 122, 156, 0.1) 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--primary-400)" strokeWidth="1.5">
                                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                                <line x1="12" y1="19" x2="12" y2="22" />
                            </svg>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>1. Upload</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Upload audio recordings or clinical notes for processing
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{
                            width: 64,
                            height: 64,
                            margin: '0 auto 1rem',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(139, 92, 246, 0.1) 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--accent-violet)" strokeWidth="1.5">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                                <line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>2. AI Processing</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            AI transcribes, extracts entities, and applies clinical guidelines
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{
                            width: 64,
                            height: 64,
                            margin: '0 auto 1rem',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.3) 0%, rgba(16, 185, 129, 0.1) 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" strokeWidth="1.5">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                <polyline points="14 2 14 8 20 8" />
                                <line x1="16" y1="13" x2="8" y2="13" />
                                <line x1="16" y1="17" x2="8" y2="17" />
                            </svg>
                        </div>
                        <h3 style={{ marginBottom: '0.5rem' }}>3. Documentation</h3>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Get structured SOAP notes, summaries, and follow-up tasks
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
