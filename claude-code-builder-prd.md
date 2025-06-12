# Claude Code Builder - Product Requirements Document v2.0

## 1. Executive Summary

### 1.1 Product Overview
Claude Code Builder is an AI-powered Python CLI tool that automates the complete software development lifecycle using Claude Code SDK and Anthropic's agent system. It transforms project specifications of any size into fully implemented, production-ready applications through intelligent task decomposition, custom AI instruction generation, and systematic phase-based execution with comprehensive documentation.

### 1.2 Core Value Proposition
- **Large Specification Support**: Handles specs exceeding context limits through intelligent chunking and context management
- **Production-Only Testing**: Enforces real-world functional testing with explicit acceptance criteria
- **MCP-First Development**: Mandates use of MCP servers at every command for maximum capability
- **Comprehensive Audit Trail**: Streams and persists all logs, code generation, and API interactions
- **Intelligent Project Management**: Unique timestamped builds with smart resume capabilities
- **Built-in Documentation**: Generates complete documentation alongside implementation

### 1.3 Key Differentiators
- **Extended Context Utilization**: Leverages Opus 4's massive context window for large specs
- **Zero Mock Policy**: Every test, every integration, every line of code is production-ready
- **Complete Transparency**: Every decision, API call, and generated line is logged
- **Turnkey Solution**: From spec to documented, tested, production code in one command
- **Resumable Builds**: Pick up exactly where you left off with full context restoration

## 2. Technical Architecture

### 2.1 System Components

```
claude-code-builder/
├── src/
│   ├── __init__.py
│   ├── cli.py                    # Main CLI entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── spec_analyzer.py      # Specification analysis agent
│   │   ├── task_generator.py     # Task breakdown generator
│   │   ├── instruction_builder.py # AI instruction generator
│   │   ├── acceptance_generator.py # Acceptance criteria generator
│   │   ├── documentation_agent.py # Documentation generator
│   │   └── executor.py           # Claude Code execution manager
│   ├── core/
│   │   ├── __init__.py
│   │   ├── project_manager.py    # Project lifecycle management
│   │   ├── context_manager.py    # Large spec context handling
│   │   ├── memory_manager.py     # Persistent memory handling
│   │   ├── mcp_orchestrator.py   # MCP server orchestration
│   │   ├── logging_system.py     # Comprehensive logging
│   │   └── output_manager.py     # Output directory management
│   ├── builders/
│   │   ├── __init__.py
│   │   ├── claude_md_builder.py  # CLAUDE.md file generator
│   │   ├── command_builder.py    # Custom command generator
│   │   ├── structure_builder.py  # Project structure creator
│   │   └── documentation_builder.py # Doc generation system
│   ├── testing/
│   │   ├── __init__.py
│   │   ├── acceptance_runner.py  # Acceptance criteria validation
│   │   ├── functional_tester.py  # Real-world test execution
│   │   └── production_validator.py # Production readiness checks
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_operations.py
│   │   ├── git_integration.py
│   │   ├── api_logger.py        # Anthropic API call logging
│   │   └── validation.py
│   └── templates/
│       ├── claude_md.j2
│       ├── commands/
│       ├── instructions/
│       └── documentation/
├── tests/                        # Functional tests only
├── docs/
├── examples/
└── pyproject.toml
```

### 2.2 Technology Stack

#### Core Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
anthropic = "^0.34.0"          # For agent operations
claude-code-sdk = "^1.0.0"      # For Claude Code execution
click = "^8.1.7"                # CLI framework
rich = "^13.7.0"                # Enhanced console output
pydantic = "^2.5.0"             # Data validation
jinja2 = "^3.1.3"               # Template engine
gitpython = "^3.1.40"           # Git operations
aiofiles = "^23.2.1"            # Async file operations
httpx = "^0.25.2"               # HTTP client
python-dotenv = "^1.0.0"        # Environment management
structlog = "^24.1.0"           # Structured logging
watchdog = "^4.0.0"             # File system monitoring
tiktoken = "^0.5.2"             # Token counting
xxhash = "^3.4.1"               # Fast hashing for caching
humanize = "^4.9.0"             # Human-readable output
tabulate = "^0.9.0"             # Table formatting
```

## 3. Context Management System

### 3.1 Large Specification Handling

```python
class ContextManager:
    """Manages large specifications that exceed single context limits"""
    
    def __init__(self, max_tokens: int = 150000):  # Opus 4 extended context
        self.max_tokens = max_tokens
        self.token_counter = TokenCounter()
        self.context_chunks = []
        self.logger = structlog.get_logger()
        
    async def process_large_spec(self, spec_path: Path) -> ProcessedSpec:
        """Process specifications of any size"""
        self.logger.info("processing_large_spec", path=spec_path)
        
        # Load and analyze spec size
        spec_content = await self._load_spec(spec_path)
        total_tokens = self.token_counter.count(spec_content)
        
        if total_tokens <= self.max_tokens * 0.8:  # Leave room for responses
            # Fits in single context
            return ProcessedSpec(
                chunks=[spec_content],
                total_tokens=total_tokens,
                requires_chunking=False
            )
        
        # Intelligent chunking for large specs
        chunks = await self._chunk_specification(spec_content)
        
        # Create chunk summaries for cross-reference
        summaries = await self._generate_chunk_summaries(chunks)
        
        return ProcessedSpec(
            chunks=chunks,
            summaries=summaries,
            total_tokens=total_tokens,
            requires_chunking=True,
            chunk_strategy=self._determine_strategy(spec_content)
        )
    
    async def _chunk_specification(self, content: str) -> List[SpecChunk]:
        """Intelligently chunk specification maintaining context"""
        chunks = []
        
        # Parse spec structure
        sections = self._parse_spec_sections(content)
        
        current_chunk = SpecChunk()
        for section in sections:
            section_tokens = self.token_counter.count(section.content)
            
            if current_chunk.tokens + section_tokens > self.max_tokens * 0.7:
                # Save current chunk and start new one
                chunks.append(current_chunk)
                current_chunk = SpecChunk()
                
                # Add cross-reference context
                current_chunk.add_context(
                    f"Previous section: {section.title}"
                )
            
            current_chunk.add_section(section)
            
        if current_chunk.sections:
            chunks.append(current_chunk)
            
        # Add chunk metadata
        for i, chunk in enumerate(chunks):
            chunk.index = i
            chunk.total_chunks = len(chunks)
            chunk.add_navigation_context(chunks)
            
        return chunks
