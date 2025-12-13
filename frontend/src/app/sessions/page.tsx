'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api, { SessionListItem } from '@/lib/api';
import SessionCard from '@/components/SessionCard';

export default function SessionsPage() {
    const router = useRouter();
    const [sessions, setSessions] = useState<SessionListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSessions();
    }, []);

    async function fetchSessions() {
        try {
            setLoading(true);
            const data = await api.listSessions();
            setSessions(data.sessions);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load sessions');
        } finally {
            setLoading(false);
        }
    }

    async function handleDelete(sessionId: string) {
        if (!confirm('Are you sure you want to delete this session?')) {
            return;
        }

        try {
            await api.deleteSession(sessionId);
            setSessions(sessions.filter(s => s.id !== sessionId));
        } catch (err) {
            alert(err instanceof Error ? err.message : 'Failed to delete session');
        }
    }

    function handleSelect(sessionId: string) {
        router.push(`/results/${sessionId}`);
    }

    if (loading) {
        return (
            <div className="container">
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <div className="animate-spin" style={{ width: 48, height: 48, margin: '0 auto 1rem' }}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary-400)" strokeWidth="2">
                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                        </svg>
                    </div>
                    <h2>Loading sessions...</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="container">
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '2rem'
            }}>
                <div>
                    <h1>Session History</h1>
                    <p style={{ color: 'var(--text-muted)' }}>
                        View and manage your previous documentation sessions
                    </p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => router.push('/')}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19" />
                        <line x1="5" y1="12" x2="19" y2="12" />
                    </svg>
                    New Session
                </button>
            </div>

            {/* Error message */}
            {error && (
                <div className="card" style={{
                    marginBottom: '2rem',
                    borderColor: 'var(--error)',
                    background: 'rgba(239, 68, 68, 0.1)'
                }}>
                    <p style={{ color: 'var(--error)' }}>{error}</p>
                    <button className="btn btn-secondary" onClick={fetchSessions} style={{ marginTop: '1rem' }}>
                        Try Again
                    </button>
                </div>
            )}

            {/* Sessions list */}
            {sessions.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
                    <div style={{
                        width: 80,
                        height: 80,
                        margin: '0 auto 1.5rem',
                        borderRadius: '50%',
                        background: 'var(--bg-tertiary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1.5">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                        </svg>
                    </div>
                    <h2 style={{ marginBottom: '0.5rem' }}>No Sessions Yet</h2>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                        Upload your first audio or notes file to get started
                    </p>
                    <button className="btn btn-primary btn-lg" onClick={() => router.push('/')}>
                        Create Your First Session
                    </button>
                </div>
            ) : (
                <div className="grid-2">
                    {sessions.map((session) => (
                        <SessionCard
                            key={session.id}
                            session={session}
                            onSelect={handleSelect}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            {/* Stats */}
            {sessions.length > 0 && (
                <div style={{
                    textAlign: 'center',
                    marginTop: '2rem',
                    padding: '1.5rem',
                    background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-lg)'
                }}>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Total sessions: <strong style={{ color: 'var(--text-primary)' }}>{sessions.length}</strong>
                        {' • '}
                        Completed: <strong style={{ color: 'var(--success)' }}>
                            {sessions.filter(s => s.status === 'completed').length}
                        </strong>
                    </p>
                </div>
            )}
        </div>
    );
}
