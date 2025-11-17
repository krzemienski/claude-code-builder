# Dynamic Skill Generation & Self-Improvement System

## Feature 6: Intelligent Skill Discovery, Generation & Testing

### The Problem
Current approach assumes all skills exist upfront. But what if:
- User requests a specific framework/library combination not in our skill library
- Project needs domain-specific patterns (e.g., "Stripe + FastAPI + webhook handling")
- New technologies emerge (e.g., a new web framework)
- Organization has internal patterns to codify

### The Solution: Self-Improving Skill Engine

The system should **analyze the spec**, **identify needed skills**, **generate them if missing**, **test them**, and **use them in the build**.

## Architecture: Skill Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    1. SPEC ANALYSIS                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Identify:                                              │ │
│  │ - Technologies mentioned (FastAPI, React, Kafka, etc.) │ │
│  │ - Patterns needed (auth, payment, real-time, etc.)    │ │
│  │ - Domain requirements (healthcare, fintech, etc.)     │ │
│  │ - Integration points (Stripe, Twilio, AWS, etc.)      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 2. SKILL DISCOVERY                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Check:                                                 │ │
│  │ ✓ Built-in skills (python-fastapi-builder, etc.)     │ │
│  │ ✓ User-installed skills (~/.claude/skills/)          │ │
│  │ ✓ Marketplace skills (if connected)                   │ │
│  │ ✓ Organization skills (private registry)              │ │
│  │                                                        │ │
│  │ Gap Analysis:                                          │ │
│  │ ❌ Missing: fastapi-stripe-webhooks skill             │ │
│  │ ❌ Missing: kafka-fastapi-integration skill           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              3. DYNAMIC SKILL GENERATION                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ For each missing skill:                                │ │
│  │                                                        │ │
│  │ 1. Generate SKILL.md with YAML frontmatter            │ │
│  │ 2. Create example implementations                     │ │
│  │ 3. Add testing templates                              │ │
│  │ 4. Include best practices documentation               │ │
│  │ 5. Generate validation tests                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  4. SKILL VALIDATION                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Test generated skill:                                  │ │
│  │ ✓ SKILL.md has valid YAML frontmatter                │ │
│  │ ✓ Instructions are clear and actionable               │ │
│  │ ✓ Examples compile/run successfully                   │ │
│  │ ✓ Generated code passes linting                       │ │
│  │ ✓ Integration test validates the pattern              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  5. SKILL USAGE IN BUILD                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Use skill in current build:                           │ │
│  │ - Load skill instructions                             │ │
│  │ - Apply patterns to generated code                    │ │
│  │ - Generate tests using skill templates                │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                6. SKILL PERSISTENCE & LEARNING               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ After successful build:                                │ │
│  │ ✓ Save skill to ~/.claude/skills/generated/          │ │
│  │ ✓ Track usage count and success rate                  │ │
│  │ ✓ Refine skill based on feedback                      │ │
│  │ ✓ Optionally publish to marketplace                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Implementation: Skill Generation Agent

### New Agent: `SkillGenerator`