```

### 3.2 Dynamic Context Loading

```python
class DynamicContextLoader:
    """Load context dynamically during execution"""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
        self.loaded_contexts = {}
        self.logger = structlog.get_logger()
        
    async def load_context_for_phase(self, phase: Phase, spec: ProcessedSpec) -> PhaseContext:
        """Load relevant context for current phase"""
        self.logger.info("loading_phase_context", phase=phase.name)
        
        # Determine which spec sections are needed
        required_sections = await self._analyze_phase_requirements(phase)
        
        # Build focused context
        context_parts = []
        
        # Always include project overview
        context_parts.append(await self._get_project_overview(spec))
        
        # Add phase-specific sections
        for section in required_sections:
            chunk = await self._find_chunk_with_section(section, spec)
            context_parts.append(chunk.get_section(section))
            
        # Add previous phase outputs if relevant
        if phase.dependencies:
            for dep_phase_id in phase.dependencies:
                prev_output = await self._get_phase_output(dep_phase_id)
                context_parts.append(prev_output.summary)
                
        # Add memory context
        memory_context = await self._get_memory_context(phase)
        context_parts.append(memory_context)
        
        return PhaseContext(
            phase_id=phase.id,
            content="\n\n".join(context_parts),
            token_count=self.token_counter.count_all(context_parts),
            sections_included=required_sections
        )
```

## 4. Output Directory Management

### 4.1 Project Output Structure

```python
class OutputManager:
    """Manages project output directories with timestamp-based organization"""
    
    def __init__(self, base_output_dir: Path = Path("./claude-builds")):
        self.base_output_dir = base_output_dir
        self.base_output_dir.mkdir(exist_ok=True)
        self.logger = structlog.get_logger()
        
    async def create_project_directory(
        self, 
        project_name: str, 
        user_specified_dir: Optional[Path] = None
    ) -> ProjectDirectory:
        """Create or resume project directory"""
        
        if user_specified_dir:
            # Check if resuming or starting fresh
            if user_specified_dir.exists():
                resume = await self._should_resume_project(user_specified_dir)
                if resume:
                    self.logger.info("resuming_project", dir=user_specified_dir)
                    return await self._load_project_directory(user_specified_dir)
                else:
                    # Backup existing and create new
                    backup_path = await self._backup_existing(user_specified_dir)
                    self.logger.info("backed_up_existing", 
                                   original=user_specified_dir, 
                                   backup=backup_path)
            
            return await self._create_new_project_directory(
                project_name, 
                user_specified_dir
            )
        
        # Create timestamped directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{project_name}_{timestamp}"
        project_dir = self.base_output_dir / dir_name
        
        return await self._create_new_project_directory(
            project_name, 
            project_dir
        )
    
    async def _create_new_project_directory(
        self, 
        project_name: str, 
        path: Path
    ) -> ProjectDirectory:
        """Create new project directory structure"""
        path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = {
            "source": path / "src",
            "logs": path / "logs",
            "artifacts": path / "artifacts",
            "checkpoints": path / ".checkpoints",
            "memory": path / ".memory",
            "documentation": path / "docs",
            "tests": path / "tests",
            "api_logs": path / "logs" / "api_calls"
        }
        
        for subdir in subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
            
        # Create project metadata
        metadata = ProjectMetadata(
            project_name=project_name,
            created_at=datetime.now(),
            claude_code_version=get_version(),
            output_directory=str(path),
            subdirectories=subdirs
        )
        
        await self._save_metadata(path, metadata)
        
        return ProjectDirectory(
            path=path,
            metadata=metadata,
            subdirs=subdirs
        )
```

### 4.2 Resume Logic

```python
class ProjectResumer:
    """Handle project resume logic"""
    
    def __init__(self, output_manager: OutputManager):
        self.output_manager = output_manager
        self.logger = structlog.get_logger()
        
    async def check_resume_capability(self, project_dir: Path) -> ResumeStatus:
        """Check if project can be resumed"""
        try:
            # Load project state
            state_file = project_dir / ".checkpoints" / "latest_state.json"
            if not state_file.exists():
                return ResumeStatus(
                    can_resume=False,
                    reason="No checkpoint found"
                )
                
            state = await self._load_project_state(state_file)
            
            # Validate state integrity
            validation = await self._validate_state(state, project_dir)
            if not validation.is_valid:
                return ResumeStatus(
                    can_resume=False,
                    reason=validation.reason,
                    corruption_details=validation.details
                )
                
            # Check spec hasn't changed
            spec_unchanged = await self._verify_spec_unchanged(
                state.spec_hash, 
                project_dir
            )
            if not spec_unchanged:
                return ResumeStatus(
                    can_resume=True,
                    reason="Specification has changed",
                    requires_confirmation=True,
                    last_phase=state.current_phase,
                    completed_phases=state.completed_phases
                )
                
            return ResumeStatus(
                can_resume=True,
                last_phase=state.current_phase,
                completed_phases=state.completed_phases,
                completed_tasks=len(state.completed_tasks),
                last_checkpoint=state.last_checkpoint
            )
            
        except Exception as e:
            self.logger.exception("resume_check_failed", error=str(e))
            return ResumeStatus(
                can_resume=False,
                reason=f"Error checking resume status: {str(e)}"
            )
