'use client';

import React, { useCallback, useState } from 'react';

interface AudioUploaderProps {
    file: File | null;
    onFileChange: (file: File | null) => void;
    disabled?: boolean;
}

export default function AudioUploader({ file, onFileChange, disabled }: AudioUploaderProps) {
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
        if (droppedFile && isValidAudioFile(droppedFile)) {
            onFileChange(droppedFile);
        }
    }, [disabled, onFileChange]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile && isValidAudioFile(selectedFile)) {
            onFileChange(selectedFile);
        }
    }, [onFileChange]);

    const isValidAudioFile = (file: File): boolean => {
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/x-wav', 'audio/ogg', 'audio/flac', 'audio/x-m4a', 'audio/mp4'];
        const validExtensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac'];
        const extension = '.' + file.name.split('.').pop()?.toLowerCase();
        return validTypes.includes(file.type) || validExtensions.includes(extension);
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const removeFile = useCallback(() => {
        onFileChange(null);
    }, [onFileChange]);

    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="22" />
                    </svg>
                </div>
                <h2>Audio Recording</h2>
            </div>

            {!file ? (
                <div
                    className={`upload-zone ${isDragging ? 'dragging' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => !disabled && document.getElementById('audio-input')?.click()}
                >
                    <input
                        id="audio-input"
                        type="file"
                        accept=".mp3,.wav,.m4a,.ogg,.flac"
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
                            background: 'rgba(13, 122, 156, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--primary-400)" strokeWidth="1.5">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                <polyline points="17 8 12 3 7 8" />
                                <line x1="12" y1="3" x2="12" y2="15" />
                            </svg>
                        </div>

                        <h3 style={{ marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                            Drop audio file here
                        </h3>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
                            or click to browse
                        </p>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                            Supports MP3, WAV, M4A, OGG, FLAC • Max 50MB
                        </p>
                    </div>
                </div>
            ) : (
                <div className="upload-zone has-file" style={{ cursor: 'default' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{
                            width: 48,
                            height: 48,
                            borderRadius: 'var(--radius-lg)',
                            background: 'rgba(16, 185, 129, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2">
                                <path d="M9 18V5l12-2v13" />
                                <circle cx="6" cy="18" r="3" />
                                <circle cx="18" cy="16" r="3" />
                            </svg>
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
