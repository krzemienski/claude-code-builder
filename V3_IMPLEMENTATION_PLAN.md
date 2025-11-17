# Claude Code Builder v3 - Shannon-Aligned Implementation Plan

**Based on**: V3_SHANNON_ALIGNED_SPEC.md
**Approach**: Phased implementation with functional testing after each phase
**Strategy**: Remove all old code, single package architecture

---

## Implementation Phases

### Phase 0: Foundation (Core Docs + Hooks + Structure)

**Duration**: 2-3 hours

**Deliverables**:
1. `.claude/` directory structure
2. 6 core reference documents (9.5K lines):
   - `core/ccb-principles.md` (2.5K)
   - `core/complexity-analysis.md` (1.8K)
   - `core/phase-planning.md` (1.5K)
   - `core/testing-philosophy.md` (1.2K)
   - `core/state-management.md` (1.0K)
   - `core/project-indexing.md` (1.5K)
3. Hooks configuration and scripts:
   - `hooks/hooks.json`
   - `hooks/session_start.sh`
   - `hooks/user_prompt_submit.py`
   - `hooks/post_tool_use.py`
   - `hooks/precompact.py`
   - `hooks/stop.py`
4. Plugin metadata:
   - `.claude-plugin/manifest.json`

**Functional Test**:
```bash
# Test 1: Verify hooks.json is valid JSON
python -c "import json; json.load(open('.claude/hooks/hooks.json'))"

# Test 2: Verify session_start.sh loads ccb-principles
bash .claude/hooks/session_start.sh | grep "CCB v3"

# Test 3: Verify Python hooks have valid syntax
python -m py_compile .claude/hooks/user_prompt_submit.py
python -m py_compile .claude/hooks/post_tool_use.py
python -m py_compile .claude/hooks/precompact.py
python -m py_compile .claude/hooks/stop.py

# Test 4: Verify all core docs exist
ls .claude/core/*.md | wc -l  # Should be 6
```

**Success Criteria**:
- ✅ All 6 core docs created with specified line counts (±10%)
- ✅ All 5 hooks pass syntax validation
- ✅ hooks.json is valid JSON
- ✅ session_start.sh executes without errors

---

### Phase 1: Core Skills (RIGID + PROTOCOL)

**Duration**: 3-4 hours

**Deliverables**:
1. **RIGID Skills** (100% enforcement):
   - `skills/ccb-principles/SKILL.md`
   - `skills/functional-testing/SKILL.md`

2. **PROTOCOL Skills** (90% enforcement):
   - `skills/spec-driven-building/SKILL.md`
   - `skills/phase-execution/SKILL.md`
   - `skills/checkpoint-preservation/SKILL.md`
   - `skills/project-indexing/SKILL.md`

**SKILL.md Structure** (each):
```yaml
---
name: skill-name
skill-type: RIGID|PROTOCOL|QUANTITATIVE|FLEXIBLE
enforcement: 100|90|80|70
mcp-requirements:
  required:
    - name: serena
      purpose: State persistence
      fallback: none
      degradation: high
  recommended:
    - name: context7
      purpose: Framework docs
---

# Skill Content
Iron Laws / Behavioral patterns / Anti-rationalization counters
```

**Functional Test**:
```bash
# Test 1: Verify all 6 skills have valid YAML frontmatter
for skill in .claude/skills/*/SKILL.md; do
  python -c "import yaml; yaml.safe_load(open('$skill').read().split('---')[1])"
done

# Test 2: Verify enforcement levels are correct
grep -r "enforcement: 100" .claude/skills/ccb-principles/
grep -r "enforcement: 100" .claude/skills/functional-testing/
grep -r "enforcement: 90" .claude/skills/spec-driven-building/

# Test 3: Verify NO MOCKS patterns in functional-testing skill
grep -r "jest.mock" .claude/skills/functional-testing/SKILL.md
grep -r "unittest.mock" .claude/skills/functional-testing/SKILL.md

# Test 4: Count total skills
ls .claude/skills/*/SKILL.md | wc -l  # Should be 6
```

**Success Criteria**:
- ✅ All 6 skills created with valid YAML frontmatter
- ✅ Enforcement levels match specification
- ✅ Anti-rationalization counters present in each skill
- ✅ MCP requirements documented

