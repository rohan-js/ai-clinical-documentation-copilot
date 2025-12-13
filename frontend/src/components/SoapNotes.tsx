'use client';

import React from 'react';
import { SOAPNotes } from '@/lib/api';

interface SoapNotesProps {
    soapNotes: SOAPNotes;
    narrative?: string;
}

const SOAP_SECTIONS = [
    {
        key: 'subjective',
        label: 'Subjective',
        description: 'Patient\'s perspective and reported symptoms',
        color: '#8b5cf6',
        icon: '💬',
    },
    {
        key: 'objective',
        label: 'Objective',
        description: 'Clinical observations and test results',
        color: '#14b8a6',
        icon: '🔬',
    },
    {
        key: 'assessment',
        label: 'Assessment',
        description: 'Clinical diagnosis and interpretation',
        color: '#f59e0b',
        icon: '📋',
    },
    {
        key: 'plan',
        label: 'Plan',
        description: 'Treatment plan and next steps',
        color: '#10b981',
        icon: '🎯',
    },
];

export default function SoapNotesComponent({ soapNotes, narrative }: SoapNotesProps) {
    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon" style={{ background: 'rgba(245, 158, 11, 0.2)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-amber)" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                </div>
                <h2>SOAP Notes</h2>
            </div>

            {/* Clinical Narrative */}
            {narrative && (
                <div style={{
                    background: 'linear-gradient(135deg, rgba(13, 122, 156, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
                    padding: '1.5rem',
                    borderRadius: 'var(--radius-lg)',
                    marginBottom: '1.5rem',
                    border: '1px solid var(--border-subtle)'
                }}>
                    <h4 style={{
                        color: 'var(--text-secondary)',
                        marginBottom: '0.75rem',
                        fontSize: '0.875rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                    }}>
                        📝 Clinical Narrative
                    </h4>
                    <p style={{
                        color: 'var(--text-primary)',
                        lineHeight: 1.8,
                        whiteSpace: 'pre-wrap'
                    }}>
                        {narrative}
                    </p>
                </div>
            )}

            {/* SOAP Sections */}
            <div className="soap-container">
                {SOAP_SECTIONS.map((section) => {
                    const content = soapNotes[section.key as keyof SOAPNotes];

                    return (
                        <div
                            key={section.key}
                            className={`soap-section ${section.key}`}
                            style={{ borderLeftColor: section.color }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                                <span>{section.icon}</span>
                                <h4 style={{ color: section.color, fontWeight: 600 }}>{section.label}</h4>
                                <span style={{
                                    fontSize: '0.75rem',
                                    color: 'var(--text-muted)',
                                    marginLeft: 'auto'
                                }}>
                                    {section.description}
                                </span>
                            </div>
                            <p style={{
                                color: 'var(--text-primary)',
                                lineHeight: 1.7,
                                whiteSpace: 'pre-wrap'
                            }}>
                                {content || 'No information available'}
                            </p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
