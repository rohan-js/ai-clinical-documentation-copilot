'use client';

import React, { useState } from 'react';
import { WorkflowTask } from '@/lib/api';

interface TaskListProps {
    tasks: WorkflowTask[];
    onTaskToggle?: (taskId: string, completed: boolean) => void;
}

const PRIORITY_CONFIG = {
    urgent: { label: 'Urgent', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.2)' },
    high: { label: 'High', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.2)' },
    medium: { label: 'Medium', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.2)' },
    low: { label: 'Low', color: '#10b981', bg: 'rgba(16, 185, 129, 0.2)' },
};

const CATEGORY_ICONS: Record<string, string> = {
    'follow-up': '📅',
    'testing': '🧪',
    'referral': '👨‍⚕️',
    'medication': '💊',
    'education': '📚',
    'review': '📋',
    'documentation': '📝',
    'default': '📌',
};

export default function TaskList({ tasks, onTaskToggle }: TaskListProps) {
    const [completedTasks, setCompletedTasks] = useState<Set<string>>(
        new Set(tasks.filter(t => t.completed).map(t => t.id))
    );

    const handleToggle = (taskId: string) => {
        const newCompleted = new Set(completedTasks);
        if (completedTasks.has(taskId)) {
            newCompleted.delete(taskId);
        } else {
            newCompleted.add(taskId);
        }
        setCompletedTasks(newCompleted);
        onTaskToggle?.(taskId, newCompleted.has(taskId));
    };

    if (!tasks || tasks.length === 0) {
        return (
            <div className="card">
                <div className="section-title">
                    <div className="section-title-icon" style={{ background: 'rgba(16, 185, 129, 0.2)' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" strokeWidth="2">
                            <path d="M9 11l3 3L22 4" />
                            <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                        </svg>
                    </div>
                    <h2>Follow-up Tasks</h2>
                </div>
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
                    No tasks have been generated.
                </p>
            </div>
        );
    }

    // Sort tasks by priority
    const sortedTasks = [...tasks].sort((a, b) => {
        const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
        return (priorityOrder[a.priority] || 3) - (priorityOrder[b.priority] || 3);
    });

    return (
        <div className="card">
            <div className="section-title">
                <div className="section-title-icon" style={{ background: 'rgba(16, 185, 129, 0.2)' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-emerald)" strokeWidth="2">
                        <path d="M9 11l3 3L22 4" />
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                    </svg>
                </div>
                <h2>Follow-up Tasks</h2>
                <span style={{
                    marginLeft: 'auto',
                    fontSize: '0.875rem',
                    color: 'var(--text-muted)'
                }}>
                    {completedTasks.size}/{tasks.length} completed
                </span>
            </div>

            <div style={{ display: 'grid', gap: '0.75rem' }}>
                {sortedTasks.map((task) => {
                    const isCompleted = completedTasks.has(task.id);
                    const priorityConfig = PRIORITY_CONFIG[task.priority] || PRIORITY_CONFIG.medium;
                    const categoryIcon = CATEGORY_ICONS[task.category] || CATEGORY_ICONS.default;

                    return (
                        <div
                            key={task.id}
                            className="task-item"
                            style={{
                                opacity: isCompleted ? 0.6 : 1,
                                textDecoration: isCompleted ? 'line-through' : 'none',
                            }}
                        >
                            <button
                                className={`task-checkbox ${isCompleted ? 'checked' : ''}`}
                                onClick={() => handleToggle(task.id)}
                                aria-label={isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
                            >
                                {isCompleted && (
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                                        <polyline points="20 6 9 17 4 12" />
                                    </svg>
                                )}
                            </button>

                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                                    <span>{categoryIcon}</span>
                                    <h4 style={{
                                        color: 'var(--text-primary)',
                                        fontWeight: 500,
                                        fontSize: '0.9375rem'
                                    }}>
                                        {task.title}
                                    </h4>
                                    <span
                                        className={`task-priority ${task.priority}`}
                                        style={{
                                            background: priorityConfig.bg,
                                            color: priorityConfig.color
                                        }}
                                    >
                                        {priorityConfig.label}
                                    </span>
                                </div>
                                <p style={{
                                    color: 'var(--text-muted)',
                                    fontSize: '0.875rem',
                                    marginLeft: '1.5rem'
                                }}>
                                    {task.description}
                                </p>
                                {task.due_date && (
                                    <p style={{
                                        color: 'var(--text-muted)',
                                        fontSize: '0.75rem',
                                        marginLeft: '1.5rem',
                                        marginTop: '0.25rem'
                                    }}>
                                        📆 {task.due_date}
                                    </p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