```python
class SkillGenerator(BaseAgent):
    """Dynamically generates skills based on project requirements."""

    async def analyze_skill_gaps(
        self,
        spec: str,
        existing_skills: List[SkillMetadata]
    ) -> List[SkillGap]:
        """Identify missing skills needed for the spec.

        Args:
            spec: Project specification
            existing_skills: Currently available skills

        Returns:
            List of skill gaps with metadata
        """
        prompt = f"""Analyze this specification and identify needed skills:

{spec}

Available skills:
{self._format_skill_list(existing_skills)}

For each missing skill needed, provide:
1. Skill name (kebab-case)
2. Description (what it does, when to use)
3. Technologies involved
4. Patterns it should encode
5. Integration points

Format as JSON array of skill gaps."""

        response = await self.query(prompt)
        return self._parse_skill_gaps(response)

    async def generate_skill(
        self,
        skill_gap: SkillGap,
        research_context: Optional[str] = None
    ) -> GeneratedSkill:
        """Generate a complete skill from scratch.

        Args:
            skill_gap: Description of missing skill
            research_context: Optional context from docs/web research

        Returns:
            GeneratedSkill with SKILL.md and resources
        """
        # Step 1: Research (if context not provided)
        if not research_context:
            research_context = await self._research_skill(skill_gap)

        # Step 2: Generate SKILL.md
        skill_md = await self._generate_skill_md(skill_gap, research_context)

        # Step 3: Generate example implementations
        examples = await self._generate_examples(skill_gap, research_context)

        # Step 4: Generate tests for the skill itself
        tests = await self._generate_skill_tests(skill_gap, examples)

        return GeneratedSkill(
            name=skill_gap.name,
            skill_md=skill_md,
            examples=examples,
            tests=tests,
            metadata=skill_gap.metadata
        )

    async def _research_skill(self, skill_gap: SkillGap) -> str:
        """Research skill requirements using MCP servers.

        Uses:
        - context7 MCP: Research libraries/frameworks
        - fetch MCP: Get documentation from official sources
        - memory MCP: Check if we've seen similar patterns before
        """
        # Use context7 to research the technology
        tech_context = await self.mcp.context7.research(
            query=f"{skill_gap.technologies} best practices patterns"
        )

        # Fetch official docs if URLs provided
        docs = []
        for url in skill_gap.doc_urls:
            doc_content = await self.mcp.fetch.get(url)
            docs.append(doc_content)

        # Check memory for similar patterns
        similar_patterns = await self.mcp.memory.search_nodes(
            query=f"skill patterns {skill_gap.technologies}",
            limit=5
        )

        return self._synthesize_research(tech_context, docs, similar_patterns)

    async def _generate_skill_md(
        self,
        skill_gap: SkillGap,
        research: str
    ) -> str:
        """Generate SKILL.md file content."""
        prompt = f"""Generate a complete SKILL.md file for:

Skill Name: {skill_gap.name}
Description: {skill_gap.description}
Technologies: {skill_gap.technologies}

Research Context:
{research}

The SKILL.md should include:
1. YAML frontmatter (name, description)
2. Overview of what the skill does
3. Project structure it creates
4. Key patterns and best practices
5. Code examples (actual working code)
6. When to use / when not to use
7. Generated files checklist

Make it comprehensive and production-ready."""

        return await self.query(prompt)

    async def _generate_examples(
        self,
        skill_gap: SkillGap,
        research: str
    ) -> Dict[str, str]:
        """Generate example implementations."""
        # Generate 2-3 example files showing the pattern
        examples = {}

        for example_type in ["basic", "with_auth", "production"]:
            prompt = f"""Generate a {example_type} example for {skill_gap.name}.

This should be real, working code demonstrating the pattern.

Context: {research}"""

            code = await self.query(prompt)
            examples[f"example_{example_type}.py"] = code

        return examples

    async def _generate_skill_tests(
        self,
        skill_gap: SkillGap,
        examples: Dict[str, str]
    ) -> Dict[str, str]:
        """Generate tests that validate the skill works."""
        tests = {}

        # Test that examples are valid
        tests["test_examples.py"] = await self.query(f"""
Generate pytest tests that validate these examples work:

{self._format_examples(examples)}

Tests should:
- Import and run the examples
- Check they produce expected output
- Validate key patterns are present
""")

        # Test that skill instructions are actionable
        tests["test_skill_instructions.py"] = await self.query(f"""
Generate a test that validates the SKILL.md instructions by:
1. Following the instructions step-by-step
2. Generating a small project using the skill
3. Verifying the project structure matches expectations
4. Running basic functionality tests
""")

        return tests

    async def validate_skill(self, skill: GeneratedSkill) -> SkillValidationResult:
        """Validate a generated skill before use.

        Checks:
        1. SKILL.md has valid YAML frontmatter
        2. Instructions are clear and complete
        3. Examples compile and run
        4. Tests pass
        5. Generated code passes linting
        """
        results = []

        # Validate YAML frontmatter
        results.append(await self._validate_yaml(skill.skill_md))

        # Run skill tests
        results.append(await self._run_skill_tests(skill))

        # Lint examples
        results.append(await self._lint_examples(skill.examples))

        # Integration test: use skill to generate a mini-project
        results.append(await self._integration_test_skill(skill))

        return SkillValidationResult(
            valid=all(r.passed for r in results),
            results=results
        )
```

