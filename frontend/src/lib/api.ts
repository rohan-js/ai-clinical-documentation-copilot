/**
 * API client for communicating with the backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface UploadResponse {
    success: boolean;
    session_id: string;
    file_type: string;
    filename: string;
    file_path: string;
    message: string;
}

export interface ProcessingStatus {
    session_id: string;
    status: string;
    progress: number;
    current_step: string;
    message?: string;
}

export interface TranscriptionSegment {
    start: number;
    end: number;
    text: string;
}

export interface TranscriptionResult {
    success: boolean;
    text: string;
    segments: TranscriptionSegment[];
    language?: string;
    duration?: number;
    error?: string;
}

export interface ExtractedEntities {
    symptoms: string[];
    patient_history: string[];
    clinician_observations: string[];
    assessments: string[];
    recommendations: string[];
    medications: string[];
    vital_signs: Record<string, string>;
    audiological_findings: string[];
}

export interface SOAPNotes {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
}

export interface WorkflowTask {
    id: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high' | 'urgent';
    category: string;
    due_date?: string;
    completed: boolean;
}

export interface ClinicalSummary {
    narrative: string;
    soap_notes: SOAPNotes;
    tasks: WorkflowTask[];
    rag_context_used: string[];
}

export interface ProcessingResult {
    success: boolean;
    session_id: string;
    status: string;
    transcription?: TranscriptionResult;
    extracted_entities?: ExtractedEntities;
    clinical_summary?: ClinicalSummary;
    processing_time_seconds?: number;
    error?: string;
}

export interface SessionListItem {
    id: string;
    created_at: string;
    status: string;
    has_audio: boolean;
    has_notes: boolean;
    preview?: string;
}

export interface SessionList {
    sessions: SessionListItem[];
    total: number;
}

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...options.headers,
                },
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return response.json();
        } catch (error) {
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('Cannot connect to server. Please ensure the backend is running.');
            }
            throw error;
        }
    }

    // Upload endpoints
    async uploadAudio(file: File, sessionId?: string): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        if (sessionId) {
            formData.append('session_id', sessionId);
        }

        return this.request<UploadResponse>('/api/upload/audio', {
            method: 'POST',
            body: formData,
        });
    }

    async uploadNotes(file: File, sessionId?: string): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);
        if (sessionId) {
            formData.append('session_id', sessionId);
        }

        return this.request<UploadResponse>('/api/upload/notes', {
            method: 'POST',
            body: formData,
        });
    }

    // Processing endpoints
    async startProcessing(sessionId: string): Promise<ProcessingStatus> {
        return this.request<ProcessingStatus>(`/api/process/${sessionId}`, {
            method: 'POST',
        });
    }

    async getProcessingStatus(sessionId: string): Promise<ProcessingStatus> {
        return this.request<ProcessingStatus>(`/api/process/${sessionId}/status`);
    }

    async getProcessingResult(sessionId: string): Promise<ProcessingResult> {
        return this.request<ProcessingResult>(`/api/process/${sessionId}/result`);
    }

    // Session endpoints
    async listSessions(skip = 0, limit = 20): Promise<SessionList> {
        return this.request<SessionList>(`/api/sessions?skip=${skip}&limit=${limit}`);
    }

    async getSession(sessionId: string): Promise<ProcessingResult> {
        return this.request<ProcessingResult>(`/api/sessions/${sessionId}`);
    }

    async deleteSession(sessionId: string): Promise<{ success: boolean }> {
        return this.request<{ success: boolean }>(`/api/sessions/${sessionId}`, {
            method: 'DELETE',
        });
    }

    async createSession(): Promise<{ success: boolean; session_id: string }> {
        return this.request<{ success: boolean; session_id: string }>('/api/sessions/create', {
            method: 'POST',
        });
    }

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health');
    }
}

export const api = new ApiClient();
export default api;
