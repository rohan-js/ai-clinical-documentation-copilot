'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api, { ProcessingResult } from '@/lib/api';
import TranscriptionView from '@/components/TranscriptionView';
import EntitiesView from '@/components/EntitiesView';
import SoapNotes from '@/components/SoapNotes';
import TaskList from '@/components/TaskList';

export default function ResultsPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.sessionId as string;

    const [result, setResult] = useState<ProcessingResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchResults() {
            try {
                const data = await api.getProcessingResult(sessionId);
                setResult(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load results');
            } finally {
                setLoading(false);
            }
        }

        if (sessionId) {
            fetchResults();
        }
    }, [sessionId]);

    if (loading) {
        return (
            <div className="container">
                <div style={{ textAlign: 'center', padding: '4rem' }}>
                    <div className="animate-spin" style={{ width: 48, height: 48, margin: '0 auto 1rem' }}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--primary-400)" strokeWidth="2">
                            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                        </svg>
                    </div>
                    <h2>Loading results...</h2>
                </div>
            </div>
        );
    }

    if (error || !result) {
        return (
            <div className="container">
                <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
                    <div style={{
                        width: 64,
                        height: 64,
                        margin: '0 auto 1rem',
                        borderRadius: '50%',
                        background: 'rgba(239, 68, 68, 0.2)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--error)" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="15" y1="9" x2="9" y2="15" />
                            <line x1="9" y1="9" x2="15" y2="15" />
                        </svg>
                    </div>
                    <h2 style={{ marginBottom: '0.5rem' }}>Failed to Load Results</h2>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                        {error || 'Session not found'}
                    </p>
                    <button className="btn btn-primary" onClick={() => router.push('/')}>
                        Back to Upload
                    </button>
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
                    <h1 style={{ marginBottom: '0.5rem' }}>Clinical Documentation</h1>
                    <p style={{ color: 'var(--text-muted)' }}>Session: {sessionId}</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        className="btn btn-secondary"
                        onClick={() => router.push('/')}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                        </svg>
                        New Session
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            // Export as JSON
                            const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `clinical-doc-${sessionId}.json`;
                            a.click();
                            URL.revokeObjectURL(url);
                        }}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="7 10 12 15 17 10" />
                            <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                        Export
                    </button>
                </div>
            </div>

            {/* Status indicator */}
            {result.status !== 'completed' && (
                <div className="card" style={{
                    marginBottom: '2rem',
                    borderColor: result.status === 'failed' ? 'var(--error)' : 'var(--warning)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            background: result.status === 'failed' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            {result.status === 'failed' ? '❌' : '⏳'}
                        </div>
                        <div>
                            <h3 style={{ color: result.status === 'failed' ? 'var(--error)' : 'var(--warning)' }}>
                                {result.status === 'failed' ? 'Processing Failed' : 'Processing in Progress'}
                            </h3>
                            <p style={{ color: 'var(--text-muted)' }}>
                                {result.error || 'Please wait for processing to complete'}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Results sections */}
            <div style={{ display: 'grid', gap: '2rem' }}>
                {/* Transcription */}
                {result.transcription && (
                    <div className="animate-slide-in">
                        <TranscriptionView transcription={result.transcription} />
                    </div>
                )}

                {/* Extracted Entities */}
                {result.extracted_entities && (
                    <div className="animate-slide-in" style={{ animationDelay: '100ms' }}>
                        <EntitiesView entities={result.extracted_entities} />
                    </div>
                )}

                {/* SOAP Notes */}
                {result.clinical_summary?.soap_notes && (
                    <div className="animate-slide-in" style={{ animationDelay: '200ms' }}>
                        <SoapNotes
                            soapNotes={result.clinical_summary.soap_notes}
                            narrative={result.clinical_summary.narrative}
                        />
                    </div>
                )}

                {/* Tasks */}
                {result.clinical_summary?.tasks && (
                    <div className="animate-slide-in" style={{ animationDelay: '300ms' }}>
                        <TaskList tasks={result.clinical_summary.tasks} />
                    </div>
                )}

                {/* RAG Context */}
                {result.clinical_summary?.rag_context_used && result.clinical_summary.rag_context_used.length > 0 && (
                    <div className="card animate-slide-in" style={{ animationDelay: '400ms' }}>
                        <div className="section-title">
                            <div className="section-title-icon" style={{ background: 'rgba(20, 184, 166, 0.2)' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-teal)" strokeWidth="2">
                                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                                </svg>
                            </div>
                            <h2>Clinical Guidelines Used</h2>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {result.clinical_summary.rag_context_used.map((context, index) => (
                                <span key={index} className="entity-tag" style={{ borderColor: 'var(--accent-teal)' }}>
                                    📚 {context}
                                </span>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Processing time */}
            {result.processing_time_seconds && (
                <p style={{
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    marginTop: '2rem',
                    fontSize: '0.875rem'
                }}>
                    Processing completed in {result.processing_time_seconds.toFixed(1)} seconds
                </p>
            )}
        </div>
    );
}
