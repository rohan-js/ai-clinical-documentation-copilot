'use client';

import React from 'react';
import { ProcessingStatus } from '@/lib/api';

interface ProcessingStatusProps {
    status: ProcessingStatus | null;
    error?: string | null;
}

const STEPS = [
    { key: 'uploading', label: 'Uploading', icon: '📤' },
    { key: 'transcribing', label: 'Transcribing', icon: '🎙️' },
    { key: 'extracting', label: 'Extracting', icon: '🔍' },
    { key: 'enhancing', label: 'Enhancing', icon: '✨' },
    { key: 'generating', label: 'Generating', icon: '📝' },
];

function getStepIndex(status: string | undefined): number {
    if (!status) return -1;
    const statusLower = status.toLowerCase();
    return STEPS.findIndex(s => statusLower.includes(s.key));
}

export default function ProcessingStatusComponent({ status, error }: ProcessingStatusProps) {
    const currentStepIndex = getStepIndex(status?.status);
    const progress = status?.progress || 0;
    const isCompleted = status?.status === 'completed';
    const isFailed = status?.status === 'failed' || error;

    if (isFailed) {
        return (
            <div className="card" style={{ borderColor: 'var(--error)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: '50%',
                        background: 'rgba(239, 68, 68, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--error)" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                    </div>
                    <div>
                        <h3 style={{ color: 'var(--error)' }}>Processing Failed</h3>
                        <p style={{ color: 'var(--text-muted)' }}>{error || status?.message || 'An error occurred'}</p>
                    </div>
                </div>
            </div>
        );
    }

    if (isCompleted) {
        return (
            <div className="card" style={{ borderColor: 'var(--success)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{
                        width: 48,
                        height: 48,
                        borderRadius: '50%',
                        background: 'rgba(16, 185, 129, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                            <polyline points="22 4 12 14.01 9 11.01" />
                        </svg>
                    </div>
                    <div>
                        <h3 style={{ color: 'var(--success)' }}>Processing Complete!</h3>
                        <p style={{ color: 'var(--text-muted)' }}>Your clinical documentation is ready</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                        {status?.current_step || 'Processing...'}
                    </span>
                    <span style={{ color: 'var(--primary-400)' }}>{progress}%</span>
                </div>
                <div className="progress-bar">
                    <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
                </div>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {STEPS.map((step, index) => {
                    const isActive = index === currentStepIndex;
                    const isComplete = index < currentStepIndex;

                    return (
                        <div
                            key={step.key}
                            className={`step ${isActive ? 'active' : ''} ${isComplete ? 'completed' : ''}`}
                            style={{ flex: '1', minWidth: '120px' }}
                        >
                            <div className="step-icon">
                                {isComplete ? (
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <polyline points="20 6 9 17 4 12" />
                                    </svg>
                                ) : isActive ? (
                                    <div className="animate-spin" style={{ width: 16, height: 16 }}>
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                                        </svg>
                                    </div>
                                ) : (
                                    <span>{step.icon}</span>
                                )}
                            </div>
                            <span style={{
                                fontSize: '0.875rem',
                                color: isActive ? 'var(--primary-400)' : isComplete ? 'var(--success)' : 'var(--text-muted)'
                            }}>
                                {step.label}
                            </span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