## Usage Flow

### Example 1: Building Stripe Integration

```bash
# User runs:
claude-code-builder build stripe-payment-api.md

# System flow:
[Spec Analysis]
  ✓ Detected: FastAPI + Stripe + webhook handling
  ✓ Existing skills: python-fastapi-builder
  ✗ Missing skill: fastapi-stripe-webhooks

[Skill Generation]
  → Researching Stripe webhooks best practices...
  → Using context7 MCP to research Stripe API patterns
  → Fetching Stripe webhook docs
  → Generating skill: fastapi-stripe-webhooks
  → Creating SKILL.md with:
     - Webhook signature verification
     - Event handling patterns
     - Idempotency handling
     - Retry logic
  → Generating examples:
     - Basic webhook endpoint
     - With signature verification
     - Production-ready with error handling
  → Generating validation tests

[Skill Validation]
  ✓ YAML frontmatter valid
  ✓ Examples compile successfully
  ✓ Integration test passed
  ✓ Skill ready to use

[Build Execution]
  → Using python-fastapi-builder for base structure
  → Using fastapi-stripe-webhooks for payment integration
  → Generated complete payment API with:
     ✓ Webhook endpoint (/webhooks/stripe)
     ✓ Signature verification
     ✓ Event handling (payment_intent.succeeded, etc.)
     ✓ Idempotent processing
     ✓ Comprehensive tests

[Skill Persistence]
  ✓ Saved to ~/.claude/skills/generated/fastapi-stripe-webhooks/
  ✓ Available for future builds
  ✓ Usage count: 1, Success rate: 100%
```

### Example 2: New Framework Combination

```bash
# User runs:
claude-code-builder build "Build a real-time chat using FastAPI + WebSockets + Redis Pub/Sub"

# System flow:
[Spec Analysis]
  ✓ Detected: FastAPI + WebSockets + Redis Pub/Sub
  ✗ Missing skill: fastapi-websocket-redis-pubsub

[Skill Generation]
  → Researching WebSocket + Redis patterns...
  → Generating skill with:
     - WebSocket connection management
     - Redis pub/sub integration
     - Room-based messaging
     - Connection lifecycle (connect, disconnect, reconnect)
     - Horizontal scaling patterns
  → Examples include:
     - Basic chat server
     - With authentication
     - Multi-room support
     - Presence tracking

[Build Execution]
  → Complete real-time chat API generated
  → With Redis pub/sub for scaling
  → WebSocket tests using pytest-asyncio

[Learning]
  → Skill saved for future real-time projects
  → Can be refined based on usage feedback
```

## Skill Improvement Loop

```
User Build → Skill Generated → Build Succeeds/Fails
                                      ↓
                              Feedback Collected
                                      ↓
                              Skill Refined ← AI Analysis
                                      ↓
                              Updated Skill Saved
                                      ↓
                              Better Next Build
```

### Skill Refinement

```python
class SkillRefiner:
    """Refines skills based on usage feedback."""

    async def refine_skill(
        self,
        skill: GeneratedSkill,
        feedback: SkillUsageFeedback
    ) -> GeneratedSkill:
        """Refine skill based on real-world usage.

        Feedback includes:
        - Build success/failure
        - Linting errors encountered
        - Tests that failed
        - User modifications to generated code
        """
        if not feedback.successful:
            # Analyze what went wrong
            issues = await self._analyze_failures(feedback)

            # Update skill to avoid these issues
            updated_skill = await self._apply_fixes(skill, issues)

            # Re-validate
            validation = await self.validator.validate_skill(updated_skill)

            if validation.valid:
                return updated_skill

        # Even for successful builds, learn from modifications
        if feedback.user_modifications:
            insights = await self._extract_insights(feedback.user_modifications)
            return await self._incorporate_insights(skill, insights)

        return skill
```

