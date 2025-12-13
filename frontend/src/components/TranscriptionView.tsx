'use client';

import React from 'react';
import { TranscriptionResult } from '@/lib/api';

interface TranscriptionViewProps {
    transcription: TranscriptionResult;
}

function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function TranscriptionView({ transcription }: TranscriptionViewProps) {
    if (!transcription.success || !transcription.text) {
        return (
            <div className="card">
                <div className="section-title">
                    <div className="section-title-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        </svg>
                    </div>
                    <h2>Transcription</h2>
                </div>
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                    {transcription.error || 'No transcription available'}
                </p>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    </svg>
                </div>
                <h2>Transcription</h2>
                {transcription.duration && (
                    <span style={{
                        marginLeft: 'auto',
                        fontSize: '0.875rem',
                        color: 'var(--text-muted)',
                        background: 'var(--bg-tertiary)',
                        padding: '0.25rem 0.75rem',
                        borderRadius: 'var(--radius-full)'
                    }}>
                        Duration: {formatTime(transcription.duration)}
                    </span>
                )}
            </div>

            {/* Full text */}
            <div style={{
                background: 'var(--bg-tertiary)',
                padding: '1.5rem',
                borderRadius: 'var(--radius-lg)',
                marginBottom: '1.5rem',
                maxHeight: '300px',
                overflowY: 'auto'
            }}>
                <p style={{
                    color: 'var(--text-primary)',
                    lineHeight: 1.8,
                    whiteSpace: 'pre-wrap'
                }}>
                    {transcription.text}
                </p>
            </div>

            {/* Segments */}
            {transcription.segments && transcription.segments.length > 0 && (
                <div>
                    <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        Timestamped Segments
                    </h4>
                    <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                        {transcription.segments.map((segment, index) => (
                            <div
                                key={index}
                                style={{
                                    display: 'flex',
                                    gap: '1rem',
                                    padding: '0.75rem',
                                    borderBottom: '1px solid var(--border-subtle)',
                                }}
                            >
                                <span style={{
                                    color: 'var(--primary-400)',
                                    fontFamily: 'monospace',
                                    fontSize: '0.875rem',
                                    minWidth: '80px'
                                }}>
                                    {formatTime(segment.start)}
                                </span>
                                <p style={{ color: 'var(--text-secondary)', flex: 1 }}>
                                    {segment.text}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {transcription.language && (
                <div style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Detected language: <span style={{ color: 'var(--text-secondary)' }}>{transcription.language}</span>
                </div>
            )}
        </div>
    );
}
