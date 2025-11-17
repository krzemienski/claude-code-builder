# /ccb:analyze

Run 6D complexity analysis without initializing build.

**Usage**: `/ccb:analyze <spec> [--save] [--mcps]`

**Output**:
- 6D dimension breakdown
- Overall score (0.0-1.0) + category
- Recommended phase count (3-6)
- Timeline distribution (%)
- Risk assessment

**Options**:
- `--save`: Persist to Serena MCP
- `--mcps`: Show MCP recommendations

**Skills**: @skill complexity-analysis

**Example**: `/ccb:analyze spec.md --save`