---

### Phase 2: Command Infrastructure + Foundation Commands

**Duration**: 4-5 hours

**Deliverables**:
1. **Remaining Skills** (6 more):
   - `skills/complexity-analysis/SKILL.md` (QUANTITATIVE)
   - `skills/validation-gates/SKILL.md` (QUANTITATIVE)
   - `skills/test-coverage/SKILL.md` (QUANTITATIVE)
   - `skills/mcp-augmented-research/SKILL.md` (FLEXIBLE)
   - `skills/honest-assessment/SKILL.md` (FLEXIBLE)
   - `skills/incremental-enhancement/SKILL.md` (FLEXIBLE)

2. **Commands** (4 foundation commands):
   - `commands/init.md` - Initialize build from spec
   - `commands/status.md` - Show build progress
   - `commands/analyze.md` - Complexity analysis only
   - `commands/index.md` - Generate PROJECT_INDEX

**Command Structure** (each):
```markdown
# /ccb:command-name

**Description**: What the command does

**Usage**:
/ccb:command-name [arguments] [--options]

**Workflow**:
1. Step 1
2. Step 2
3. Step 3

**Skills Invoked**:
- @skill skill-name-1
- @skill skill-name-2

**Serena MCP Storage**:
- .serena/ccb/file.json

**Output**: What user sees

**Examples**:
/ccb:command-name example
```

**Functional Test**:
```bash
# Test 1: Verify all 12 skills exist
ls .claude/skills/*/SKILL.md | wc -l  # Should be 12

# Test 2: Verify all 4 commands exist
ls .claude/commands/*.md | wc -l  # Should be 4

# Test 3: Verify each command references at least one skill
for cmd in .claude/commands/*.md; do
  grep -q "@skill" "$cmd" || echo "ERROR: $cmd has no skill references"
done

# Test 4: Verify Serena MCP paths documented
grep -r ".serena/ccb/" .claude/commands/*.md
```

**Success Criteria**:
- ✅ All 12 skills created (6 RIGID/PROTOCOL + 6 QUANTITATIVE/FLEXIBLE)
- ✅ All 4 foundation commands created
- ✅ Commands reference appropriate skills
- ✅ Serena MCP paths documented

---

### Phase 3: Execution Commands

**Duration**: 4-5 hours

**Deliverables**:
1. **Commands** (4 execution commands):
   - `commands/build.md` - Execute phase with validation
   - `commands/do.md` - Operate on existing codebase
   - `commands/checkpoint.md` - Manual state save
   - `commands/resume.md` - Restore from checkpoint

2. **Serena MCP Integration Examples**:
   - Example `.serena/ccb/` structure
   - Sample checkpoint format
   - Auto-resume logic pseudocode

**Functional Test**:
```bash
# Test 1: Verify all 8 commands exist
ls .claude/commands/*.md | wc -l  # Should be 8

# Test 2: Verify build.md references phase-execution skill
grep "@skill phase-execution" .claude/commands/build.md

# Test 3: Verify do.md references project-indexing skill
grep "@skill project-indexing" .claude/commands/do.md

# Test 4: Verify checkpoint format documented
grep -A 10 "checkpoint_id" .claude/commands/checkpoint.md

# Test 5: Create sample .serena structure
mkdir -p test_serena/ccb/{artifacts,checkpoints,indices}
touch test_serena/ccb/build_goal.txt
ls test_serena/ccb/ | wc -l  # Should be >=4
rm -rf test_serena/
```

**Success Criteria**:
- ✅ All 8 commands created
- ✅ build.md orchestrates phase execution
- ✅ do.md handles existing codebases
- ✅ Checkpoint format documented with examples
- ✅ Auto-resume logic specified

---

### Phase 4: Quality Commands + Cleanup

**Duration**: 3-4 hours

**Deliverables**:
1. **Commands** (2 quality commands):
   - `commands/test.md` - Functional testing (NO MOCKS)
   - `commands/reflect.md` - Honest gap assessment

2. **Documentation**:
   - `.claude/README.md` - Framework overview
   - `CLAUDE.md` - Updated project instructions
   - `USER_GUIDE.md` - Usage examples

