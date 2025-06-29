import React from 'react';
import { render, screen } from '@testing-library/react';
import { TutorHints } from './TutorHints';

describe('TutorHints', () => {
  it('renders nothing when no props are provided', () => {
    const { container } = render(<TutorHints />);
    expect(container.firstChild).toBeNull();
  });

  it('renders question when provided', () => {
    const question = 'W jakim kontekście chcesz użyć tego prompta?';
    render(<TutorHints question={question} />);
    
    expect(screen.getByText('🤔 Pytanie od Tutora Antoniny:')).toBeInTheDocument();
    expect(screen.getByText(question)).toBeInTheDocument();
  });

  it('renders feedback when provided', () => {
    const feedback = 'Sugestia: Twój prompt jest dobry.\n\nUlepszony prompt: [ulepszona wersja]';
    render(<TutorHints feedback={feedback} />);
    
    expect(screen.getByText('✅ Sugestia od Tutora Antoniny:')).toBeInTheDocument();
    expect(screen.getByText('Sugestia: Twój prompt jest dobry.')).toBeInTheDocument();
    expect(screen.getByText('Ulepszony prompt: [ulepszona wersja]')).toBeInTheDocument();
  });

  it('renders both question and feedback when both are provided', () => {
    const question = 'W jakim kontekście chcesz użyć tego prompta?';
    const feedback = 'Sugestia: Twój prompt jest dobry.';
    
    render(<TutorHints question={question} feedback={feedback} />);
    
    expect(screen.getByText('🤔 Pytanie od Tutora Antoniny:')).toBeInTheDocument();
    expect(screen.getByText(question)).toBeInTheDocument();
    expect(screen.getByText('✅ Sugestia od Tutora Antoniny:')).toBeInTheDocument();
    expect(screen.getByText('Sugestia: Twój prompt jest dobry.')).toBeInTheDocument();
  });

  it('renders educational information about the 6 elements', () => {
    render(<TutorHints question="Test question" />);
    
    expect(screen.getByText(/Tutor Antonina pomaga tworzyć skuteczne prompty z 6 kluczowymi elementami/)).toBeInTheDocument();
    expect(screen.getByText(/Kontekst, Instrukcja, Ograniczenia, Format, Przykłady, System prompt/)).toBeInTheDocument();
  });

  it('applies correct styling classes', () => {
    const { container } = render(<TutorHints question="Test question" />);
    
    const mainDiv = container.firstChild as HTMLElement;
    expect(mainDiv).toHaveClass('mt-4', 'p-4', 'bg-gradient-to-r', 'from-teen-pink-50', 'to-teen-purple-50');
  });
}); 