## CLI Integration

### New Commands

```bash
# Analyze what skills would be needed (without building)
claude-code-builder analyze-skills spec.md
# Output:
#   Existing skills:
#     ✓ python-fastapi-builder
#     ✓ test-strategy-selector
#
#   Skills to generate:
#     → fastapi-stripe-webhooks
#     → fastapi-kafka-integration

# Generate specific skill
claude-code-builder skills generate fastapi-stripe-webhooks \
  --technologies "FastAPI,Stripe,webhooks" \
  --description "Stripe webhook integration with signature verification"

# Test a generated skill
claude-code-builder skills test ~/.claude/skills/generated/fastapi-stripe-webhooks

# Refine a skill based on feedback
claude-code-builder skills refine fastapi-stripe-webhooks \
  --feedback-file ./build-feedback.json

# Show generated skills
claude-code-builder skills list --generated
# Output:
#   Generated Skills:
#   - fastapi-stripe-webhooks (used 5 times, 100% success)
#   - fastapi-kafka-integration (used 2 times, 100% success)
#   - nextjs-realtime-updates (used 1 time, 100% success)

# Publish a generated skill to marketplace
claude-code-builder skills publish fastapi-stripe-webhooks \
  --visibility public \
  --category payments
```

## Configuration

```yaml
# ~/.claude/skills/config.yml
skill_generation:
  enabled: true
  auto_validate: true
  save_generated: true
  refine_on_feedback: true

  research:
    use_context7: true
    use_fetch_mcp: true
    use_memory_mcp: true

  testing:
    run_examples: true
    run_integration_tests: true
    lint_generated_code: true

  persistence:
    location: "~/.claude/skills/generated/"
    version_control: true  # Git track generated skills

  marketplace:
    auto_publish: false  # Manual approval for publishing
    organization: "my-company"  # Private org registry
```

## Benefits

### 1. Handles Novel Combinations
```
User: "Build API with FastAPI + Temporal + Stripe + Twilio"

Traditional: ❌ No skill exists for this specific combo
v3 with Skill Gen: ✅ Generates compound skill on-the-fly
```

### 2. Keeps Pace with Technology
```
New Framework Released: Bun + Hono web framework

Traditional: ❌ Wait for CCB update
v3 with Skill Gen: ✅ Researches and generates skill automatically
```

### 3. Organization-Specific Patterns
```
Company: "We always use Auth0 + FastAPI + PostgreSQL with multi-tenancy"

Traditional: ❌ Configure every time
v3 with Skill Gen: ✅ Generates company-specific skill once, reuses forever
```

### 4. Self-Improving
```
Build 1: Generated skill works but tests are basic
Build 2: Same skill, refined based on Build 1 feedback
Build 3: Skill now includes edge cases discovered in Builds 1-2
Build 10: Skill is production-grade from community usage
```

### 5. Knowledge Capture
```
Senior Dev: "I always set up FastAPI projects this specific way"

Traditional: ❌ Knowledge stays in their head
v3 with Skill Gen: ✅ System observes, generates skill, everyone benefits
```

## Integration with MCP Discovery Pattern

The skill generation system mirrors MCP discovery:

**MCP Discovery:**
1. Analyze what MCPs are needed (filesystem, memory, git)
2. Connect to required MCPs
3. Use them during build

**Skill Discovery:**
1. Analyze what skills are needed
2. Generate missing skills (using MCPs for research!)
3. Use them during build

