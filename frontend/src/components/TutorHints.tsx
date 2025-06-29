import React from 'react';
import { Lightbulb, HelpCircle, CheckCircle } from 'lucide-react';

interface TutorHintsProps {
  question?: string;
  feedback?: string;
}

export const TutorHints: React.FC<TutorHintsProps> = ({ question, feedback }) => {
  if (!question && !feedback) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-gradient-to-r from-teen-pink-50 to-teen-purple-50 border border-teen-purple-200 rounded-lg">
      {question && (
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0 p-2 bg-teen-purple-100 rounded-lg">
            <HelpCircle className="w-5 h-5 text-teen-purple-600" />
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-teen-purple-800 mb-2">
              🤔 Pytanie od Tutora Antoniny:
            </h4>
            <p className="text-sm text-teen-purple-700 leading-relaxed">
              {question}
            </p>
          </div>
        </div>
      )}
      
      {feedback && (
        <div className="flex items-start space-x-3 mt-4">
          <div className="flex-shrink-0 p-2 bg-teen-mint-100 rounded-lg">
            <CheckCircle className="w-5 h-5 text-teen-mint-600" />
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-teen-mint-800 mb-2">
              ✅ Sugestia od Tutora Antoniny:
            </h4>
            <div className="text-sm text-teen-mint-700 leading-relaxed whitespace-pre-wrap">
              {feedback}
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-3 pt-3 border-t border-teen-purple-200">
        <div className="flex items-center text-xs text-teen-purple-600">
          <Lightbulb className="w-3 h-3 mr-1" />
          <span>
            Tutor Antonina pomaga tworzyć skuteczne prompty z 6 kluczowymi elementami: 
            Kontekst, Instrukcja, Ograniczenia, Format, Przykłady, System prompt
          </span>
        </div>
      </div>
    </div>
  );
}; 