```

## 5. Comprehensive Logging System

### 5.1 Multi-Level Logging Architecture

```python
class ComprehensiveLogger:
    """Unified logging system with streaming and persistence"""
    
    def __init__(self, project_dir: ProjectDirectory):
        self.project_dir = project_dir
        self.log_dir = project_dir.subdirs["logs"]
        self.api_log_dir = project_dir.subdirs["api_logs"]
        
        # Set up multiple log streams
        self.streams = self._setup_log_streams()
        self.api_logger = APICallLogger(self.api_log_dir)
        self.code_logger = GeneratedCodeLogger(self.log_dir / "generated_code")
        
    def _setup_log_streams(self) -> Dict[str, Any]:
        """Set up console and file logging streams"""
        streams = {}
        
        # Console stream with rich formatting
        console_handler = RichHandler(
            console=Console(record=True),
            show_time=True,
            show_path=False
        )
        
        # Main log file
        main_log_path = self.log_dir / "claude_code_builder.log"
        file_handler = logging.FileHandler(main_log_path)
        
        # Detailed debug log
        debug_log_path = self.log_dir / "debug.log"
        debug_handler = logging.FileHandler(debug_log_path)
        
        # Structured JSON log for analysis
        json_log_path = self.log_dir / "structured.jsonl"
        json_handler = StructuredFileHandler(json_log_path)
        
        # Configure handlers
        formatters = {
            "console": logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%H:%M:%S"
            ),
            "file": logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s"
            ),
            "json": JSONFormatter()
        }
        
        console_handler.setFormatter(formatters["console"])
        file_handler.setFormatter(formatters["file"])
        debug_handler.setFormatter(formatters["file"])
        
        streams["console"] = console_handler
        streams["main_file"] = file_handler
        streams["debug_file"] = debug_handler
        streams["json_file"] = json_handler
        
        return streams
    
    async def log_api_call(self, api_call: APICall):
        """Log Anthropic API call with full request/response"""
        self.logger.info(
            "api_call",
            endpoint=api_call.endpoint,
            model=api_call.model,
            tokens_in=api_call.tokens_in,
            tokens_out=api_call.tokens_out,
            latency_ms=api_call.latency_ms
        )
        
        # Save full API call details
        await self.api_logger.log_call(api_call)
        
    async def log_generated_code(self, code_block: GeneratedCode):
        """Log generated code with context"""
        self.logger.info(
            "code_generated",
            file_path=code_block.file_path,
            language=code_block.language,
            lines=code_block.line_count,
            phase=code_block.phase,
            task=code_block.task
        )
        
        # Save code with metadata
        await self.code_logger.log_code(code_block)
```

### 5.2 API Call Logging

```python
class APICallLogger:
    """Detailed logging of all Anthropic API interactions"""
    
    def __init__(self, api_log_dir: Path):
        self.api_log_dir = api_log_dir
        self.current_session_dir = None
        self.call_counter = 0
        
    async def start_session(self):
        """Start new API logging session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_dir = self.api_log_dir / f"session_{timestamp}"
        self.current_session_dir.mkdir(parents=True)
        
    async def log_call(self, api_call: APICall):
        """Log complete API call with request and response"""
        self.call_counter += 1
        
        # Create call-specific file
        call_file = self.current_session_dir / f"call_{self.call_counter:04d}.json"
        
        call_data = {
            "timestamp": api_call.timestamp.isoformat(),
            "call_id": api_call.call_id,
            "endpoint": api_call.endpoint,
            "model": api_call.model,
            "request": {
                "messages": api_call.request_messages,
                "system": api_call.system_prompt,
                "temperature": api_call.temperature,
                "max_tokens": api_call.max_tokens,
                "tools": api_call.tools
            },
            "response": {
                "content": api_call.response_content,
                "tool_calls": api_call.tool_calls,
                "usage": {
                    "input_tokens": api_call.tokens_in,
                    "output_tokens": api_call.tokens_out,
                    "total_tokens": api_call.tokens_total
                }
            },
            "performance": {
                "latency_ms": api_call.latency_ms,
                "stream_chunks": api_call.stream_chunks
            },
            "context": {
                "phase": api_call.phase,
                "task": api_call.task,
                "agent": api_call.agent_type
            }
        }
        
        # Write with pretty formatting
        async with aiofiles.open(call_file, 'w') as f:
            await f.write(json.dumps(call_data, indent=2))
            
        # Also append to session log
        session_log = self.current_session_dir / "session_summary.jsonl"
        summary = {
            "timestamp": api_call.timestamp.isoformat(),
            "call_number": self.call_counter,
            "model": api_call.model,
            "tokens": api_call.tokens_total,
            "latency_ms": api_call.latency_ms,
            "cost": api_call.estimated_cost
        }
        
        async with aiofiles.open(session_log, 'a') as f:
            await f.write(json.dumps(summary) + "\n")
```

### 5.3 Generated Code Tracking

```python
class GeneratedCodeLogger:
    """Track all generated code with full context"""
    
    def __init__(self, code_log_dir: Path):
        self.code_log_dir = code_log_dir
        self.code_log_dir.mkdir(exist_ok=True)
        self.code_index = []
        
    async def log_code(self, code_block: GeneratedCode):
        """Log generated code with metadata"""
        # Create phase-specific directory
        phase_dir = self.code_log_dir / code_block.phase
        phase_dir.mkdir(exist_ok=True)
        
        # Save code file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        code_file = phase_dir / f"{timestamp}_{code_block.file_name}"
        
        # Write code with header
        header = f"""# Generated by Claude Code Builder
# Phase: {code_block.phase}
# Task: {code_block.task}
# Timestamp: {code_block.timestamp}
# Model: {code_block.model}
# Tokens: {code_block.tokens_used}
# Original Path: {code_block.file_path}
# {"="*60}

