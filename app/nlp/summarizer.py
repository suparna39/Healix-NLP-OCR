"""Medical text summarization using pretrained models."""

import logging
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SummarizerBase(ABC):
    """Base class for medical text summarization."""

    @abstractmethod
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Summarize medical text."""
        pass

    @abstractmethod
    def summarize_hierarchical(self, text: str, chunk_size: int = 500) -> str:
        """Hierarchically summarize long documents."""
        pass


class MedicalSummarizer(SummarizerBase):
    """Summarize medical text using transformers (FLAN-T5/BART)."""

    def __init__(self, model_name: str = "google/flan-t5-base"):
        """
        Initialize summarizer with lazy loading.

        Args:
            model_name: Hugging Face model identifier
        """
        self.model_name = model_name
        self.pipeline = None
        self.model = None
        self.tokenizer = None
        self._model_loaded = False
        # Don't load model on init - defer until first use

    def _load_model(self) -> None:
        """Lazy load summarization model on first use."""
        if self._model_loaded:
            return
        
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            logger.info(f"Lazy loading summarization model: {self.model_name}")
            # Load model and tokenizer directly instead of using pipeline
            # This works better with FLAN-T5 and avoids task compatibility issues
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.pipeline = True  # Flag indicating model is loaded
            self._model_loaded = True
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarization model: {e}")
            self.pipeline = None
            self.tokenizer = None
            self.model = None
            self._model_loaded = True  # Mark as attempted even if failed

    def summarize(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 50
    ) -> str:
        """
        Summarize text using pretrained model.

        Args:
            text: Medical text to summarize
            max_length: Maximum summary length
            min_length: Minimum summary length

        Returns:
            Summarized text
        """
        # Lazy load model on first use
        self._load_model()
        
        if not self.pipeline or not self.model or not self.tokenizer:
            logger.warning("Summarizer not loaded, returning truncated text")
            return self._fallback_summary(text, max_length)

        if not text or len(text) < 50:
            return text  # Too short to summarize

        try:
            # Truncate input if needed
            if len(text) > 1024:
                text = text[:1024]

            # Prepare input
            input_text = f"summarize: {text}"
            inputs = self.tokenizer(input_text, max_length=1024, truncation=True, return_tensors="pt")
            
            # Generate summary
            summary_ids = self.model.generate(
                inputs['input_ids'],
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                early_stopping=True
            )

            # Decode summary
            summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary_text

        except Exception as e:
            logger.warning(f"Summarization failed: {e}, using fallback")
            return self._fallback_summary(text, max_length)

    def summarize_hierarchical(
        self,
        text: str,
        chunk_size: int = 500,
        max_length: int = 150
    ) -> str:
        """
        Hierarchically summarize very long documents.

        1. Split text into chunks
        2. Summarize each chunk
        3. Combine summaries and summarize again

        Args:
            text: Medical text to summarize
            chunk_size: Characters per chunk
            max_length: Maximum summary length

        Returns:
            Final summary
        """
        if len(text) <= chunk_size:
            return self.summarize(text, max_length=max_length)

        logger.info(f"Performing hierarchical summarization (chunk_size={chunk_size})")

        # Split into chunks
        chunks = self._split_text(text, chunk_size)
        logger.debug(f"Split text into {len(chunks)} chunks")

        # Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            summary = self.summarize(chunk, max_length=100, min_length=30)
            chunk_summaries.append(summary)
            logger.debug(f"Summarized chunk {i+1}/{len(chunks)}")

        # Combine summaries
        combined = " ".join(chunk_summaries)

        # Final summarization
        final_summary = self.summarize(combined, max_length=max_length)

        return final_summary

    @staticmethod
    def _split_text(text: str, chunk_size: int) -> List[str]:
        """Split text into chunks."""
        chunks = []
        current_chunk = ""

        sentences = text.split(". ")
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence + ". "

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    @staticmethod
    def _fallback_summary(text: str, max_length: int) -> str:
        """Fallback summary method (extractive)."""
        if not text:
            return ""

        # Extract first few sentences
        sentences = text.split(". ")
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip()

    def generate_short_summary(self, text: str) -> str:
        """Generate brief clinical summary (1-2 sentences)."""
        return self.summarize(text, max_length=80, min_length=30)

    def generate_long_summary(self, text: str) -> str:
        """Generate comprehensive summary."""
        if len(text) > 1500:
            return self.summarize_hierarchical(text, chunk_size=500, max_length=200)
        else:
            return self.summarize(text, max_length=150, min_length=50)

    def generate_key_findings_summary(self, text: str) -> str:
        """Generate summary focused on key findings."""
        prompt = f"Summarize key clinical findings:\n{text}"
        return self.summarize(prompt, max_length=120, min_length=40)


class SimpleRuleSummarizer(SummarizerBase):
    """Fallback rule-based summarizer (no ML model)."""

    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Extract-based summarization."""
        sentences = text.split(". ")
        summary = ""

        for sentence in sentences:
            if len(summary) + len(sentence) < max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip() or text[:max_length]

    def summarize_hierarchical(self, text: str, chunk_size: int = 500) -> str:
        """Fallback hierarchical summarization."""
        return self.summarize(text, max_length=200, min_length=80)


def create_summarizer(model_name: Optional[str] = None) -> SummarizerBase:
    """Factory function to create appropriate summarizer.
    
    On Render free tier, defaults to rule-based summarizer to avoid memory exhaustion.
    Set SUMMARIZATION_MODEL=flan-t5-base to use transformer (requires more resources).
    """
    import os
    
    # Check if we're on Render (has RENDER env var)
    on_render = os.getenv("RENDER", "false").lower() == "true"
    
    if model_name and model_name != "default":
        try:
            logger.info(f"Attempting to load transformer model: {model_name}")
            return MedicalSummarizer(model_name)
        except Exception as e:
            logger.warning(f"Failed to load {model_name}, using fallback: {e}")
            return SimpleRuleSummarizer()
    
    # On Render, use lightweight rule-based by default
    if on_render:
        logger.info("Running on Render - using lightweight rule-based summarizer")
        return SimpleRuleSummarizer()
    
    # Locally, try to use transformer with fallback
    try:
        logger.info("Using default FLAN-T5 transformer summarizer")
        return MedicalSummarizer("google/flan-t5-base")
    except Exception as e:
        logger.warning(f"Failed to load default summarizer, using fallback: {e}")
        return SimpleRuleSummarizer()
