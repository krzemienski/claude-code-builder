"""Context management for handling large specifications with 150K+ tokens."""

import asyncio
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# import tiktoken  # Commented out for Python 3.13 compatibility
from pydantic import Field

from claude_code_builder.core.base_model import BaseModel
from claude_code_builder.core.enums import ChunkStrategy, MCPServer
from claude_code_builder.core.exceptions import ContextOverflowError, SpecificationError
from claude_code_builder.core.models import SpecChunk


class TokenCounter:
    """Utility for counting tokens in text."""

    def __init__(self, model: str = "cl100k_base") -> None:
        """Initialize the token counter."""
        # Simple approximation without tiktoken for Python 3.13 compatibility
        # Average English word is ~1.3 tokens, average character is ~0.25 tokens
        self.chars_per_token = 4

    def count(self, text: str) -> int:
        """Count tokens in text using approximation."""
        # Simple approximation: ~4 characters per token on average
        return len(text) // self.chars_per_token

    def truncate(self, text: str, max_tokens: int) -> str:
        """Truncate text to max tokens."""
        max_chars = max_tokens * self.chars_per_token
        if len(text) <= max_chars:
            return text
        # Truncate at word boundary
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.8:  # If we have a reasonable amount of text
            return truncated[:last_space]
        return truncated


class ChunkMetadata(BaseModel):
    """Metadata for a specification chunk."""

    chunk_id: str
    section_name: str
    subsection: Optional[str] = None
    token_count: int
    dependencies: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    priority: int = 1
    checksum: str = ""
    
    def __init__(self, **data: Any) -> None:
        """Initialize and compute checksum if not provided."""
        super().__init__(**data)
        if not self.checksum:
            content = f"{self.section_name}:{self.subsection}:{self.token_count}"
            self.checksum = hashlib.md5(content.encode()).hexdigest()