"""
        
        async with aiofiles.open(code_file, 'w') as f:
            await f.write(header + code_block.content)
            
        # Update index
        self.code_index.append({
            "timestamp": code_block.timestamp.isoformat(),
            "phase": code_block.phase,
            "task": code_block.task,
            "file_path": code_block.file_path,
            "language": code_block.language,
            "lines": code_block.line_count,
            "tokens": code_block.tokens_used,
            "log_path": str(code_file.relative_to(self.code_log_dir))
        })
        
        # Save index
        index_file = self.code_log_dir / "code_index.json"
        async with aiofiles.open(index_file, 'w') as f:
            await f.write(json.dumps(self.code_index, indent=2))
```

## 6. MCP Server Orchestration

### 6.1 MCP-First Development Enforcement

```python
class MCPOrchestrator:
    """Ensures MCP servers are used at every command"""
    
    def __init__(self):
        self.required_servers = {
            "context7": {
                "usage": "MANDATORY for all documentation lookups",
                "enforce_at": ["phase_start", "before_implementation", "research"]
            },
            "memory": {
                "usage": "MANDATORY for context storage and retrieval",
                "enforce_at": ["task_complete", "phase_complete", "checkpoint"]
            },
            "sequential-thinking": {
                "usage": "MANDATORY for complex problem decomposition",
                "enforce_at": ["phase_planning", "architecture_decisions", "debugging"]
            },
            "filesystem": {
                "usage": "MANDATORY for all file operations",
                "enforce_at": ["file_read", "file_write", "directory_ops"]
            },
            "git": {
                "usage": "MANDATORY for version control",
                "enforce_at": ["task_complete", "phase_complete", "checkpoint"]
            }
        }
        
    async def generate_mcp_instructions(self, phase: Phase) -> str:
        """Generate phase-specific MCP usage instructions"""
        instructions = ["## 🚨 MANDATORY MCP USAGE FOR THIS PHASE\n"]
        
        # Analyze phase requirements
        required_mcps = await self._analyze_phase_mcp_needs(phase)
        
        for server, requirements in required_mcps.items():
            instructions.append(f"\n### {server.upper()} MCP - REQUIRED")
            instructions.append(f"**Usage**: {requirements['usage']}")
            instructions.append(f"**When**: {', '.join(requirements['when'])}")
            instructions.append(f"**Pattern**:")
            instructions.append(f"```")
            instructions.append(requirements['example'])
            instructions.append(f"```")
            
        return "\n".join(instructions)
    
    async def validate_mcp_usage(self, execution_log: ExecutionLog) -> MCPValidation:
        """Validate that MCPs were used appropriately"""
        validation = MCPValidation()
        
        for server, config in self.required_servers.items():
            usage_points = config["enforce_at"]
            
            for point in usage_points:
                if point in execution_log.checkpoints:
                    server_used = await self._check_mcp_usage_at_point(
                        server, 
                        point, 
                        execution_log
                    )
                    
                    if not server_used:
                        validation.add_violation(
                            server=server,
                            checkpoint=point,
                            severity="critical",
                            message=f"{server} MCP not used at {point}"
                        )
                        
        return validation
```

### 6.2 Custom MCP Instructions

```python
MCP_INSTRUCTION_TEMPLATE = """
## 🔴 CRITICAL MCP USAGE REQUIREMENTS

You MUST use these MCP servers at EVERY appropriate opportunity:

### 1. context7 MCP - Documentation Research
**MANDATORY USAGE**:
- BEFORE implementing ANY library or framework
- WHEN encountering unfamiliar APIs or methods  
- TO verify current best practices
- FOR security advisory checks

**Example Usage Pattern**:
```
Before implementing FastAPI endpoints:
1. Use context7 to get latest FastAPI documentation
2. Research current async patterns
3. Check for deprecation warnings
4. Find security best practices
```

### 2. memory MCP - Context Persistence
**MANDATORY USAGE**:
- AFTER completing each task
- WHEN making architectural decisions
- TO store error solutions
- FOR tracking implementation progress

**Example Usage Pattern**:
```
After implementing authentication:
1. Store implementation details in memory
2. Save architectural decisions made
3. Record any workarounds used
4. Update progress tracking
```

### 3. sequential-thinking MCP - Problem Decomposition
**MANDATORY USAGE**:
- BEFORE starting complex implementations
- WHEN debugging difficult issues
- FOR planning multi-step operations
- TO break down architectural challenges

### 4. filesystem MCP - File Operations
**MANDATORY USAGE**:
- FOR all file reading operations
- WHEN creating or modifying files
- TO check file existence
- FOR directory management

### 5. git MCP - Version Control
**MANDATORY USAGE**:
- AFTER each task completion
- WHEN reaching phase milestones
- TO create meaningful commits
- FOR branch management

## ⚠️ ENFORCEMENT

Failure to use MCP servers when required will result in:
1. Task marked as incomplete
2. Requirement to redo with proper MCP usage
3. Logged as compliance violation

Remember: MCP servers are not optional - they are MANDATORY for quality and consistency.
"""
```

## 7. Production Testing System

### 7.1 Acceptance Criteria Generation

```python
class AcceptanceCriteriaGenerator:
    """Generate explicit acceptance criteria for each phase"""
    
    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic()
        self.model = model
        
    async def generate_criteria(
        self, 
        phase: Phase, 
        spec_context: SpecContext
    ) -> AcceptanceCriteria:
        """Generate comprehensive acceptance criteria"""
        
        prompt = f"""
You are a QA architect creating acceptance criteria for production validation.
Generate explicit, measurable acceptance criteria for this phase.

Phase: {phase.name}
Tasks: {json.dumps([t.name for t in phase.tasks])}
Specification Context: {spec_context.summary}

Generate acceptance criteria that:
1. Are specific and measurable
2. Can be tested with real data/systems
3. Cover functional requirements
4. Include performance requirements
5. Address security considerations
6. Verify integration points

Format:
{{
  "functional_criteria": [
    {{
      "id": "FC001",
      "description": "User can successfully authenticate with valid credentials",
      "test_steps": ["Step 1", "Step 2"],
      "expected_result": "User receives JWT token and 200 status",
      "validation_method": "api_test",
      "test_data_requirements": ["Valid user account", "Test database"]
    }}
  ],
  "performance_criteria": [...],
  "security_criteria": [...],
  "integration_criteria": [...]
}}