3. **Cleanup**:
   - Remove `src/claude_code_builder/` (v1/v2)
   - Remove `src/claude_code_builder_v3/` (old v3)
   - Update `pyproject.toml` - single package entry point

**Functional Test**:
```bash
# Test 1: Verify all 10 commands exist
ls .claude/commands/*.md | wc -l  # Should be 10

# Test 2: Verify test.md blocks mock patterns
grep -A 5 "jest.mock" .claude/commands/test.md
grep -A 5 "unittest.mock" .claude/commands/test.md

# Test 3: Verify old code is removed
test ! -d src/claude_code_builder && echo "v1/v2 removed ✓"
test ! -d src/claude_code_builder_v3 && echo "old v3 removed ✓"

# Test 4: Verify only .claude/ structure remains
ls -d .claude/*/ | wc -l  # Should be 4 (core, hooks, skills, commands)

# Test 5: Count all framework files
find .claude -type f | wc -l  # Should be ~30 files
```

**Success Criteria**:
- ✅ All 10 commands created
- ✅ test.md enforces NO MOCKS
- ✅ reflect.md provides gap analysis
- ✅ ALL old code removed (v1, v2, old v3)
- ✅ Only `.claude/` framework remains
- ✅ Documentation complete

---

### Phase 5: Final Validation

**Duration**: 2 hours

**End-to-End Functional Test**:
```bash
# Test 1: Complete framework structure validation
test -d .claude/core && echo "Core docs ✓"
test -d .claude/hooks && echo "Hooks ✓"
test -d .claude/skills && echo "Skills ✓"
test -d .claude/commands && echo "Commands ✓"

# Test 2: Count all components
echo "Core docs: $(ls .claude/core/*.md | wc -l) / 6"
echo "Hooks: $(ls .claude/hooks/*.py .claude/hooks/*.sh .claude/hooks/*.json 2>/dev/null | wc -l) / 6"
echo "Skills: $(ls .claude/skills/*/SKILL.md | wc -l) / 12"
echo "Commands: $(ls .claude/commands/*.md | wc -l) / 10"

# Test 3: Verify YAML frontmatter in all skills
python3 << 'EOF'
import yaml
import sys
from pathlib import Path

skills_dir = Path('.claude/skills')
errors = []

for skill_file in skills_dir.glob('*/SKILL.md'):
    content = skill_file.read_text()
    if '---' not in content:
        errors.append(f"{skill_file}: No YAML frontmatter")
        continue

    parts = content.split('---')
    if len(parts) < 3:
        errors.append(f"{skill_file}: Invalid frontmatter format")
        continue

    try:
        metadata = yaml.safe_load(parts[1])
        required = ['name', 'skill-type', 'enforcement']
        for field in required:
            if field not in metadata:
                errors.append(f"{skill_file}: Missing {field}")
    except Exception as e:
        errors.append(f"{skill_file}: {e}")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  ❌ {e}")
    sys.exit(1)
else:
    print("✅ All skills have valid YAML frontmatter")
EOF

# Test 4: Verify enforcement hierarchy
python3 << 'EOF'
import yaml
from pathlib import Path

skills_dir = Path('.claude/skills')
enforcement_levels = {
    'RIGID': [],
    'PROTOCOL': [],
    'QUANTITATIVE': [],
    'FLEXIBLE': []
}

for skill_file in skills_dir.glob('*/SKILL.md'):
    content = skill_file.read_text()
    parts = content.split('---')
    metadata = yaml.safe_load(parts[1])
    skill_type = metadata.get('skill-type', 'UNKNOWN')
    enforcement_levels[skill_type].append(metadata['name'])

print("Enforcement Hierarchy:")
print(f"  RIGID (100%): {len(enforcement_levels['RIGID'])} skills")
for s in enforcement_levels['RIGID']:
    print(f"    - {s}")
print(f"  PROTOCOL (90%): {len(enforcement_levels['PROTOCOL'])} skills")
for s in enforcement_levels['PROTOCOL']:
    print(f"    - {s}")
print(f"  QUANTITATIVE (80%): {len(enforcement_levels['QUANTITATIVE'])} skills")
for s in enforcement_levels['QUANTITATIVE']:
    print(f"    - {s}")
print(f"  FLEXIBLE (70%): {len(enforcement_levels['FLEXIBLE'])} skills")
for s in enforcement_levels['FLEXIBLE']:
    print(f"    - {s}")

expected = {'RIGID': 2, 'PROTOCOL': 4, 'QUANTITATIVE': 3, 'FLEXIBLE': 3}
actual = {k: len(v) for k, v in enforcement_levels.items()}

if actual == expected:
    print("\n✅ Skill distribution matches specification")
else:
    print(f"\n❌ Expected {expected}, got {actual}")
EOF

# Test 5: Verify hook references skills
grep -r "@skill" .claude/hooks/ || echo "⚠️  Hooks don't reference skills"

# Test 6: Verify commands reference skills
for cmd in .claude/commands/*.md; do
  if ! grep -q "@skill" "$cmd"; then
    echo "❌ $cmd doesn't reference any skills"
  fi
done

# Test 7: Verify NO MOCKS enforcement
grep -r "jest.mock" .claude/skills/functional-testing/SKILL.md > /dev/null && echo "✅ NO MOCKS patterns documented"
grep -r "MOCK_PATTERNS" .claude/hooks/post_tool_use.py > /dev/null && echo "✅ Mock detection in hooks"

# Test 8: Verify Serena MCP integration
grep -r ".serena/ccb/" .claude/ | wc -l  # Should be multiple references

echo ""
echo "=========================================="
echo "FINAL VALIDATION SUMMARY"
echo "=========================================="
echo "Framework Components:"
echo "  Core Docs: $(ls .claude/core/*.md 2>/dev/null | wc -l) / 6"
echo "  Hooks: $(ls .claude/hooks/*.py .claude/hooks/*.sh 2>/dev/null | wc -l) / 5"
echo "  Skills: $(ls .claude/skills/*/SKILL.md 2>/dev/null | wc -l) / 12"
echo "  Commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l) / 10"
echo ""
echo "Old Code Removed:"
echo "  v1/v2 removed: $(test ! -d src/claude_code_builder && echo '✅' || echo '❌')"
echo "  old v3 removed: $(test ! -d src/claude_code_builder_v3 && echo '✅' || echo '❌')"
echo ""
echo "Framework Status: COMPLETE"
echo "=========================================="
```