class SpecificationChunker:
    """Handles intelligent chunking of large specifications."""

    def __init__(
        self,
        max_chunk_tokens: int = 30000,
        overlap_tokens: int = 500,
        strategy: ChunkStrategy = ChunkStrategy.SEMANTIC,
    ) -> None:
        """Initialize the chunker."""
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.strategy = strategy
        self.token_counter = TokenCounter()

    async def chunk_specification(
        self, spec_content: str, spec_path: Path
    ) -> List[SpecChunk]:
        """Chunk a specification into manageable pieces."""
        if self.strategy == ChunkStrategy.SEMANTIC:
            return await self._semantic_chunking(spec_content, spec_path)
        elif self.strategy == ChunkStrategy.SLIDING_WINDOW:
            return await self._sliding_window_chunking(spec_content, spec_path)
        elif self.strategy == ChunkStrategy.SECTION_BASED:
            return await self._section_based_chunking(spec_content, spec_path)
        else:
            raise ValueError(f"Unknown chunking strategy: {self.strategy}")

    async def _semantic_chunking(
        self, content: str, spec_path: Path
    ) -> List[SpecChunk]:
        """Chunk based on semantic boundaries."""
        chunks: List[SpecChunk] = []
        
        # Split by common section markers
        section_markers = [
            "\n## ", "\n### ", "\n#### ",
            "\n---\n", "\n***\n", "\n___\n",
            "\n\n\n", "\n\nRequirements:", "\n\nSpecification:",
        ]
        
        sections = self._split_by_markers(content, section_markers)
        
        # Estimate total chunks
        total_tokens = self.token_counter.count(content)
        estimated_chunks = max(1, (total_tokens // self.max_chunk_tokens) + 1)
        
        current_chunk = ""
        current_tokens = 0
        chunk_index = 0
        
        for section in sections:
            section_tokens = self.token_counter.count(section)
            
            # If section alone exceeds max, split it further
            if section_tokens > self.max_chunk_tokens:
                if current_chunk:
                    # Save current chunk
                    chunks.append(
                        await self._create_spec_chunk(
                            current_chunk, chunk_index, spec_path, len(chunks), None, estimated_chunks
                        )
                    )
                    current_chunk = ""
                    current_tokens = 0
                    chunk_index += 1
                
                # Split large section
                sub_chunks = await self._split_large_section(
                    section, spec_path, chunk_index, None, estimated_chunks
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
                
            elif current_tokens + section_tokens > self.max_chunk_tokens:
                # Save current chunk and start new one
                chunks.append(
                    await self._create_spec_chunk(
                        current_chunk, chunk_index, spec_path, len(chunks), None, estimated_chunks
                    )
                )
                
                # Add overlap from end of previous chunk
                overlap = self._get_overlap_text(current_chunk)
                current_chunk = overlap + section
                current_tokens = self.token_counter.count(current_chunk)
                chunk_index += 1
                
            else:
                # Add to current chunk
                current_chunk += section
                current_tokens += section_tokens
        
        # Save final chunk
        if current_chunk.strip():
            chunks.append(
                await self._create_spec_chunk(
                    current_chunk, chunk_index, spec_path, len(chunks), None, estimated_chunks
                )
            )
        
        return chunks

    async def _sliding_window_chunking(
        self, content: str, spec_path: Path
    ) -> List[SpecChunk]:
        """Chunk using sliding window approach."""
        chunks: List[SpecChunk] = []
        lines = content.split('\n')
        
        # Estimate total chunks
        total_tokens = self.token_counter.count(content)
        estimated_chunks = max(1, (total_tokens // self.max_chunk_tokens) + 1)
        
        window_start = 0
        chunk_index = 0
        
        while window_start < len(lines):
            # Build chunk up to max tokens
            current_chunk_lines = []
            current_tokens = 0
            line_idx = window_start
            
            while line_idx < len(lines) and current_tokens < self.max_chunk_tokens:
                line = lines[line_idx]
                line_tokens = self.token_counter.count(line + '\n')
                
                if current_tokens + line_tokens > self.max_chunk_tokens:
                    break
                    
                current_chunk_lines.append(line)
                current_tokens += line_tokens
                line_idx += 1
            
            # Create chunk
            chunk_content = '\n'.join(current_chunk_lines)
            chunks.append(
                await self._create_spec_chunk(
                    chunk_content, chunk_index, spec_path, len(chunks), None, estimated_chunks
                )
            )
            
            # Calculate next window start with overlap
            overlap_lines = self._calculate_overlap_lines(
                current_chunk_lines, self.overlap_tokens
            )
            window_start = line_idx - len(overlap_lines)
            chunk_index += 1
        
        return chunks

    async def _section_based_chunking(
        self, content: str, spec_path: Path
    ) -> List[SpecChunk]:
        """Chunk based on document sections."""
        chunks: List[SpecChunk] = []
        
        # Parse document structure
        sections = self._parse_document_structure(content)
        total_sections = len(sections)
        
        for idx, section in enumerate(sections):
            # Check if section needs splitting
            section_tokens = self.token_counter.count(section['content'])
            
            if section_tokens <= self.max_chunk_tokens:
                # Create single chunk for section
                chunk = SpecChunk(
                    index=idx,
                    total_chunks=total_sections,
                    content=section['content'],
                    tokens=section_tokens,
                    sections=[section['name']] if section.get('name') else [],
                    cross_references=[],
                    summary=None,
                    metadata={
                        "chunk_id": f"section_{idx}",
                        "section_name": section['name'],
                        "subsection": section.get('subsection'),
                        "keywords": self._extract_keywords(section['content']),
                        "start_line": section['start_line'],
                        "end_line": section['end_line'],
                    },
                )
                chunks.append(chunk)
            else:
                # Split large section
                sub_chunks = await self._split_large_section(
                    section['content'], spec_path, idx, section['name'], total_sections
                )
                chunks.extend(sub_chunks)
        
        return chunks

    def _split_by_markers(self, content: str, markers: List[str]) -> List[str]:
        """Split content by markers while preserving markers."""
        sections = []
        current_section = ""
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check if line starts new section
            is_new_section = False
            for marker in markers:
                if marker.strip() and line.startswith(marker.strip()):
                    is_new_section = True
                    break
            
            if is_new_section and current_section:
                sections.append(current_section)
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        if current_section:
            sections.append(current_section)
        
        return sections

    async def _split_large_section(
        self,
        section: str,
        spec_path: Path,
        base_index: int,
        section_name: Optional[str] = None,
        total_chunks: int = 1,
    ) -> List[SpecChunk]:
        """Split a large section into smaller chunks."""
        chunks = []
        
        # Try paragraph-based splitting first
        paragraphs = section.split('\n\n')
        
        current_chunk = ""
        current_tokens = 0
        sub_index = 0
        
        for para in paragraphs:
            para_tokens = self.token_counter.count(para + '\n\n')
            
            if current_tokens + para_tokens > self.max_chunk_tokens:
                if current_chunk:
                    chunks.append(
                        await self._create_spec_chunk(
                            current_chunk,
                            f"{base_index}.{sub_index}",
                            spec_path,
                            0,
                            section_name,
                            total_chunks,
                        )
                    )
                    sub_index += 1
                
                # Start new chunk with overlap
                overlap = self._get_overlap_text(current_chunk)
                current_chunk = overlap + para + '\n\n'
                current_tokens = self.token_counter.count(current_chunk)
            else:
                current_chunk += para + '\n\n'
                current_tokens += para_tokens
        
        if current_chunk.strip():
            chunks.append(
                await self._create_spec_chunk(
                    current_chunk,
                    f"{base_index}.{sub_index}",
                    spec_path,
                    0,
                    section_name,
                    total_chunks,
                )
            )
        
        return chunks

    async def _create_spec_chunk(
        self,
        content: str,
        chunk_index: Any,
        spec_path: Path,
        position: int,
        section_name: Optional[str] = None,
        total_chunks: int = 1,
    ) -> SpecChunk:
        """Create a specification chunk."""
        # Count tokens
        tokens = self.token_counter.count(content)
        
        # Extract sections from content
        sections = []
        for line in content.split('\n'):
            if line.strip().startswith('#'):
                sections.append(line.strip())
        
        # Create metadata dictionary
        metadata = {
            "chunk_id": f"chunk_{chunk_index}",
            "section_name": section_name or self._extract_section_name(content),
            "keywords": self._extract_keywords(content),
            "priority": self._calculate_priority(content),
            "start_line": position * 100 + 1 if position > 0 else 1,
            "end_line": (position * 100 + 1 if position > 0 else 1) + len(content.split('\n')) - 1,
        }
        
        return SpecChunk(
            index=chunk_index if isinstance(chunk_index, int) else position,
            total_chunks=total_chunks,
            content=content,
            tokens=tokens,
            sections=sections[:5] if sections else [],  # Limit to first 5 sections
            cross_references=[],
            summary=None,
            metadata=metadata,
        )

    def _get_overlap_text(self, chunk: str) -> str:
        """Get overlap text from end of chunk."""
        lines = chunk.split('\n')
        overlap_lines = []
        current_tokens = 0
        
        # Work backwards to get overlap
        for line in reversed(lines):
            line_tokens = self.token_counter.count(line + '\n')
            if current_tokens + line_tokens > self.overlap_tokens:
                break
            overlap_lines.insert(0, line)
            current_tokens += line_tokens
        
        return '\n'.join(overlap_lines) + '\n' if overlap_lines else ""

    def _calculate_overlap_lines(
        self, lines: List[str], target_tokens: int
    ) -> List[str]:
        """Calculate lines needed for overlap tokens."""
        overlap_lines = []
        current_tokens = 0
        
        for line in reversed(lines):
            line_tokens = self.token_counter.count(line + '\n')
            if current_tokens + line_tokens > target_tokens:
                break
            overlap_lines.insert(0, line)
            current_tokens += line_tokens
        
        return overlap_lines

    def _parse_document_structure(self, content: str) -> List[Dict[str, Any]]:
        """Parse document structure into sections."""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            'name': 'Introduction',
            'content': '',
            'start_line': 1,
            'level': 0,
        }
        
        for i, line in enumerate(lines):
            # Detect headers
            if line.startswith('#'):
                # Save previous section
                if current_section['content'].strip():
                    current_section['end_line'] = i
                    sections.append(current_section)
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                name = line.lstrip('#').strip()
                
                current_section = {
                    'name': name,
                    'content': line + '\n',
                    'start_line': i + 1,
                    'level': level,
                }
            else:
                current_section['content'] += line + '\n'
        
        # Save final section
        if current_section['content'].strip():
            current_section['end_line'] = len(lines)
            sections.append(current_section)
        
        return sections

    def _extract_section_name(self, content: str) -> str:
        """Extract section name from content."""
        lines = content.strip().split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if line.startswith('#'):
                return line.lstrip('#').strip()
        return "Unnamed Section"

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction - in production would use NLP
        keywords = []
        
        # Common technical keywords to look for
        tech_keywords = [
            'api', 'database', 'authentication', 'authorization',
            'frontend', 'backend', 'microservice', 'deployment',
            'testing', 'performance', 'security', 'scalability',
            'integration', 'configuration', 'monitoring', 'logging',
        ]
        
        content_lower = content.lower()
        for keyword in tech_keywords:
            if keyword in content_lower:
                keywords.append(keyword)
        
        return keywords[:10]  # Limit to 10 keywords

    def _calculate_priority(self, content: str) -> int:
        """Calculate chunk priority based on content."""
        priority = 1
        
        # Higher priority for sections with key terms
        priority_terms = [
            'requirement', 'must', 'shall', 'critical',
            'api', 'interface', 'architecture', 'overview',
        ]
        
        content_lower = content.lower()
        for term in priority_terms:
            if term in content_lower:
                priority += 1
        
        return min(priority, 5)  # Max priority 5


class ContextManager:
    """Manages context for agent interactions."""

    def __init__(
        self,
        max_context_tokens: int = 150000,
        reserve_output_tokens: int = 4000,
        chunker: Optional[SpecificationChunker] = None,
    ) -> None:
        """Initialize the context manager."""
        self.max_context_tokens = max_context_tokens
        self.reserve_output_tokens = reserve_output_tokens
        self.effective_max_tokens = max_context_tokens - reserve_output_tokens
        self.chunker = chunker or SpecificationChunker()
        self.token_counter = TokenCounter()
        
        # Context state
        self.loaded_chunks: Dict[str, SpecChunk] = {}
        self.chunk_access_count: Dict[str, int] = defaultdict(int)
        self.last_access_time: Dict[str, datetime] = {}
        self.phase_contexts: Dict[str, List[str]] = defaultdict(list)

    async def load_specification(
        self, spec_path: Path, spec_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load and process a specification."""
        if spec_content is None:
            spec_content = spec_path.read_text()
        
        # Check total size
        total_tokens = self.token_counter.count(spec_content)
        
        if total_tokens <= self.effective_max_tokens:
            # Fits in single context
            chunk = SpecChunk(
                index=0,
                total_chunks=1,
                content=spec_content,
                tokens=total_tokens,
                sections=[],
                cross_references=[],
                summary=None,
                metadata={
                    "chunk_id": "full_spec",
                    "section_name": "Complete Specification",
                    "start_line": 1,
                    "end_line": len(spec_content.split('\n')),
                },
            )
            
            self.loaded_chunks["full_spec"] = chunk
            
            return {
                "strategy": "single_context",
                "total_tokens": total_tokens,
                "chunks": 1,
                "chunk_ids": ["full_spec"],
            }
        
        # Need to chunk
        chunks = await self.chunker.chunk_specification(spec_content, spec_path)
        
        # Store chunks
        for chunk in chunks:
            chunk_id = chunk.metadata.get("chunk_id", f"chunk_{chunk.index}")
            self.loaded_chunks[chunk_id] = chunk
        
        return {
            "strategy": str(self.chunker.strategy),
            "total_tokens": total_tokens,
            "chunks": len(chunks),
            "chunk_ids": [c.metadata.get("chunk_id", f"chunk_{c.index}") for c in chunks],
            "avg_chunk_tokens": total_tokens // len(chunks) if chunks else 0,
        }

    async def get_context_for_phase(
        self, phase_name: str, required_sections: Optional[List[str]] = None
    ) -> str:
        """Get optimized context for a specific phase."""
        context_parts = []
        current_tokens = 0
        
        # Add phase-specific header
        header = f"# Context for Phase: {phase_name}\n\n"
        context_parts.append(header)
        current_tokens += self.token_counter.count(header)
        
        # Get chunks relevant to phase
        relevant_chunks = await self._select_relevant_chunks(
            phase_name, required_sections
        )
        
        # Sort by priority and relevance
        relevant_chunks.sort(
            key=lambda c: (
                -c.metadata.get("priority", 0),
                -self.chunk_access_count.get(c.metadata.get("chunk_id", f"chunk_{c.index}"), 0),
            )
        )
        
        # Add chunks up to token limit
        for chunk in relevant_chunks:
            chunk_tokens = chunk.tokens
            
            if current_tokens + chunk_tokens > self.effective_max_tokens:
                # Try to add a summary instead
                summary = await self._create_chunk_summary(chunk)
                summary_tokens = self.token_counter.count(summary)
                
                if current_tokens + summary_tokens <= self.effective_max_tokens:
                    section_name = chunk.metadata.get("section_name", f"Section {chunk.index}")
                    context_parts.append(f"\n## Summary: {section_name}\n")
                    context_parts.append(summary)
                    current_tokens += summary_tokens
                break
            
            # Add full chunk
            section_name = chunk.metadata.get("section_name", f"Section {chunk.index}")
            context_parts.append(f"\n## {section_name}\n")
            context_parts.append(chunk.content)
            current_tokens += chunk_tokens
            
            # Update access tracking
            chunk_id = chunk.metadata.get("chunk_id", f"chunk_{chunk.index}")
            self.chunk_access_count[chunk_id] += 1
            self.last_access_time[chunk_id] = datetime.utcnow()
            self.phase_contexts[phase_name].append(chunk_id)
        
        return '\n'.join(context_parts)

    async def _select_relevant_chunks(
        self, phase_name: str, required_sections: Optional[List[str]] = None
    ) -> List[SpecChunk]:
        """Select chunks relevant to a phase."""
        relevant_chunks = []
        
        # Phase-specific selection logic
        phase_keywords = self._get_phase_keywords(phase_name)
        
        for chunk in self.loaded_chunks.values():
            relevance_score = 0
            
            # Check required sections
            if required_sections:
                for section in required_sections:
                    section_name = chunk.metadata.get("section_name", "")
                    if section_name and section.lower() in section_name.lower():
                        relevance_score += 10
            
            # Check keywords
            for keyword in phase_keywords:
                keywords = chunk.metadata.get("keywords", [])
                if keyword in keywords:
                    relevance_score += 5
                elif keyword in chunk.content.lower():
                    relevance_score += 2
            
            # Add if relevant
            if relevance_score > 0 or not required_sections:
                relevant_chunks.append(chunk)
        
        return relevant_chunks

    def _get_phase_keywords(self, phase_name: str) -> List[str]:
        """Get keywords relevant to a phase."""
        phase_keywords = {
            "specification_analysis": [
                "requirement", "overview", "architecture", "goal",
                "objective", "scope", "constraint", "assumption",
            ],
            "task_generation": [
                "task", "milestone", "deliverable", "timeline",
                "dependency", "phase", "breakdown", "planning",
            ],
            "instruction_building": [
                "implementation", "technical", "api", "interface",
                "component", "integration", "configuration",
            ],
            "code_generation": [
                "code", "function", "class", "module", "package",
                "implementation", "algorithm", "structure",
            ],
            "testing": [
                "test", "validation", "verification", "quality",
                "coverage", "scenario", "case", "assertion",
            ],
        }
        
        return phase_keywords.get(phase_name.lower(), [])

    async def _create_chunk_summary(self, chunk: SpecChunk) -> str:
        """Create a summary of a chunk."""
        # Simple extraction - in production would use LLM
        lines = chunk.content.split('\n')
        summary_lines = []
        
        # Get section headers and key points
        for line in lines:
            if any(line.startswith(marker) for marker in ['#', '-', '*', '•']):
                summary_lines.append(line)
            elif any(term in line.lower() for term in ['must', 'shall', 'requirement']):
                summary_lines.append(f"- {line.strip()}")
        
        summary = '\n'.join(summary_lines[:50])  # Limit summary length
        return summary

    async def optimize_context(
        self, current_context: str, target_tokens: int
    ) -> str:
        """Optimize context to fit within token limit."""
        current_tokens = self.token_counter.count(current_context)
        
        if current_tokens <= target_tokens:
            return current_context
        
        # Need to reduce - try various strategies
        strategies = [
            self._remove_code_examples,
            self._remove_redundant_sections,
            self._summarize_verbose_sections,
            self._remove_low_priority_content,
        ]
        
        optimized = current_context
        for strategy in strategies:
            optimized = await strategy(optimized)
            new_tokens = self.token_counter.count(optimized)
            
            if new_tokens <= target_tokens:
                break
        
        # Final truncation if needed
        if self.token_counter.count(optimized) > target_tokens:
            optimized = self.token_counter.truncate(optimized, target_tokens)
        
        return optimized

    async def _remove_code_examples(self, content: str) -> str:
        """Remove code examples to save tokens."""
        lines = content.split('\n')
        filtered_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if not in_code_block:
                    filtered_lines.append("[Code example removed for context optimization]")
            elif not in_code_block:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    async def _remove_redundant_sections(self, content: str) -> str:
        """Remove redundant or repetitive sections."""
        # Simple implementation - would use more sophisticated detection
        sections = content.split('\n\n')
        seen_content = set()
        filtered_sections = []
        
        for section in sections:
            # Create content signature
            signature = ' '.join(section.lower().split()[:20])
            
            if signature not in seen_content:
                filtered_sections.append(section)
                seen_content.add(signature)
        
        return '\n\n'.join(filtered_sections)

    async def _summarize_verbose_sections(self, content: str) -> str:
        """Summarize verbose sections."""
        # Placeholder - would use LLM for actual summarization
        return content

    async def _remove_low_priority_content(self, content: str) -> str:
        """Remove low priority content."""
        lines = content.split('\n')
        filtered_lines = []
        
        skip_patterns = [
            'note:', 'example:', 'for instance', 'additionally',
            'furthermore', 'in other words', 'that is to say',
        ]
        
        for line in lines:
            line_lower = line.lower()
            if not any(pattern in line_lower for pattern in skip_patterns):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about context usage."""
        total_chunks = len(self.loaded_chunks)
        total_tokens = sum(c.metadata.token_count for c in self.loaded_chunks.values())
        accessed_chunks = len(self.chunk_access_count)
        
        return {
            "total_chunks": total_chunks,
            "total_tokens": total_tokens,
            "accessed_chunks": accessed_chunks,
            "access_rate": accessed_chunks / total_chunks if total_chunks > 0 else 0,
            "most_accessed": sorted(
                self.chunk_access_count.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "phase_coverage": {
                phase: len(chunks) for phase, chunks in self.phase_contexts.items()
            },
        }


class DynamicContextLoader:
    """Dynamically loads context based on runtime needs."""

    def __init__(
        self,
        context_manager: ContextManager,
        mcp_servers: Dict[str, MCPServer],
    ) -> None:
        """Initialize the loader."""
        self.context_manager = context_manager
        self.mcp_servers = mcp_servers
        self.loaded_resources: Set[str] = set()

    async def load_for_agent(
        self,
        agent_type: str,
        phase: str,
        task: Optional[str] = None,
    ) -> str:
        """Load context optimized for specific agent."""
        context_parts = []
        
        # Base specification context
        base_context = await self.context_manager.get_context_for_phase(phase)
        context_parts.append(base_context)
        
        # Agent-specific additions
        if agent_type == "SpecAnalyzer":
            extra = await self._load_spec_analyzer_context()
        elif agent_type == "TaskGenerator":
            extra = await self._load_task_generator_context(phase)
        elif agent_type == "InstructionBuilder":
            extra = await self._load_instruction_builder_context(task)
        elif agent_type == "CodeGenerator":
            extra = await self._load_code_generator_context(task)
        else:
            extra = ""
        
        if extra:
            context_parts.append(extra)
        
        # Combine and optimize
        full_context = '\n\n'.join(context_parts)
        return await self.context_manager.optimize_context(
            full_context,
            self.context_manager.effective_max_tokens,
        )

    async def _load_spec_analyzer_context(self) -> str:
        """Load context for specification analyzer."""
        context_parts = []
        
        # Add analysis templates
        context_parts.append("""
## Specification Analysis Guidelines

Focus on extracting:
1. Project type and technology stack
2. Core functional requirements
3. Non-functional requirements
4. Technical constraints
5. Integration points
6. Success criteria
""")
        
        # Load from MCP if available
        if MCPServer.CONTEXT7 in self.mcp_servers:
            # Would call MCP to get relevant examples
            pass
        
        return '\n'.join(context_parts)

    async def _load_task_generator_context(self, phase: str) -> str:
        """Load context for task generator."""
        context_parts = []
        
        # Add task generation templates
        context_parts.append(f"""
## Task Generation for {phase}

Structure tasks with:
- Clear, actionable descriptions
- Specific acceptance criteria
- Dependency relationships
- Estimated complexity
- Required tools/resources
""")
        
        return '\n'.join(context_parts)

    async def _load_instruction_builder_context(self, task: Optional[str]) -> str:
        """Load context for instruction builder."""
        if not task:
            return ""
        
        context_parts = []
        
        # Add instruction templates
        context_parts.append(f"""
## Instruction Building for: {task}

Include:
- Step-by-step implementation guide
- Code structure requirements
- Integration points
- Testing requirements
- Error handling specifications
""")
        
        return '\n'.join(context_parts)

    async def _load_code_generator_context(self, task: Optional[str]) -> str:
        """Load context for code generator."""
        if not task:
            return ""
        
        # Would load relevant code examples, patterns, etc.
        return f"## Code Generation Context for: {task}\n"


class ContextSummarizer:
    """Creates summaries of context for checkpointing."""

    def __init__(self, token_counter: Optional[TokenCounter] = None) -> None:
        """Initialize the summarizer."""
        self.token_counter = token_counter or TokenCounter()

    async def summarize_phase_context(
        self,
        phase_name: str,
        context: str,
        max_summary_tokens: int = 2000,
    ) -> str:
        """Create a summary of phase context."""
        # Extract key information
        summary_parts = [f"# Phase Summary: {phase_name}\n"]
        
        # Extract headers and key points
        lines = context.split('\n')
        current_section = ""
        key_points = []
        
        for line in lines:
            if line.startswith('#'):
                if current_section and key_points:
                    summary_parts.append(f"\n{current_section}")
                    summary_parts.extend(f"- {point}" for point in key_points[:3])
                current_section = line
                key_points = []
            elif any(marker in line.lower() for marker in ['must', 'shall', 'require']):
                key_points.append(line.strip())
        
        # Add final section
        if current_section and key_points:
            summary_parts.append(f"\n{current_section}")
            summary_parts.extend(f"- {point}" for point in key_points[:3])
        
        summary = '\n'.join(summary_parts)
        
        # Truncate if needed
        if self.token_counter.count(summary) > max_summary_tokens:
            summary = self.token_counter.truncate(summary, max_summary_tokens)
        
        return summary

    async def create_checkpoint_summary(
        self,
        completed_phases: List[str],
        current_phase: str,
        key_decisions: List[str],
    ) -> str:
        """Create a checkpoint summary."""
        summary = f"""# Checkpoint Summary

## Completed Phases
{chr(10).join(f"- {phase}" for phase in completed_phases)}

## Current Phase
{current_phase}

## Key Decisions
{chr(10).join(f"- {decision}" for decision in key_decisions[-10:])}

## Next Steps
Ready to continue from {current_phase}
"""
        return summary


class ContextArchiver:
    """Archives context for long-term storage."""

    def __init__(self, archive_dir: Path) -> None:
        """Initialize the archiver."""
        self.archive_dir = archive_dir
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    async def archive_phase_context(
        self,
        phase_name: str,
        context: str,
        metadata: Dict[str, Any],
    ) -> Path:
        """Archive context from a phase."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = self.archive_dir / f"{phase_name}_{timestamp}.json"
        
        archive_data = {
            "phase": phase_name,
            "timestamp": timestamp,
            "metadata": metadata,
            "context": context,
            "context_hash": hashlib.sha256(context.encode()).hexdigest(),
        }
        
        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        return archive_file

    async def retrieve_phase_context(self, phase_name: str) -> Optional[str]:
        """Retrieve most recent context for a phase."""
        pattern = f"{phase_name}_*.json"
        files = sorted(self.archive_dir.glob(pattern), reverse=True)
        
        if not files:
            return None
        
        with open(files[0]) as f:
            data = json.load(f)
        
        return data["context"]


__all__ = [
    "ContextManager",
    "SpecificationChunker",
    "DynamicContextLoader",
    "ContextSummarizer",
    "ContextArchiver",
    "TokenCounter",
    "ChunkMetadata",
]