NO MOCK TESTS - all criteria must be validated with real implementations.
"""
        
        response = await self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.3
        )
        
        criteria_data = json.loads(response.content[0].text)
        return AcceptanceCriteria(**criteria_data)
```

### 7.2 Production Test Runner

```python
class ProductionTestRunner:
    """Execute real-world tests with no mocks"""
    
    def __init__(self, project_dir: ProjectDirectory):
        self.project_dir = project_dir
        self.test_env = self._setup_test_environment()
        self.logger = structlog.get_logger()
        
    def _setup_test_environment(self) -> TestEnvironment:
        """Set up real test environment"""
        return TestEnvironment(
            database_url=os.getenv("TEST_DATABASE_URL"),
            api_keys={
                "test_api_key": os.getenv("TEST_API_KEY"),
                "integration_key": os.getenv("INTEGRATION_API_KEY")
            },
            test_data_dir=self.project_dir.path / "test_data",
            services={
                "redis": "redis://localhost:6379/1",
                "elasticsearch": "http://localhost:9200"
            }
        )
        
    async def run_acceptance_tests(
        self, 
        criteria: AcceptanceCriteria,
        implementation_path: Path
    ) -> TestResults:
        """Run all acceptance tests with real data"""
        self.logger.info(
            "running_acceptance_tests",
            total_criteria=criteria.total_count,
            categories=criteria.categories
        )
        
        results = TestResults()
        
        # Functional tests
        for criterion in criteria.functional_criteria:
            result = await self._run_functional_test(criterion, implementation_path)
            results.add_result(result)
            
            self.logger.info(
                "functional_test_complete",
                criterion_id=criterion.id,
                passed=result.passed,
                duration_ms=result.duration_ms
            )
            
        # Performance tests  
        for criterion in criteria.performance_criteria:
            result = await self._run_performance_test(criterion, implementation_path)
            results.add_result(result)
            
        # Security tests
        for criterion in criteria.security_criteria:
            result = await self._run_security_test(criterion, implementation_path)
            results.add_result(result)
            
        # Integration tests
        for criterion in criteria.integration_criteria:
            result = await self._run_integration_test(criterion, implementation_path)
            results.add_result(result)
            
        return results
    
    async def _run_functional_test(
        self, 
        criterion: FunctionalCriterion,
        implementation_path: Path
    ) -> TestResult:
        """Run functional test with real implementation"""
        start_time = time.time()
        
        try:
            # Set up test data
            test_data = await self._prepare_test_data(criterion.test_data_requirements)
            
            # Execute test steps
            for step in criterion.test_steps:
                await self._execute_test_step(step, test_data, implementation_path)
                
            # Validate result
            actual_result = await self._get_actual_result(
                criterion.validation_method,
                implementation_path
            )
            
            passed = self._validate_result(actual_result, criterion.expected_result)
            
            return TestResult(
                criterion_id=criterion.id,
                passed=passed,
                actual_result=actual_result,
                expected_result=criterion.expected_result,
                duration_ms=int((time.time() - start_time) * 1000),
                test_type="functional"
            )
            
        except Exception as e:
            self.logger.exception("functional_test_failed", criterion_id=criterion.id)
            return TestResult(
                criterion_id=criterion.id,
                passed=False,
                error=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                test_type="functional"
            )
```

## 8. Documentation Generation

### 8.1 Integrated Documentation System

```python
class DocumentationGenerator:
    """Generate comprehensive documentation alongside code"""
    
    def __init__(self, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.doc_builder = DocumentationBuilder()
        
    async def generate_project_documentation(
        self,
        project: Project,
        implementation: Implementation
    ) -> Documentation:
        """Generate complete project documentation"""
        
        docs = Documentation()
        
        # Architecture documentation
        arch_doc = await self._generate_architecture_doc(
            project.spec,
            implementation.architecture_decisions
        )
        docs.add_section("architecture", arch_doc)
        
        # API documentation
        if implementation.has_api:
            api_doc = await self._generate_api_documentation(
                implementation.api_endpoints
            )
            docs.add_section("api", api_doc)
            
        # Component documentation
        for component in implementation.components:
            comp_doc = await self._generate_component_doc(component)
            docs.add_section(f"component_{component.name}", comp_doc)
            
        # Deployment documentation
        deploy_doc = await self._generate_deployment_doc(
            implementation.deployment_config
        )
        docs.add_section("deployment", deploy_doc)
        
        # Testing documentation
        test_doc = await self._generate_testing_doc(
            implementation.test_results,
            implementation.acceptance_criteria
        )
        docs.add_section("testing", test_doc)
        
        # User guide
        user_guide = await self._generate_user_guide(
            project.spec,
            implementation
        )
        docs.add_section("user_guide", user_guide)
        
        # Developer guide
        dev_guide = await self._generate_developer_guide(
            implementation,
            project.custom_instructions
        )
        docs.add_section("developer_guide", dev_guide)
        
        return docs
    
    async def _generate_architecture_doc(
        self,
        spec: Specification,
        decisions: List[ArchitectureDecision]
    ) -> str:
        """Generate architecture documentation"""
        
        prompt = f"""
Create comprehensive architecture documentation for this implementation.

Project Specification Summary:
{spec.summary}

Architecture Decisions Made:
{json.dumps([d.to_dict() for d in decisions], indent=2)}

Include:
1. System Overview
   - High-level architecture diagram (ASCII/Mermaid)
   - Component relationships
   - Data flow

2. Component Details
   - Purpose and responsibilities
   - Interfaces and contracts
   - Dependencies

3. Design Patterns
   - Patterns used and why
   - Implementation details
   - Trade-offs

4. Technology Stack
   - Technologies chosen
   - Justification for choices
   - Integration approaches

5. Scalability Considerations
   - Current limitations
   - Scaling strategies
   - Performance optimizations

6. Security Architecture
   - Authentication/Authorization
   - Data protection
   - Security boundaries

Format as comprehensive markdown documentation.
"""
        
        response = await self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192,
            temperature=0.3
        )
        
        return response.content[0].text
```

### 8.2 Documentation Templates

```python
DOCUMENTATION_TEMPLATES = {
    "readme": """# {project_name}

{project_description}

## 🚀 Quick Start

```bash
# Installation
{installation_commands}

# Configuration
{configuration_steps}

# Run
{run_commands}
```

## 📋 Features

{features_list}

## 🏗️ Architecture

{architecture_overview}

## 📖 Documentation

- [Architecture Guide](docs/architecture.md)
- [API Reference](docs/api.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment.md)

## 🧪 Testing

{testing_instructions}

## 🤝 Contributing

{contributing_guidelines}

## 📄 License

{license_info}
""",
    
    "api_endpoint": """## {method} {path}

### Description
{description}

### Authentication
{auth_requirements}

### Request

#### Headers
```
{headers}
```

#### Parameters
{parameters_table}

#### Body
```json
{request_body_example}
```

### Response

#### Success Response (200)
```json
{success_response_example}
```

#### Error Responses
{error_responses}

### Example Usage

```{language}
{code_example}
```