**Synergy:**
```
Skill Generation uses MCPs to research:
- context7: Research technologies and patterns
- fetch: Get official documentation
- memory: Check for similar past patterns
- filesystem: Save generated skills
- git: Version control skills
```

## Technical Implementation

### Database Schema for Skill Tracking

```sql
CREATE TABLE generated_skills (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    technologies JSON,  -- ["FastAPI", "Stripe", "webhooks"]

    skill_md_content TEXT,
    examples JSON,  -- {"example_basic.py": "...", ...}

    generated_at TIMESTAMP,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,

    version INTEGER DEFAULT 1,
    parent_skill_id UUID REFERENCES generated_skills(id),  -- For refinements

    feedback JSON,  -- Collected feedback from builds
    metadata JSON
);

CREATE TABLE skill_usage (
    id UUID PRIMARY KEY,
    skill_id UUID REFERENCES generated_skills(id),
    build_id UUID,

    successful BOOLEAN,
    feedback TEXT,
    modifications JSON,  -- User changes to generated code

    created_at TIMESTAMP
);
```

### Metrics Dashboard

```
Generated Skills Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Generated Skills: 47
Active Skills (used in last 30 days): 23
Average Success Rate: 94%

Top Skills by Usage:
1. fastapi-stripe-webhooks (23 uses, 100% success)
2. nextjs-realtime-updates (15 uses, 93% success)
3. django-multi-tenant (12 uses, 100% success)

Recently Generated:
- fastapi-temporal-workflows (2 hours ago)
- react-native-offline-sync (5 hours ago)

Skills Pending Validation:
- golang-grpc-gateway (awaiting integration test)
```

## Success Metrics

- **Skill Generation Success Rate**: >90% of generated skills pass validation
- **Build Success with Generated Skills**: >85% first-time success
- **Time to Generate Skill**: <5 minutes from research to validated skill
- **Skill Reuse Rate**: 70% of generated skills used in multiple builds
- **Community Contribution**: 30% of generated skills published to marketplace

## Summary

Dynamic skill generation transforms CCB v3 from a tool with **fixed capabilities** to a **self-improving platform** that:

1. **Discovers** what skills are needed from the spec
2. **Generates** missing skills using AI + MCP research
3. **Validates** skills work correctly before use
4. **Uses** skills to build the project
5. **Learns** from feedback to refine skills
6. **Shares** valuable skills with the community

This creates a **positive feedback loop** where every build makes the system smarter and more capable.

## Claude Agent SDK Integration

### How Generated Skills Are Used During Build

The generated skills are not just documentation - they're **actively loaded and used** by Claude via the Agent SDK's skills system.

### SDK Skills API Integration

```python
from claude_agent_sdk import query, create_sdk_mcp_server
from pathlib import Path

class SDKSkillsOrchestrator:
    """Orchestrates skill usage via Claude Agent SDK."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.generated_skills_dir = Path.home() / ".claude" / "skills" / "generated"

    async def build_with_skills(
        self,
        spec: str,
        required_skills: List[str],
        generated_skills: List[GeneratedSkill]
    ) -> BuildResult:
        """Execute build using both existing and generated skills via SDK.

        This is the KEY integration - generated skills are loaded into
        Claude's context via the SDK's skills system.
        """

        # Step 1: Save generated skills to filesystem
        for skill in generated_skills:
            await self._save_skill_to_filesystem(skill)

        # Step 2: Configure SDK with skills directory
        # Claude Agent SDK will discover skills in this directory
        skill_paths = [
            str(Path.home() / ".claude" / "skills"),  # Built-in skills
            str(self.generated_skills_dir),  # Generated skills
        ]

        # Step 3: Create query with skills enabled
        # The SDK will automatically load skill metadata and make skills
        # available to Claude during the conversation
        messages = [
            {
                "role": "user",
                "content": f"""Build a project from this specification:

{spec}

You have access to these skills - use them when relevant:
{self._format_available_skills(required_skills + [s.name for s in generated_skills])}

Generate the complete project structure, code, tests, and deployment configs."""
            }
        ]

        # Step 4: Execute via SDK with skills
        async for chunk in query(
            messages=messages,
            api_key=self.api_key,
            # The skills are discovered automatically from the skills directory
            # Claude will load skill instructions when triggered by the conversation
        ):
            if chunk.type == "text":
                self._handle_generated_code(chunk.content)
            elif chunk.type == "tool_use":
                self._handle_tool_use(chunk)

        return BuildResult(success=True)

    async def _save_skill_to_filesystem(self, skill: GeneratedSkill) -> None:
        """Save generated skill to filesystem for SDK to discover.

        Claude Agent SDK discovers skills from filesystem:
        ~/.claude/skills/generated/{skill-name}/SKILL.md
        """
        skill_dir = self.generated_skills_dir / skill.name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md (required by SDK)
        (skill_dir / "SKILL.md").write_text(skill.skill_md)

        # Write examples (optional resources)
        examples_dir = skill_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        for filename, content in skill.examples.items():
            (examples_dir / filename).write_text(content)

        # Write tests (optional resources)
        tests_dir = skill_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        for filename, content in skill.tests.items():
            (tests_dir / filename).write_text(content)

        self.logger.info(
            "skill_saved_to_filesystem",
            skill=skill.name,
            path=str(skill_dir),
            discoverable_by_sdk=True
        )
```

