---
name: complexity-analysis
skill-type: QUANTITATIVE
enforcement: 80
---

# Complexity Analysis: 6D Quantitative Scoring

**Enforcement**: QUANTITATIVE (80%)

## 6 Dimensions (Weighted)

1. Structure (20%): Files, modules, depth
2. Logic (25%): Business rules, branches
3. Integration (20%): APIs, databases, services
4. Scale (15%): Users, data volume
5. Uncertainty (10%): Spec completeness
6. Technical Debt (10%): Legacy code, deprecated deps

## Output

- Overall score: 0.0-1.0
- Category: TRIVIAL → CRITICAL
- Phase count: 3-6 (algorithmic)
- Timeline: Hours to weeks

## Usage

`/ccb:analyze spec.md` → 6D scores → Phase plan

## References

- `.claude/core/complexity-analysis.md`