### Notes
{additional_notes}
"""
}
```

## 9. Enhanced CLI Implementation

### 9.1 Advanced CLI Commands

```python
@cli.command()
@click.argument('spec_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--project-name', '-n', help='Project name')
@click.option('--model', '-m', default='claude-opus-4-20250514')
@click.option('--max-cost', type=float, default=100.0)
@click.option('--phases', '-p', multiple=True, help='Specific phases to execute')
@click.option('--dry-run', is_flag=True, help='Show plan without executing')
@click.option('--no-tests', is_flag=True, help='Skip test execution')
@click.option('--verbose', '-v', count=True, help='Increase verbosity')
@click.option('--continue-on-error', is_flag=True, help='Continue on errors')
@click.option('--custom-mcp', type=click.Path(), help='Custom MCP config file')
@click.option('--parallel-tasks', type=int, default=1, help='Parallel task execution')
async def init(
    spec_file: str,
    output_dir: Optional[str],
    project_name: Optional[str],
    model: str,
    max_cost: float,
    phases: List[str],
    dry_run: bool,
    no_tests: bool,
    verbose: int,
    continue_on_error: bool,
    custom_mcp: Optional[str],
    parallel_tasks: int
):
    """Initialize and build a new project from specification"""
    
    # Set up logging based on verbosity
    setup_logging(verbosity=verbose)
    logger = structlog.get_logger()
    
    # Display startup banner
    console = Console()
    console.print(Panel.fit(
        f"[bold cyan]Claude Code Builder v{__version__}[/bold cyan]\n"
        f"[dim]Building from: {spec_file}[/dim]",
        title="🚀 Starting Build",
        border_style="cyan"
    ))
    
    try:
        # Load and validate specification
        spec_loader = SpecificationLoader()
        spec = await spec_loader.load(spec_file)
        
        logger.info(
            "specification_loaded",
            size_bytes=spec.size_bytes,
            estimated_tokens=spec.estimated_tokens
        )
        
        # Handle large specifications
        if spec.estimated_tokens > 100000:
            console.print(
                "[yellow]⚠️  Large specification detected. "
                "Will use chunking strategy.[/yellow]"
            )
            
        # Create or determine output directory
        output_manager = OutputManager()
        project_dir = await output_manager.create_project_directory(
            project_name or spec.inferred_name,
            Path(output_dir) if output_dir else None
        )
        
        console.print(
            f"[green]✓[/green] Project directory: {project_dir.path}"
        )
        
        # Check for resume capability
        if project_dir.can_resume:
            if Confirm.ask(
                f"Found existing project. Resume from {project_dir.last_phase}?"
            ):
                return await resume_build(project_dir)
                
        # Initialize comprehensive logger
        comp_logger = ComprehensiveLogger(project_dir)
        await comp_logger.start_session()
        
        # Load custom MCP configuration if provided
        mcp_config = DEFAULT_MCP_SERVERS.copy()
        if custom_mcp:
            custom_config = await load_custom_mcp_config(custom_mcp)
            mcp_config.update(custom_config)
            
        # Phase 1: Specification Analysis
        with console.status("[bold cyan]Analyzing specification..."):
            analyzer = SpecAnalyzer(model="claude-3-opus-20240229")
            analysis = await analyzer.analyze(spec.content)
            
            await comp_logger.log_api_call(analyzer.last_api_call)
            
        console.print("[green]✓[/green] Specification analyzed")
        console.print(f"  Project Type: {analysis.project_type}")
        console.print(f"  Complexity: {analysis.complexity}")
        console.print(f"  Estimated Hours: {analysis.estimated_hours}")
        
        # Phase 2: Task Generation
        with console.status("[bold cyan]Generating task breakdown..."):
            task_gen = TaskGenerator(model="claude-3-opus-20240229")
            task_breakdown = await task_gen.generate(analysis)
            
            await comp_logger.log_api_call(task_gen.last_api_call)
            
        console.print(f"[green]✓[/green] Generated {len(task_breakdown.phases)} phases")
        console.print(f"  Total Tasks: {task_breakdown.total_tasks}")
        
        # Phase 3: Acceptance Criteria Generation  
        with console.status("[bold cyan]Generating acceptance criteria..."):
            criteria_gen = AcceptanceCriteriaGenerator()
            all_criteria = {}
            
            for phase in task_breakdown.phases:
                criteria = await criteria_gen.generate_criteria(phase, spec)
                all_criteria[phase.id] = criteria
                
        console.print("[green]✓[/green] Generated acceptance criteria for all phases")
        
        # Phase 4: Custom Instructions Generation
        with console.status("[bold cyan]Generating custom AI instructions..."):
            instruction_builder = InstructionBuilder()
            instructions = await instruction_builder.build(
                analysis,
                task_breakdown,
                mcp_config,
                all_criteria
            )
            
            await comp_logger.log_api_call(instruction_builder.last_api_call)
            
        console.print("[green]✓[/green] Generated custom instructions")
        
        # Save all artifacts
        await project_dir.save_artifacts({
            "specification": spec,
            "analysis": analysis,
            "task_breakdown": task_breakdown,
            "acceptance_criteria": all_criteria,
            "custom_instructions": instructions,
            "mcp_config": mcp_config
        })
        
        if dry_run:
            display_execution_plan(
                task_breakdown,
                all_criteria,
                estimated_cost=calculate_estimated_cost(task_breakdown)
            )
            return
            
        # Phase 5: Execute Implementation
        executor = ClaudeCodeExecutor(
            model=model,
            max_cost=max_cost,
            project_dir=project_dir,
            logger=comp_logger,
            continue_on_error=continue_on_error,
            parallel_tasks=parallel_tasks
        )
        
        # Execute phases
        phases_to_execute = phases or [p.id for p in task_breakdown.phases]
        
        for phase_id in phases_to_execute:
            phase = task_breakdown.get_phase(phase_id)
            criteria = all_criteria[phase_id]
            
            console.rule(f"[bold cyan]Phase: {phase.name}[/bold cyan]")
            
            # Load context for phase
            context = await load_phase_context(phase, spec, project_dir)
            
            # Execute phase
            result = await executor.execute_phase(phase, context)
            
            if result.status == "success":
                console.print(f"[green]✓[/green] Phase completed successfully")
                
                # Run acceptance tests unless skipped
                if not no_tests:
                    console.print("[cyan]Running acceptance tests...[/cyan]")
                    
                    test_runner = ProductionTestRunner(project_dir)
                    test_results = await test_runner.run_acceptance_tests(
                        criteria,
                        project_dir.source_path
                    )
                    
                    if test_results.all_passed:
                        console.print(
                            f"[green]✓[/green] All {test_results.total_tests} "
                            f"acceptance tests passed"
                        )
                    else:
                        console.print(
                            f"[red]✗[/red] {test_results.failed_count} "
                            f"tests failed"
                        )
                        
                        if not continue_on_error:
                            raise TestFailure(test_results.failure_summary)
                            
            else:
                console.print(f"[red]✗[/red] Phase failed: {result.error}")
                
                if not continue_on_error:
                    raise PhaseExecutionError(phase.name, result.error)
                    
        # Phase 6: Generate Documentation
        console.rule("[bold cyan]Generating Documentation[/bold cyan]")
        
        with console.status("[bold cyan]Creating project documentation..."):
            doc_gen = DocumentationGenerator()
            documentation = await doc_gen.generate_project_documentation(
                project_dir.load_project(),
                project_dir.load_implementation()
            )
            
            await documentation.save_to_directory(project_dir.docs_path)
            
        console.print("[green]✓[/green] Documentation generated")
        
        # Final Summary
        console.rule("[bold green]Build Complete[/bold green]")
        
        summary = await generate_build_summary(project_dir)
        console.print(summary)
        
        # Save final state
        await project_dir.save_final_state()
        
    except Exception as e:
        logger.exception("build_failed")
        console.print(f"[red]Build failed: {str(e)}[/red]")
        
        if verbose > 0:
            console.print_exception()
            
        raise click.ClickException(str(e))
```

### 9.2 Resume Command Implementation

```python
@cli.command()
@click.argument('project_dir', type=click.Path(exists=True))
@click.option('--from-phase', help='Resume from specific phase')
@click.option('--from-task', help='Resume from specific task')
@click.option('--rerun-tests', is_flag=True, help='Rerun previous tests')
@click.option('--update-spec', type=click.Path(), help='Update specification')
async def resume(
    project_dir: str,
    from_phase: Optional[str],
    from_task: Optional[str],
    rerun_tests: bool,
    update_spec: Optional[str]
):
    """Resume an existing project build"""
    
    console = Console()
    project_path = Path(project_dir)
    
    try:
        # Load project state
        project = await ProjectDirectory.load(project_path)
        
        console.print(Panel.fit(
            f"[bold cyan]Resuming: {project.metadata.project_name}[/bold cyan]\n"
            f"[dim]Created: {project.metadata.created_at}[/dim]\n"
            f"[dim]Last checkpoint: {project.state.last_checkpoint}[/dim]",
            title="📂 Project Resume",
            border_style="cyan"
        ))
        
        # Display current progress
        progress_table = Table(title="Progress Summary")
        progress_table.add_column("Phase", style="cyan")
        progress_table.add_column("Status", style="green")
        progress_table.add_column("Tasks", justify="right")
        
        for phase in project.task_breakdown.phases:
            status = "✓ Complete" if phase.id in project.state.completed_phases else "○ Pending"
            task_count = f"{project.state.phase_task_count(phase.id)}/{len(phase.tasks)}"
            progress_table.add_row(phase.name, status, task_count)
            
        console.print(progress_table)
        
        # Check for specification update
        if update_spec:
            console.print(
                "[yellow]⚠️  Specification update detected. "
                "This may invalidate completed work.[/yellow]"
            )
            
            if Confirm.ask("Continue with specification update?"):
                await update_project_specification(project, update_spec)
                
        # Determine resume point
        resume_point = determine_resume_point(
            project.state,
            from_phase,
            from_task
        )
        
        console.print(
            f"\n[cyan]Resuming from: {resume_point.description}[/cyan]"
        )
        
        # Rerun tests if requested
        if rerun_tests:
            await rerun_acceptance_tests(project, resume_point)
            
        # Continue execution
        executor = ClaudeCodeExecutor.from_project(project)
        await executor.resume_from(resume_point)
        
    except Exception as e:
        console.print(f"[red]Resume failed: {str(e)}[/red]")
        raise click.ClickException(str(e))
```

## 10. Performance and Resource Management

### 10.1 Token and Cost Tracking

```python
class ResourceTracker:
    """Track tokens, costs, and resource usage"""
    
    def __init__(self, max_cost: float, max_tokens: int = 10_000_000):
        self.max_cost = max_cost
        self.max_tokens = max_tokens
        self.current_cost = 0.0
        self.current_tokens = 0
        self.cost_breakdown = defaultdict(float)
        self.token_breakdown = defaultdict(int)
        self.logger = structlog.get_logger()
        
    async def track_api_call(self, api_call: APICall):
        """Track resource usage from API call"""
        # Calculate cost
        cost = self._calculate_cost(
            api_call.model,
            api_call.tokens_in,
            api_call.tokens_out
        )
        
        # Update totals
        self.current_cost += cost
        self.current_tokens += api_call.tokens_total
        
        # Update breakdowns
        self.cost_breakdown[api_call.agent_type] += cost
        self.token_breakdown[api_call.agent_type] += api_call.tokens_total
        
        # Log usage
        self.logger.info(
            "resource_usage",
            total_cost=self.current_cost,
            total_tokens=self.current_tokens,
            remaining_budget=self.max_cost - self.current_cost,
            cost_by_agent=dict(self.cost_breakdown)
        )
        
        # Check limits
        if self.current_cost >= self.max_cost:
            raise ResourceLimitExceeded(
                f"Cost limit exceeded: ${self.current_cost:.2f} >= ${self.max_cost:.2f}"
            )
            
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate cost based on model and token usage"""
        # Opus 4 pricing (example rates)
        rates = {
            "claude-opus-4-20250514": {
                "input": 0.015 / 1000,   # $15 per million tokens
                "output": 0.075 / 1000   # $75 per million tokens
            },
            "claude-3-opus-20240229": {
                "input": 0.015 / 1000,
                "output": 0.075 / 1000
            }
        }
        
        model_rates = rates.get(model, rates["claude-3-opus-20240229"])
        
        input_cost = tokens_in * model_rates["input"]
        output_cost = tokens_out * model_rates["output"]
        
        return input_cost + output_cost