### Skill Discovery Flow with SDK

```python
class BuildOrchestrator:
    """Main build orchestrator using SDK with dynamic skills."""

    async def execute_build(self, spec_path: Path) -> BuildResult:
        """Execute build with skill generation and SDK integration."""

        # Phase 1: Analyze spec and identify skill gaps
        spec = spec_path.read_text()
        skill_gaps = await self.skill_generator.analyze_skill_gaps(
            spec,
            existing_skills=self._get_available_skills()
        )

        # Phase 2: Generate missing skills
        generated_skills = []
        for gap in skill_gaps:
            self.logger.info("generating_skill", skill=gap.name)

            skill = await self.skill_generator.generate_skill(gap)

            # Validate before use
            validation = await self.skill_generator.validate_skill(skill)
            if not validation.valid:
                self.logger.error("skill_validation_failed", skill=gap.name)
                continue

            generated_skills.append(skill)
            self.logger.info("skill_generated_and_validated", skill=gap.name)

        # Phase 3: Execute build via SDK with ALL skills
        # (built-in + generated)
        result = await self.sdk_orchestrator.build_with_skills(
            spec=spec,
            required_skills=self._get_required_skill_names(spec),
            generated_skills=generated_skills
        )

        # Phase 4: Collect feedback for skill refinement
        if result.success:
            await self._record_skill_success(generated_skills)
        else:
            await self._refine_skills_from_failure(generated_skills, result)

        return result
```

### Real Example: SDK Using Generated Skill

When Claude Agent SDK processes the build:

