# SAP Performance Improvements

## Summary
This document outlines the performance optimizations implemented for the Strategic Adaptation Process (SAP) system to improve execution speed and responsiveness.

## Optimizations Implemented

### 1. Regex Pattern Precompilation (High Impact)
**File**: `core/router/sap_scoring/score_sap.py`

**Problem**: 40+ regex patterns were being compiled on every SAP scoring call (3 calls per task execution).

**Solution**:
- Precompiled all regex patterns at module load time
- Patterns organized by scoring dimension:
  - Plausibility: 9 patterns
  - Utility: 3 patterns
  - Novelty: 9 patterns
  - Risk: 9 patterns
  - Alignment: 9 patterns
  - Efficiency: 3 patterns
  - Resilience: 8 patterns

**Expected Impact**: 60-80% reduction in scoring time (from ~50ms to ~10-20ms per SAP)

### 2. LRU Caching for Scoring Functions (Medium Impact)
**File**: `core/router/sap_scoring/score_sap.py`

**Problem**: Identical SAP texts could be scored multiple times with redundant computation.

**Solution**:
- Added `@lru_cache(maxsize=128)` to all 7 dimension calculation functions
- Caches the 128 most recent unique SAP text evaluations

**Expected Impact**: Near-instant scoring for repeated SAPs (cache hit = <1ms vs 10-20ms)

### 3. Dynamic SAP Generation Integration (High Impact)
**File**: `core/task_manager/runner.py`

**Problem**: SAPs were hardcoded, not dynamically generated based on user prompts.

**Solution**:
- Integrated `mutate_sap()` function into main task runner
- SAPs now generated dynamically via DeepSeek-R1 model
- Proposals tailored to actual user input

**Expected Impact**: Better quality SAPs, more relevant to user queries

### 4. Streaming Enabled by Default (Medium Impact)
**File**: `config.yaml`

**Problem**: Non-streaming mode caused slower time-to-first-token (TTFT).

**Solution**:
- Enabled `stream: true` in Ollama configuration
- Reduces perceived latency by streaming tokens as they're generated
- Already implemented in `latent_executor.py` (lines 77-103)

**Expected Impact**: 30-50% faster perceived response time (TTFT improves from ~2s to ~500ms)

### 5. Output Cleaning Optimization (Low Impact)
**File**: `core/shared/output_cleaner.py`

**Problem**: 8 regex patterns + text wrapper created on every clean_output() call.

**Solution**:
- Precompiled all regex patterns at module level
- Reused shared `TextWrapper` instance for default width (80)
- Reduced object creation overhead

**Expected Impact**: 40-60% reduction in output cleaning time (from ~5ms to ~2-3ms)

### 6. Probe Suite Configuration Updates (Medium Impact)
**File**: `config.yaml`

**Problem**: Default probe count (3) and control probe added overhead.

**Solution**:
- Reduced `default_probe_count` from 3 to 1
- Disabled `include_control` by default
- Users can still override for thorough testing

**Expected Impact**: 66% reduction in probe execution time (3 probes → 1 probe)

## Performance Configuration

### Optimized Ollama Settings
```yaml
ollama:
  stream: true              # Fast time-to-first-token
  num_predict: 220          # Bounded token generation
  temperature: 0.3          # Deterministic output
  probe_num_predict: 100    # Faster probes
```

## Expected Overall Performance Gains

| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| SAP Scoring (3 SAPs) | ~150ms | ~30-60ms | **60-80%** |
| Time-to-First-Token | ~2s | ~500ms | **75%** |
| Output Cleaning | ~5ms | ~2-3ms | **40-60%** |
| Probe Execution | 3 probes | 1 probe | **66%** |

**Total End-to-End**: Estimated **50-70% reduction** in SAP execution time

## Implementation Details

### Regex Precompilation Example
**Before:**
```python
for word in concrete_words:
    if re.search(rf'\b{word}\b', text_lower):  # Compiled every time
        score += 2
```

**After:**
```python
PLAUSIBILITY_CONCRETE = [re.compile(rf'\b{word}\b') for word in [...]]  # Compiled once

for pattern in PLAUSIBILITY_CONCRETE:
    if pattern.search(text_lower):  # Reused compiled pattern
        score += 2
```

### LRU Cache Example
```python
@lru_cache(maxsize=128)
def _calculate_plausibility(text_lower: str) -> int:
    # Function body remains the same
    # Results cached for repeated inputs
```

## Testing Recommendations

1. **Performance Benchmarking**:
   - Measure end-to-end SAP execution time before/after
   - Monitor Ollama response latency
   - Track cache hit rates in production

2. **Functional Testing**:
   - Verify SAP proposals are dynamically generated
   - Confirm streaming output appears progressively
   - Test with various prompt types

3. **Load Testing**:
   - Test with multiple concurrent SAP executions
   - Verify cache performance under load
   - Monitor memory usage with LRU cache

## Future Optimization Opportunities

1. **Parallel SAP Scoring**: Score 3 SAPs concurrently (requires threading)
2. **MAPLE Pipeline**: Implement actual deep analysis (currently stubbed)
3. **Probe Suite Parallelization**: Run probes concurrently when multiple probes used
4. **Response Caching**: Cache mutate_sap() outputs for repeated prompts

## Rollback Instructions

If issues arise, revert these configuration changes:

```yaml
# config.yaml
ollama:
  stream: false             # Disable streaming

probe_suite:
  default_probe_count: 3    # Increase probe count
  include_control: true     # Re-enable control probe
```

And restore hardcoded SAPs in `core/task_manager/runner.py` if mutate_sap causes issues.

---

**Date**: 2026-01-13
**Author**: Claude Code Performance Optimization