```

## 11. Error Handling and Recovery

### 11.1 Comprehensive Error Management

```python
class ErrorRecoverySystem:
    """Handle errors with intelligent recovery strategies"""
    
    def __init__(self, project_state: ProjectState):
        self.project_state = project_state
        self.recovery_strategies = {
            ErrorType.API_RATE_LIMIT: self._handle_rate_limit,
            ErrorType.API_ERROR: self._handle_api_error,
            ErrorType.CONTEXT_OVERFLOW: self._handle_context_overflow,
            ErrorType.MCP_SERVER_ERROR: self._handle_mcp_error,
            ErrorType.EXECUTION_TIMEOUT: self._handle_timeout,
            ErrorType.FILE_CONFLICT: self._handle_file_conflict,
            ErrorType.TEST_FAILURE: self._handle_test_failure,
            ErrorType.RESOURCE_LIMIT: self._handle_resource_limit
        }
        
    async def handle_error(
        self, 
        error: Exception, 
        context: ExecutionContext
    ) -> RecoveryAction:
        """Determine and execute recovery strategy"""
        error_type = self._classify_error(error)
        strategy = self.recovery_strategies.get(
            error_type,
            self._handle_unknown_error
        )
        
        self.logger.error(
            "handling_error",
            error_type=error_type,
            error_message=str(error),
            phase=context.current_phase,
            task=context.current_task
        )
        
        return await strategy(error, context)
        
    async def _handle_context_overflow(
        self, 
        error: ContextOverflowError,
        context: ExecutionContext
    ) -> RecoveryAction:
        """Handle context window overflow"""
        self.logger.info("handling_context_overflow")
        
        # Strategy 1: Summarize previous context
        summarizer = ContextSummarizer()
        summarized_context = await summarizer.summarize(
            context.full_context,
            preserve_sections=context.critical_sections
        )
        
        # Strategy 2: Archive completed work
        archiver = ContextArchiver()
        await archiver.archive_completed(
            context.completed_tasks,
            self.project_state.memory_dir
        )
        
        # Strategy 3: Reload with optimized context
        optimized_context = await self._rebuild_context(
            summarized_context,
            context.current_task
        )
        
        return RecoveryAction(
            action_type="retry_with_optimized_context",
            modified_context=optimized_context,
            retry_count=1,
            log_message="Context optimized and retrying"
        )
