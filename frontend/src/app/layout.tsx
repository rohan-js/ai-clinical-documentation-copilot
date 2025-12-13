import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'AI Clinical Documentation Copilot',
    description: 'AI-powered clinical documentation assistant for audiologists and clinicians',
    keywords: ['clinical documentation', 'AI', 'audiology', 'healthcare', 'transcription'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com" />
                <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                <link
                    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body>
                <nav className="nav">
                    <a href="/" className="nav-brand">
                        <div className="nav-brand-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 2a10 10 0 0 1 10 10c0 5.523-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z" />
                                <path d="M12 6v6l4 2" />
                            </svg>
                        </div>
                        <span>Clinical Doc AI</span>
                    </a>
                    <div className="nav-links">
                        <a href="/" className="nav-link">Upload</a>
                        <a href="/sessions" className="nav-link">Sessions</a>
                    </div>
                </nav>
                <main>{children}</main>
            </body>
        </html>
    );
}
