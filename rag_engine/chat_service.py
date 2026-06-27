import os
import yaml
import json
from indexing.retriever_orchestrator import RetrieverOrchestrator
from .prompt_builder import PromptBuilder
from .guardrails import Guardrails
from .citation_checker import CitationChecker
from .llm_client import OllamaClient

class ChatService:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.settings = yaml.safe_load(f)
        except Exception:
            self.settings = {}
            
        self.retriever = RetrieverOrchestrator()
        # Initialize DB if not done yet
        self.retriever.load_or_build_index()
        
        self.prompt_builder = PromptBuilder()
        self.guardrails = Guardrails(self.settings)
        self.citation_checker = CitationChecker()
        
        llm_cfg = self.settings.get("llm", {})
        self.llm_client = OllamaClient(
            base_url=llm_cfg.get("ollama_url", "http://localhost:11434"),
            model=llm_cfg.get("default_model", "qwen2.5:3b")
        )
        self.temperature = llm_cfg.get("temperature", 0.1)

    async def get_chat_response_stream(self, query: str):
        """Pipeline RAG hoàn chỉnh (Streaming)."""
        # 1. Retrieval
        docs = self.retriever.search(query)
        
        # Format sources to send to frontend immediately
        sources_payload = []
        for d in docs:
            sources_payload.append({
                "id": d["id"],
                "title": d["title"],
                "section": d["section_title"],
                "url": d["url"],
                "source": d["source"]
            })
            
        # Gửi sources trước
        yield f"data: {json.dumps({'sources': sources_payload}, ensure_ascii=False)}\n\n"
        
        # 2. Guardrails (Abstain)
        if self.guardrails.should_abstain(docs):
            abstain_msg = self.guardrails.get_abstention_message()
            yield f"data: {json.dumps({'delta': abstain_msg}, ensure_ascii=False)}\n\n"
            return
            
        # 3. Prompting
        messages = self.prompt_builder.build_prompt(query, docs)
        
        # 4. Generation (Stream)
        full_response = ""
        async for chunk in self.llm_client.generate_stream(messages, self.temperature):
            full_response += chunk
            yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
            
        # 5. Citation validation (chạy ngầm sau khi stream xong, hoặc có thể gửi update cuối)
        # Trong streaming thì người dùng đã thấy text, ta không thể thu hồi.
        # Nhưng ta có thể dùng CitationChecker để log.
        val_result = self.citation_checker.validate_citations(full_response, docs)
        if val_result["has_hallucination"]:
            # Có thể lưu log cảnh báo
            pass

    async def get_chat_response_sync(self, query: str) -> dict:
        """Pipeline RAG hoàn chỉnh (Sync)."""
        # 1. Retrieval
        docs = self.retriever.search(query)
        
        # 2. Guardrails (Abstain)
        if self.guardrails.should_abstain(docs):
            return {
                "message": self.guardrails.get_abstention_message(),
                "sources": [],
                "warning": "Hệ thống từ chối trả lời do thiếu thông tin."
            }
            
        # 3. Prompting
        messages = self.prompt_builder.build_prompt(query, docs)
        
        # 4. Generation
        response_text = await self.llm_client.generate(messages, self.temperature)
        
        # 5. Citation validation
        val_result = self.citation_checker.validate_citations(response_text, docs)
        
        # 6. Thêm Disclaimer
        disclaimer = "\n\n*Lưu ý: LungCare AI chỉ cung cấp thông tin tham khảo. Vui lòng tham vấn bác sĩ để có chỉ định y khoa chính xác.*"
        final_text = val_result["clean_text"] + disclaimer
        
        return {
            "message": final_text,
            "sources": val_result["used_sources"] if val_result["used_sources"] else docs,
            "hallucination_detected": val_result["has_hallucination"]
        }
