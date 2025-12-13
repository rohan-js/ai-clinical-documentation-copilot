'use client';

import React from 'react';
import { ExtractedEntities } from '@/lib/api';

interface EntitiesViewProps {
    entities: ExtractedEntities;
}

const ENTITY_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
    symptoms: { label: 'Symptoms', color: '#f43f5e', icon: '🩺' },
    patient_history: { label: 'Patient History', color: '#8b5cf6', icon: '📋' },
    clinician_observations: { label: 'Clinician Observations', color: '#0d7a9c', icon: '👁️' },
    assessments: { label: 'Assessments', color: '#f59e0b', icon: '📊' },
    recommendations: { label: 'Recommendations', color: '#10b981', icon: '💡' },
    medications: { label: 'Medications', color: '#3b82f6', icon: '💊' },
    audiological_findings: { label: 'Audiological Findings', color: '#14b8a6', icon: '👂' },
};

export default function EntitiesView({ entities }: EntitiesViewProps) {
    const entityEntries = Object.entries(entities).filter(([key, value]) => {
        if (key === 'vital_signs') {
            return value && Object.keys(value).length > 0;
        }
        return Array.isArray(value) && value.length > 0;
    });

    if (entityEntries.length === 0) {
        return (
            <div className="card">
                <div className="section-title">
                    <div className="section-title-icon" style={{ background: 'rgba(139, 92, 246, 0.2)' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-violet)" strokeWidth="2">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="12" y1="16" x2="12" y2="12" />
                            <line x1="12" y1="8" x2="12.01" y2="8" />
                        </svg>
                    </div>
                    <h2>Extracted Entities</h2>
                </div>
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                    No clinical entities were extracted from the text.
                </p>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon" style={{ background: 'rgba(139, 92, 246, 0.2)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-violet)" strokeWidth="2">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                        <line x1="10" y1="9" x2="8" y2="9" />
                    </svg>
                </div>
                <h2>Extracted Entities</h2>
            </div>

            <div style={{ display: 'grid', gap: '1.5rem' }}>
                {entityEntries.map(([key, value]) => {
                    if (key === 'vital_signs') {
                        const vitals = value as Record<string, string>;
                        return (
                            <div key={key}>
                                <h4 style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    marginBottom: '0.75rem',
                                    color: 'var(--text-secondary)',
                                    fontSize: '0.875rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.05em'
                                }}>
                                    <span>❤️</span>
                                    Vital Signs
                                </h4>
                                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                    {Object.entries(vitals).map(([vitalKey, vitalValue]) => (
                                        <span
                                            key={vitalKey}
                                            className="entity-tag"
                                            style={{ borderColor: '#ef4444' }}
                                        >
                                            <strong>{vitalKey}:</strong> {vitalValue}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        );
                    }

                    const config = ENTITY_CONFIG[key];
                    if (!config) return null;

                    const items = value as string[];

                    return (
                        <div key={key}>
                            <h4 style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                marginBottom: '0.75rem',
                                color: 'var(--text-secondary)',
                                fontSize: '0.875rem',
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em'
                            }}>
                                <span>{config.icon}</span>
                                {config.label}
                                <span style={{
                                    background: 'var(--bg-tertiary)',
                                    padding: '0.125rem 0.5rem',
                                    borderRadius: 'var(--radius-full)',
                                    fontSize: '0.75rem',
                                    color: 'var(--text-muted)'
                                }}>
                                    {items.length}
                                </span>
                            </h4>
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                {items.map((item, index) => (
                                    <span
                                        key={index}
                                        className="entity-tag"
                                        style={{
                                            borderColor: config.color,
                                            background: `${config.color}15`
                                        }}
                                    >
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