```

## 12. Security and Compliance

### 12.1 Secure Configuration Management

```python
class SecureConfigManager:
    """Manage sensitive configuration securely"""
    
    def __init__(self):
        self.keyring = keyring.get_keyring()
        self.env_prefix = "CLAUDE_CODE_BUILDER_"
        
    async def get_api_key(self, service: str) -> str:
        """Retrieve API key with fallback chain"""
        # 1. Environment variable
        env_key = f"{self.env_prefix}{service.upper()}_API_KEY"
        if env_value := os.getenv(env_key):
            return env_value
            
        # 2. Keyring
        if keyring_value := self.keyring.get_password("claude-code-builder", service):
            return keyring_value
            
        # 3. Config file (encrypted)
        if config_value := await self._load_from_encrypted_config(service):
            return config_value
            
        # 4. Prompt user
        return await self._prompt_for_key(service)
        
    async def store_api_key(self, service: str, key: str, persistent: bool = True):
        """Store API key securely"""
        if persistent:
            self.keyring.set_password("claude-code-builder", service, key)
        else:
            os.environ[f"{self.env_prefix}{service.upper()}_API_KEY"] = key
```

## 13. Monitoring and Analytics

### 13.1 Build Analytics

```python
class BuildAnalytics:
    """Collect and analyze build metrics"""
    
    def __init__(self, project_dir: ProjectDirectory):
        self.project_dir = project_dir
        self.metrics = BuildMetrics()
        
    async def generate_analytics_report(self) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        report = AnalyticsReport()
        
        # Performance metrics
        report.performance = PerformanceMetrics(
            total_duration=self.metrics.total_duration,
            phase_durations=self.metrics.phase_durations,
            task_durations=self.metrics.task_durations,
            api_latencies=self.metrics.api_latencies
        )
        
        # Resource usage
        report.resources = ResourceMetrics(
            total_tokens=self.metrics.total_tokens,
            tokens_by_phase=self.metrics.tokens_by_phase,
            total_cost=self.metrics.total_cost,
            cost_by_agent=self.metrics.cost_by_agent
        )
        
        # Quality metrics
        report.quality = QualityMetrics(
            test_pass_rate=self.metrics.test_pass_rate,
            acceptance_criteria_met=self.metrics.criteria_met_count,
            error_count=self.metrics.error_count,
            recovery_success_rate=self.metrics.recovery_success_rate
        )
        
        # MCP usage
        report.mcp_usage = MCPUsageMetrics(
            calls_by_server=self.metrics.mcp_calls,
            compliance_rate=self.metrics.mcp_compliance_rate
        )
        
        return report
```

## 14. Integration Examples

### 14.1 Complete Build Example

```python
# Example: Building a full-stack application
async def build_fullstack_app():
    """Example of building a complete full-stack application"""
    
    # Create specification
    spec_content = """
    # Task Management System
    
    Build a production-ready task management system with:
    - FastAPI backend with PostgreSQL
    - React frontend with TypeScript
    - Real-time updates via WebSockets
    - JWT authentication
    - Role-based access control
    - Full-text search with Elasticsearch
    - Redis caching
    - Docker deployment
    
    ## Acceptance Criteria
    - Users can register and authenticate
    - Tasks support CRUD operations
    - Real-time updates across clients
    - Search returns results in <100ms
    - System handles 1000 concurrent users
    """
    
    # Run build
    result = await subprocess.run([
        "claude-code-builder",
        "init",
        "-",  # Read from stdin
        "--project-name", "task-manager",
        "--output-dir", "./projects/task-manager",
        "--model", "claude-opus-4-20250514",
        "--max-cost", "75.0",
        "--verbose", "-vv"
    ], input=spec_content.encode())
    
    # Monitor output
    # The CLI will stream:
    # - Specification analysis results
    # - Task breakdown (likely 6-8 phases)
    # - Real-time progress for each phase
    # - Test execution results
    # - Documentation generation
    # - Final summary with metrics
```

### 14.2 Custom MCP Integration

```python
# custom_mcp_config.yaml
mcp_servers:
  code-reviewer:
    command: "node"
    args: ["./mcp-servers/code-reviewer/index.js"]
    description: "Automated code review"
    required: true
    enforce_at:
      - "task_complete"
      - "phase_complete"
      
  security-scanner:
    command: "python"
    args: ["-m", "security_scanner_mcp"]
    description: "Security vulnerability scanning"
    required: true
    enforce_at:
      - "phase_complete"
      - "before_deployment"
```

## 15. Conclusion

Claude Code Builder provides a comprehensive, production-ready solution for automated software development. Key features include:

1. **Large Specification Support**: Handles specs of any size through intelligent chunking
2. **Production-Only Testing**: No mocks, only real-world validation
3. **MCP-First Development**: Mandatory use of MCP servers for consistency
4. **Complete Transparency**: Every decision and action is logged
5. **Intelligent Resume**: Continue exactly where you left off
6. **Built-in Documentation**: Comprehensive docs generated alongside code

The system ensures that every project built is production-ready, fully tested, and thoroughly documented.