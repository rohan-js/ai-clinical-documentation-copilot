'use client';

import React, { useCallback, useState } from 'react';

interface NotesUploaderProps {
    file: File | null;
    onFileChange: (file: File | null) => void;
    disabled?: boolean;
}

export default function NotesUploader({ file, onFileChange, disabled }: NotesUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) {
            setIsDragging(true);
        }
    }, [disabled]);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        if (disabled) return;

        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && isValidNotesFile(droppedFile)) {
            onFileChange(droppedFile);
        }
    }, [disabled, onFileChange]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile && isValidNotesFile(selectedFile)) {
            onFileChange(selectedFile);
        }
    }, [onFileChange]);

    const isValidNotesFile = (file: File): boolean => {
        const validTypes = ['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        const validExtensions = ['.txt', '.pdf', '.doc', '.docx'];
        const extension = '.' + file.name.split('.').pop()?.toLowerCase();
        return validTypes.includes(file.type) || validExtensions.includes(extension);
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const getFileIcon = (filename: string) => {
        const ext = filename.split('.').pop()?.toLowerCase();
        if (ext === 'pdf') {
            return (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-rose)" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
            );
        }
        return (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-teal)" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
            </svg>
        );
    };

    const removeFile = useCallback(() => {
        onFileChange(null);
    }, [onFileChange]);

    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon" style={{ background: 'rgba(20, 184, 166, 0.2)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-teal)" strokeWidth="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                    </svg>
                </div>
                <h2>Clinical Notes</h2>
            </div>

            {!file ? (
                <div
                    className={`upload-zone ${isDragging ? 'dragging' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => !disabled && document.getElementById('notes-input')?.click()}
                >
                    <input
                        id="notes-input"
                        type="file"
                        accept=".txt,.pdf,.doc,.docx"
                        onChange={handleFileSelect}
                        disabled={disabled}
                        style={{ display: 'none' }}
                    />

                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <div style={{
                            width: 64,
                            height: 64,
                            margin: '0 auto 1rem',
                            borderRadius: '50%',
                            background: 'rgba(20, 184, 166, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--accent-teal)" strokeWidth="1.5">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                                <polyline points="14 2 14 8 20 8" />
                            </svg>
                        </div>

                        <h3 style={{ marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                            Drop notes file here
                        </h3>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                            or click to browse
                        </p>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Supports TXT, PDF, DOC, DOCX • Max 10MB
                        </p>
                    </div>
                </div>
            ) : (
                <div className="upload-zone has-file" style={{ cursor: 'default', borderColor: 'var(--accent-teal)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{
                            width: 48,
                            height: 48,
                            borderRadius: 'var(--radius-lg)',
                            background: 'rgba(20, 184, 166, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            {getFileIcon(file.name)}
                        </div>

                        <div style={{ flex: 1, textAlign: 'left' }}>
                            <p style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                                {file.name}
                            </p>
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                {formatFileSize(file.size)}
                            </p>
                        </div>

                        <button
                            onClick={(e) => { e.stopPropagation(); removeFile(); }}
                            className="btn btn-ghost"
                            disabled={disabled}
                            style={{ padding: '0.5rem' }}
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <line x1="18" y1="6" x2="6" y2="18" />
                                <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