**Success Criteria**:
- ✅ 6 core docs
- ✅ 5 hooks + hooks.json
- ✅ 12 skills (2 RIGID, 4 PROTOCOL, 3 QUANTITATIVE, 3 FLEXIBLE)
- ✅ 10 commands
- ✅ All YAML frontmatter valid
- ✅ NO MOCKS enforcement present
- ✅ Serena MCP integration documented
- ✅ ALL old code removed

---

## File Count Summary

**Total Framework Files**: ~35-40

**Breakdown**:
- Core docs: 6 files (~9.5K lines)
- Hooks: 6 files (5 scripts + hooks.json)
- Skills: 12 files (12 × SKILL.md)
- Commands: 10 files (10 × .md)
- Plugin metadata: 1 file (manifest.json)
- Documentation: 2-3 files (README.md, USER_GUIDE.md)

---

## Implementation Order

1. ✅ Phase 0: Foundation (hooks + core docs)
2. ✅ Phase 1: Core Skills (RIGID + PROTOCOL)
3. ✅ Phase 2: Remaining Skills + Foundation Commands
4. ✅ Phase 3: Execution Commands
5. ✅ Phase 4: Quality Commands + Cleanup
6. ✅ Phase 5: Final Validation

**Total Estimated Time**: 16-20 hours
**Compressed Timeline**: Can complete in 1 focused session (8-10 hours)

---

## Success Metrics

**Quantitative**:
- 6/6 core docs
- 5/5 hooks + configuration
- 12/12 skills with valid YAML
- 10/10 commands
- 0 old code directories
- 100% functional tests passing

**Qualitative**:
- Framework follows Shannon's 4-layer architecture
- Skills enforce behavior, not generate code
- Hooks auto-activate without manual intervention
- Commands orchestrate workflows
- NO MOCKS enforced at all layers
- Existing codebase support via project-indexing

---

**Status**: Ready for implementation
**Next**: Begin Phase 0
