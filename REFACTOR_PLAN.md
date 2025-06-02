# Silent Agreement Evaluation Framework - Refactor Plan

## Overview
This document outlines the planned refactoring of the Silent Agreement evaluation framework to improve code quality, reduce duplication, and enhance maintainability.

## Current State Analysis

### Major Issues Identified
1. **Code Duplication**: ~40% of codebase is duplicated across modules
2. **Over-Engineering**: Complex abstractions that add no value
3. **Poor Separation of Concerns**: Functions handling multiple responsibilities
4. **Dead Code**: Unused imports and stubbed implementations

## Refactor Phases

### Phase 1: Quick Wins ✅ COMPLETED
- [x] Remove unused `import os` from all entry scripts
- [x] Delete `ThinkingResultsProcessor` stub class
- [x] Clean up unused imports throughout codebase
- [x] Remove empty `__init__.py` files or add proper exports

### Phase 2: Entry Script Consolidation
**Goal**: Replace 3 nearly-identical scripts with one unified script

**Current Structure** (750+ lines of duplicated code):
- `scripts/run_base_eval.py`
- `scripts/run_effort_reasoning_eval.py`
- `scripts/run_token_reasoning_eval.py`

**Proposed Structure**:
```python
# scripts/run_eval.py
python scripts/run_eval.py --type base --model groq/llama-3.3-70b-versatile --test-mode quick-test
python scripts/run_eval.py --type effort --model openai/o3-mini --test-mode full
python scripts/run_eval.py --type tokens --model anthropic/claude-3.7 --test-mode quick-test
```

**Benefits**:
- Removes ~500 lines of duplicated code
- Single point of maintenance
- Consistent behavior across evaluation types
- Easier to add new evaluation types

### Phase 3: Simplify Hash Verification System
**Goal**: Remove unnecessary prompt version control complexity

**To Remove** (~600 lines):
- `dataset_generation/prompt_registry.py` (entire file)
- `dataset_generation/regenerate_hashes.py` (entire file)
- `dataset_generation/base/base_prompts_hashes.json`
- `dataset_generation/reasoning/reasoning_prompts_hashes.json`
- Hash verification logic in task files

**To Keep**:
- Prompts as simple constants in `prompts.py`
- Git for version control
- Simple version tags for experiment milestones

### Phase 4: Unify Evaluation Logic
**Goal**: Consolidate duplicate evaluation implementations

**Metric Functions**:
- Merge `sare_metrics()` and `sart_metrics()` into single configurable function
- Create unified `calculate_metrics(scores, eval_type="base")`

**Scorer Consolidation**:
- Combine `base/scorer.py` and `shared/reasoning_scorer.py`
- Extract validation logic to utilities
- Separate scoring from validation and extraction

**Task Unification**:
- Create single configurable task class
- Use composition over inheritance
- Pass evaluation type as configuration

### Phase 5: Simplify Results Processing
**Goal**: Streamline the results generation pipeline

**Current Issues**:
- Over-abstracted framework with only one implementation
- 320-line `generate_json_results_from_eval()` function
- Multiple data transformations
- Confusing generic naming ("exp1", "exp2", "exp3")

**Proposed Changes**:
- Remove `framework/processor.py` abstraction
- Break down large functions into focused utilities
- Use consistent naming throughout
- Single data transformation pass

### Phase 6: Architecture Improvements
**Goal**: Establish clear, maintainable architecture

**Key Changes**:
1. **Configuration-Driven Design**:
   - Central configuration for evaluation types
   - Explicit type passing (no inference from task names)
   - Extract magic numbers to named constants

2. **Clear Data Flow**:
   ```
   Dataset → Task → Evaluation → Scoring → Results
   ```

3. **Proper Error Handling**:
   - Replace generic `except Exception` with specific types
   - Add structured logging instead of print statements
   - Better error messages for users

4. **Type Safety**:
   - Add type hints throughout
   - Use dataclasses for configuration objects
   - Validate inputs at boundaries

## Implementation Priority

### High Priority (Do First)
1. Entry script consolidation - High impact, relatively easy
2. Unify metric functions - Quick win, reduces duplication
3. Extract constants - Simple improvement

### Medium Priority
4. Simplify hash verification - Significant code reduction
5. Merge scorers - Important but requires careful testing
6. Streamline results processing - Good improvement but complex

### Low Priority (Do Last)
7. Full architecture improvements - Important but can be incremental
8. Add comprehensive type hints - Nice to have
9. Enhanced logging system - Improvement but not critical

## Expected Outcomes

### Code Reduction
- **Lines of Code**: Reduce by ~1,500-2,000 lines (25-30%)
- **File Count**: Remove ~10-15 unnecessary files
- **Duplication**: Eliminate ~90% of duplicated code

### Quality Improvements
- **Maintainability**: Single implementation for common functionality
- **Clarity**: Clear separation of concerns
- **Extensibility**: Easy to add new evaluation types
- **Testability**: Simpler components easier to unit test

### Performance
- **Faster Development**: Less code to understand and modify
- **Reduced Bugs**: Single implementation reduces inconsistencies
- **Easier Debugging**: Clear data flow and better error messages

## Migration Strategy

1. **Create Feature Branch**: Work in isolation from main branch
2. **Incremental Changes**: Complete one phase before moving to next
3. **Maintain Tests**: Ensure all tests pass after each phase
4. **Document Changes**: Update documentation as code changes
5. **Gradual Integration**: Merge completed phases back to main

## Notes for Discussion

- Should we keep any of the hash verification for specific use cases?
- Are there plans for additional evaluation types that would affect the design?
- What level of backwards compatibility is needed?
- Are there any external dependencies on the current structure?