'use client';

import React from 'react';
import { SessionListItem } from '@/lib/api';

interface SessionCardProps {
    session: SessionListItem;
    onSelect: (sessionId: string) => void;
    onDelete?: (sessionId: string) => void;
}

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
    pending: { label: 'Pending', color: '#64748b', icon: '⏳' },
    uploading: { label: 'Uploading', color: '#3b82f6', icon: '📤' },
    transcribing: { label: 'Transcribing', color: '#8b5cf6', icon: '🎙️' },
    extracting: { label: 'Extracting', color: '#f59e0b', icon: '🔍' },
    enhancing: { label: 'Enhancing', color: '#14b8a6', icon: '✨' },
    generating: { label: 'Generating', color: '#0d7a9c', icon: '📝' },
    completed: { label: 'Completed', color: '#10b981', icon: '✅' },
    failed: { label: 'Failed', color: '#ef4444', icon: '❌' },
};

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

export default function SessionCard({ session, onSelect, onDelete }: SessionCardProps) {
    const statusConfig = STATUS_CONFIG[session.status] || STATUS_CONFIG.pending;

    return (
        <div
            className="card"
            style={{
                cursor: 'pointer',
                transition: 'all var(--transition-default)',
            }}
            onClick={() => onSelect(session.id)}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                    <h3 style={{
                        fontSize: '1rem',
                        fontWeight: 500,
                        color: 'var(--text-primary)',
                        marginBottom: '0.25rem'
                    }}>
                        {session.id}
                    </h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                        {formatDate(session.created_at)}
                    </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        padding: '0.25rem 0.75rem',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        background: `${statusConfig.color}20`,
                        color: statusConfig.color,
                    }}>
                        {statusConfig.icon} {statusConfig.label}
                    </span>

                    {onDelete && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(session.id);
                            }}
                            className="btn btn-ghost"
                            style={{ padding: '0.25rem' }}
                            title="Delete session"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                        </button>
                    )}
                </div>
            </div>

            {/* File indicators */}
            <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
                {session.has_audio && (
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        fontSize: '0.75rem',
                        color: 'var(--primary-400)',
                    }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        </svg>
                        Audio
                    </span>
                )}
                {session.has_notes && (
                    <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        fontSize: '0.75rem',
                        color: 'var(--accent-teal)',
                    }}>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                        </svg>
                        Notes
                    </span>
                )}
            </div>

            {/* Preview */}
            {session.preview && (
                <p style={{
                    fontSize: '0.875rem',
                    color: 'var(--text-muted)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                }}>
                    {session.preview}
                </p>
            )}
        </div>
    );
}