```
┌─────────────────────────────────────────────────────────────┐
│ Claude Agent SDK Processing                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ User Request: "Build FastAPI API with Stripe webhooks"      │
│                                                              │
│ SDK Discovery Phase:                                         │
│   ✓ Found ~/.claude/skills/python-fastapi-builder/SKILL.md  │
│   ✓ Found ~/.claude/skills/generated/                       │
│         fastapi-stripe-webhooks/SKILL.md                    │
│                                                              │
│ Skill Metadata Loaded (Progressive Disclosure):             │
│   - python-fastapi-builder: ~100 tokens                     │
│   - fastapi-stripe-webhooks: ~100 tokens                    │
│                                                              │
│ Conversation Analysis:                                       │
│   "Stripe webhooks" → Matches fastapi-stripe-webhooks desc  │
│   "FastAPI API" → Matches python-fastapi-builder desc       │
│                                                              │
│ Skill Triggering:                                            │
│   1. Load python-fastapi-builder instructions (~3K tokens)  │
│   2. Load fastapi-stripe-webhooks instructions (~3K tokens) │
│                                                              │
│ Code Generation:                                             │
│   Using python-fastapi-builder patterns:                    │
│     → Created src/main.py with FastAPI app                  │
│     → Created src/routers/ directory                        │
│     → Created src/models.py with SQLAlchemy                 │
│                                                              │
│   Using fastapi-stripe-webhooks patterns:                   │
│     → Created src/routers/webhooks.py                       │
│     → Added signature verification function                 │
│     → Added event handler mapping                           │
│     → Created src/services/stripe_service.py                │
│                                                              │
│   Resources Accessed On-Demand:                             │
│     → Read examples/webhook_handler.py from skill           │
│     → Applied pattern to generated code                     │
│     → 0 additional tokens (filesystem access)               │
│                                                              │
│ Result:                                                      │
│   ✓ Complete FastAPI + Stripe webhook integration          │
│   ✓ Production-ready code with error handling               │
│   ✓ Tests included from skill templates                     │
│   ✓ Total tokens used: ~6.2K (vs 50K+ without skills)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### SDK Configuration for Generated Skills

```python
# Configure SDK to use generated skills location
import os
os.environ["CLAUDE_SKILLS_PATH"] = str(Path.home() / ".claude" / "skills")

# When using SDK query(), skills are automatically discovered from:
# - ~/.claude/skills/ (built-in)
# - ~/.claude/skills/generated/ (dynamically generated)

from claude_agent_sdk import query

async def build_with_generated_skills():
    """SDK automatically discovers and uses generated skills."""

    messages = [
        {
            "role": "user",
            "content": "Build a FastAPI API with Stripe webhook handling"
        }
    ]

    # SDK will:
    # 1. Discover fastapi-stripe-webhooks from filesystem
    # 2. Load metadata into context
    # 3. Trigger when conversation mentions Stripe webhooks
    # 4. Load full instructions and examples
    # 5. Use patterns to generate code

    async for chunk in query(messages=messages):
        # Process build output
        handle_chunk(chunk)
```

### Skill Loader Implementation

```python
class SDKSkillLoader:
    """Loads skills into Claude Agent SDK context."""

    def __init__(self, skills_paths: List[Path]):
        self.skills_paths = skills_paths
        self.loaded_skills: Dict[str, Skill] = {}

    async def discover_skills(self) -> List[SkillMetadata]:
        """Discover all available skills from filesystem.

        Mimics Claude Agent SDK's skill discovery.
        """
        skills = []

        for base_path in self.skills_paths:
            if not base_path.exists():
                continue

            # Iterate through skill directories
            for skill_dir in base_path.iterdir():
                if not skill_dir.is_dir():
                    continue

                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                # Parse SKILL.md frontmatter
                metadata = self._parse_skill_metadata(skill_md)
                skills.append(metadata)

        return skills

    def _parse_skill_metadata(self, skill_md_path: Path) -> SkillMetadata:
        """Parse YAML frontmatter from SKILL.md."""
        content = skill_md_path.read_text()

        # Extract YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                metadata = yaml.safe_load(yaml_content)
                return SkillMetadata(
                    name=metadata["name"],
                    description=metadata["description"],
                    path=skill_md_path.parent
                )

        raise ValueError(f"Invalid SKILL.md format: {skill_md_path}")

    async def load_skill_instructions(self, skill_name: str) -> str:
        """Load full skill instructions when triggered.

        This is called by SDK when a skill is matched.
        """
        if skill_name not in self.loaded_skills:
            # Find skill path
            for base_path in self.skills_paths:
                skill_path = base_path / skill_name / "SKILL.md"
                if skill_path.exists():
                    self.loaded_skills[skill_name] = Skill(
                        metadata=self._parse_skill_metadata(skill_path),
                        instructions=skill_path.read_text()
                    )
                    break

        return self.loaded_skills[skill_name].instructions
