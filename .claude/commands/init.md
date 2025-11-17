# /ccb:init

Initialize build from specification.

**Usage**: `/ccb:init <spec_file_or_description>`

**Workflow**:
1. Load specification (file or inline)
2. Run 6D complexity analysis
3. Generate phase plan
4. Save to `.serena/ccb/`
5. Display: score, phases, timeline, next steps

**Example**:
```
/ccb:init spec.md
/ccb:init "Build REST API with auth and rate limiting"
```

**Skills**: @skill spec-driven-building, @skill complexity-analysis

**Output**: `.serena/ccb/build_goal.txt`, `complexity_analysis.json`, `phase_plan.json`
