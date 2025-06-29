"""
Tutor Antonina Agent.
Agent edukacyjny pomagający w tworzeniu skutecznych promptów.
"""

import logging
from typing import Dict, List, Optional, Any
from backend.core.llm_providers.provider_factory import provider_factory as llm_factory
from backend.agents.base_agent import BaseAgent, AgentConfig, AgentContext, AgentResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Jesteś Antoniną – doświadczoną trenerką promptów. Pomagaj uczennicy tworzyć pełne, skuteczne prompty, uwzględniając te 6 elementów:

1. **Kontekst** - tło sytuacji, cel i okoliczności
2. **Instrukcja** - konkretne zadanie do wykonania
3. **Ograniczenia** - co NIE robić, ograniczenia techniczne
4. **Format odpowiedzi** - jak ma wyglądać odpowiedź
5. **Przykłady** - wzorce lub przykłady oczekiwanych rezultatów
6. **System prompt** - rola i styl komunikacji AI

**Zasady działania:**
- Jeśli brakuje któregoś z 6 elementów, zadaj JEDNO pytanie doprecyzowujące ten konkretny element
- Pytanie powinno być konkretne i prowadzić do uzupełnienia brakującego elementu
- Gdy wszystkie 6 elementów są obecne, rozpocznij odpowiedź od "Sugestia:" i podaj zwięzłą sugestię ulepszenia
- Następnie podaj "Ulepszony prompt:" i zoptymalizowaną wersję prompta
- Bądź przyjazna, ale profesjonalna - jak doświadczona nauczycielka

**Przykład pytania:** "W jakim kontekście chcesz użyć tego prompta? Czy to zadanie szkolne, praca, czy coś innego?"

**Przykład odpowiedzi z sugestią:**
Sugestia: Twój prompt jest dobry, ale dodaj konkretny format odpowiedzi.

Ulepszony prompt: [zoptymalizowana wersja]
"""


class TutorAntonina(BaseAgent):
    """Agent edukacyjny pomagający w tworzeniu skutecznych promptów."""
    
    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None):
        config = AgentConfig(
            agent_type="tutor_antonina",
            name="Tutor Antonina",
            description="Edukacyjny agent pomagający w tworzeniu skutecznych promptów",
            priority=2,
            max_concurrent_requests=5,
            timeout_seconds=45
        )
        super().__init__(config)
        self.model = model
        self.provider = provider
    
    async def guide(self, last_prompt: str, chat_history: List[Dict[str, str]]) -> Dict[str, Optional[str]]:
        """
        Przewodnik po tworzeniu promptów.
        
        Args:
            last_prompt: Ostatni prompt użytkownika
            chat_history: Historia rozmowy
            
        Returns:
            Dict z pytaniem lub feedbackiem
        """
        try:
            # Przygotuj wiadomości dla LLM
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Przeanalizuj ten prompt i pomóż mi go ulepszyć:\n\n{last_prompt}"}
            ]
            
            # Dodaj kontekst z historii jeśli istnieje
            if chat_history:
                context = "\n\nKontekst z poprzednich wiadomości:\n"
                for msg in chat_history[-3:]:  # Ostatnie 3 wiadomości
                    context += f"- {msg['role']}: {msg['content'][:100]}...\n"
                messages[1]["content"] += context
            
            # Wybierz provider
            if self.provider:
                provider_type = None
                for pt in llm_factory.get_available_providers():
                    if pt.value == self.provider:
                        provider_type = pt
                        break
                
                if not provider_type:
                    logger.warning(f"Provider {self.provider} not available, using fallback")
                    result = await llm_factory.chat_with_fallback(
                        messages=messages,
                        model=self.model,
                        temperature=0.2,
                        max_tokens=400
                    )
                else:
                    provider = llm_factory.get_provider(provider_type)
                    result = await provider.chat(
                        messages=messages,
                        model=self.model,
                        temperature=0.2,
                        max_tokens=400
                    )
            else:
                result = await llm_factory.chat_with_fallback(
                    messages=messages,
                    model=self.model,
                    temperature=0.2,
                    max_tokens=400
                )
            
            # Handle different response formats
            if isinstance(result, str):
                content = result.strip()
            elif isinstance(result, dict):
                if "text" in result:
                    content = result["text"].strip()
                elif "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                else:
                    content = str(result).strip()
            else:
                content = str(result).strip()
            
            # Analizuj odpowiedź
            if content.startswith("Sugestia:"):
                # Prompt jest kompletny - zwróć feedback
                parts = content.split("Ulepszony prompt:")
                suggestion = parts[0].replace("Sugestia:", "").strip()
                improved = parts[1].strip() if len(parts) > 1 else ""
                
                feedback = f"{suggestion}\n\nUlepszony prompt:\n{improved}"
                return {"question": None, "feedback": feedback}
            else:
                # Brakuje elementów - zwróć pytanie
                return {"question": content, "feedback": None}
                
        except Exception as e:
            logger.error(f"Tutor guide error: {e}")
            return {
                "question": "Przepraszam, wystąpił błąd. Spróbuj ponownie sformułować swój prompt.",
                "feedback": None
            }
    
    async def process_query(
        self, 
        query: str, 
        context: Optional[AgentContext] = None,
        **kwargs: Any
    ) -> AgentResponse:
        """
        Przetwarzanie zapytania przez tutora.
        
        Args:
            query: Prompt do analizy
            context: Kontekst agenta
            **kwargs: Dodatkowe parametry
            
        Returns:
            Odpowiedź agenta
        """
        start_time = self._get_current_time()
        
        try:
            # Pobierz historię z kontekstu jeśli dostępna
            chat_history = context.metadata.get("chat_history", []) if context else []
            
            # Przewodnik po promptach
            guide_result = await self.guide(query, chat_history)
            
            # Przygotuj odpowiedź
            if guide_result["question"]:
                content = f"🤔 **Pytanie od Tutora Antoniny:**\n\n{guide_result['question']}"
            else:
                content = f"✅ **Sugestia od Tutora Antoniny:**\n\n{guide_result['feedback']}"
            
            processing_time = self._get_current_time() - start_time
            
            return AgentResponse(
                success=True,
                content=content,
                agent_type=self.config.agent_type,
                provider_used=self.provider,
                processing_time=processing_time,
                metadata={
                    "tutor_question": guide_result["question"],
                    "tutor_feedback": guide_result["feedback"]
                }
            )
            
        except Exception as e:
            logger.error(f"Tutor process_query error: {e}")
            self.error_count += 1
            self.last_error = str(e)
            
            return AgentResponse(
                success=False,
                content=f"Przepraszam, wystąpił błąd podczas analizy prompta: {str(e)}",
                agent_type=self.config.agent_type,
                processing_time=self._get_current_time() - start_time
            )
    
    def _get_current_time(self) -> float:
        """Pobierz aktualny czas."""
        import time
        return time.time() 