```

### End-to-End Flow with SDK

```python
async def complete_build_flow_with_sdk():
    """Complete flow showing skill generation → SDK usage."""

    # 1. Initialize orchestrator
    orchestrator = BuildOrchestrator(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 2. Analyze spec
    spec = Path("project-spec.md").read_text()

    # 3. Identify skill gaps
    gaps = await orchestrator.skill_generator.analyze_skill_gaps(spec)
    # Found: fastapi-stripe-webhooks (missing)

    # 4. Generate missing skill
    skill = await orchestrator.skill_generator.generate_skill(gaps[0])
    # Generated:
    #   - SKILL.md with patterns
    #   - examples/webhook_handler.py
    #   - tests/test_skill.py

    # 5. Validate skill
    validation = await orchestrator.skill_generator.validate_skill(skill)
    assert validation.valid  # ✓ Skill is valid

    # 6. Save to filesystem for SDK discovery
    await orchestrator.sdk_orchestrator._save_skill_to_filesystem(skill)
    # Saved to: ~/.claude/skills/generated/fastapi-stripe-webhooks/

    # 7. Execute build via SDK
    # SDK will automatically discover and use the generated skill
    result = await orchestrator.sdk_orchestrator.build_with_skills(
        spec=spec,
        required_skills=["python-fastapi-builder"],
        generated_skills=[skill]
    )

    # 8. SDK Processing:
    # - Discovers fastapi-stripe-webhooks from filesystem
    # - Loads metadata (~100 tokens)
    # - Matches "Stripe webhooks" in conversation
    # - Loads full instructions (~3K tokens)
    # - Accesses examples from filesystem (0 tokens)
    # - Generates code using skill patterns

    # 9. Result
    assert result.success
    assert "webhook_handler" in result.generated_files
    assert "stripe_service" in result.generated_files
```

## Benefits of SDK Integration

### 1. Zero Additional Context Cost
- Generated skills stored on filesystem
- SDK accesses via progressive disclosure
- Only loads what's needed, when needed

### 2. Seamless Integration
- Generated skills work identically to built-in skills
- No special handling needed
- Same discovery and loading mechanism

### 3. Persistent and Reusable
- Generated once, used forever
- Automatically available in future builds
- Can be refined based on usage

### 4. Type-Safe and Validated
- Skills validated before first use
- Integration tests ensure patterns work
- Linting ensures code quality

### 5. Observable and Debuggable
- Can inspect which skills were used
- Can see when skills were triggered
- Can track skill effectiveness

## Monitoring Skill Usage via SDK

```python
class SkillUsageTracker:
    """Track which skills are used during SDK execution."""

    async def track_build(self, build_id: str):
        """Monitor SDK execution to track skill usage."""

        skill_usage = []

        # Hook into SDK skill loading
        original_load = SDKSkillLoader.load_skill_instructions

        async def tracked_load(skill_name: str):
            self.logger.info("skill_triggered", skill=skill_name, build=build_id)
            skill_usage.append({
                "skill": skill_name,
                "triggered_at": datetime.now(),
                "build_id": build_id
            })
            return await original_load(skill_name)

        SDKSkillLoader.load_skill_instructions = tracked_load

        # After build completes
        await self._save_usage_metrics(build_id, skill_usage)
```

## Summary: SDK Integration Flow

```
Spec Analysis
     ↓
Skill Gaps Identified
     ↓
Skills Generated → Validated → Saved to Filesystem
     ↓
Claude Agent SDK Execution
     │
     ├─→ Discovers skills from filesystem
     ├─→ Loads skill metadata into context
     ├─→ Matches skills to conversation
     ├─→ Loads full instructions when triggered
     ├─→ Accesses skill resources on-demand
     └─→ Generates code using skill patterns
           ↓
     Production-Ready Project
           ↓
     Skill Usage Feedback
           ↓
     Skill Refinement (if needed)
```

The generated skills are **first-class citizens** in the Claude Agent SDK ecosystem, used exactly like built-in skills through the SDK's skills system.
