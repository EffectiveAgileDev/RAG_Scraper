# Mini PRD: Cost-Optimized LLM Semantic Detection System

## Problem Statement

**Current Issue**: RAG_Scraper uses hardcoded keyword matching that misses semantic equivalents, resulting in poor extraction of menu items, cuisine types, and other restaurant content from pages using synonyms or creative terminology.

**Impact**: 
- JSON structured data missing menu items when restaurants use terms like "shareables" instead of "appetizers"
- Poor extraction accuracy across different restaurant website styles
- Maintenance burden of expanding hardcoded synonym lists

## Solution Overview

Implement a hybrid extraction system that combines existing pattern matching with cost-optimized LLM semantic analysis, using intelligent caching and batching to minimize API costs while maximizing extraction accuracy.

## Key Features & Requirements

### Core Functionality
1. **Hybrid Extraction Pipeline**
   - Primary: Existing hardcoded pattern matching (fast, free)
   - Fallback: LLM semantic analysis (when patterns fail)
   - Smart triggering based on confidence thresholds

2. **Cost Optimization**
   - **Intelligent Caching**: Store LLM results with content fingerprinting
   - **Batch Processing**: Group multiple extraction requests
   - **Smart Fallback**: Only use LLM when traditional extraction confidence < 70%
   - **Rate Limiting**: Configurable API call limits per hour/day

3. **Content Classification**
   - Menu section identification ("apps" → "appetizers")
   - Cuisine type detection with variations ("tex-mex" → "mexican")
   - Service type recognition ("carry-out" → "takeout")
   - Hours format normalization ("Mondays" → "monday")

### Technical Requirements

#### LLM Integration
- **Provider flexibility**: Support OpenAI, Anthropic, local models
- **Model selection**: GPT-3.5-turbo as default (cost-effective)
- **Prompt engineering**: Optimized prompts for restaurant content
- **Response parsing**: Structured JSON output validation

#### Caching System
- **Cache key**: Content hash + extraction type + model version
- **Storage**: SQLite database for persistence across sessions
- **TTL**: 30-day expiration for cached results
- **Size limits**: Max 10MB cache with LRU eviction

#### Performance Targets
- **Response time**: < 200ms for cached results, < 2s for LLM calls
- **Cost target**: < $0.50/month for typical usage (100 sites/day)
- **Accuracy improvement**: 25%+ increase in extracted content

## Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Content In    │───▶│  Pattern Matcher │───▶│  Confidence     │
└─────────────────┘    └──────────────────┘    │  Evaluator      │
                                               └─────────┬───────┘
                                                         │
                                               confidence < 70%?
                                                         │
                                                         ▼
                       ┌─────────────────┐    ┌──────────────────┐
                       │  Cache Check    │◀───│  LLM Semantic    │
                       └─────────┬───────┘    │  Analyzer        │
                                 │            └──────────────────┘
                           cache hit?
                                 │
                                 ▼
                       ┌─────────────────┐    ┌──────────────────┐
                       │  Enhanced       │◀───│  Result Merger   │
                       │  Extraction     │    └──────────────────┘
                       │  Result         │
                       └─────────────────┘
```

### Implementation Components

#### 1. `SemanticAnalyzer` Class
```python
class SemanticAnalyzer:
    def __init__(self, llm_provider="openai", cache_enabled=True)
    def analyze_content(self, content: str, analysis_type: str) -> SemanticResult
    def batch_analyze(self, content_batch: List[ContentRequest]) -> List[SemanticResult]
```

#### 2. `IntelligentCache` Class
```python
class IntelligentCache:
    def get_cached_result(self, content_hash: str) -> Optional[SemanticResult]
    def store_result(self, content_hash: str, result: SemanticResult)
    def cleanup_expired(self) -> int
```

#### 3. `HybridExtractor` Class
```python
class HybridExtractor:
    def extract_with_fallback(self, content: str) -> ExtractionResult
    def evaluate_confidence(self, traditional_result: dict) -> float
    def merge_results(self, traditional: dict, semantic: dict) -> dict
```

## Success Metrics

### Primary KPIs
- **Extraction Accuracy**: 90%+ for menu items, cuisine types, services
- **Cost Efficiency**: < $0.50/month operational cost
- **Performance**: 95% of requests < 2s response time

### Secondary Metrics
- **Cache Hit Rate**: 70%+ for repeated content patterns
- **Traditional vs LLM Usage**: 80% traditional, 20% LLM
- **User Satisfaction**: Improved JSON output completeness

## Implementation Phases

### Phase 1: Foundation (1 week)
- [ ] Basic LLM integration with OpenAI API
- [ ] Simple caching mechanism (in-memory)
- [ ] Confidence evaluation for existing extractors
- [ ] Integration point in heuristic extractor

### Phase 2: Optimization (1 week)  
- [ ] Persistent SQLite cache with TTL
- [ ] Batch processing for multiple requests
- [ ] Cost tracking and rate limiting
- [ ] Prompt optimization for restaurant content

### Phase 3: Enhancement (1 week)
- [ ] Multi-provider support (Anthropic, local models)
- [ ] Advanced caching strategies (content fingerprinting)
- [ ] Performance monitoring and alerts
- [ ] A/B testing framework for prompt iterations

### Phase 4: Production (1 week)
- [ ] Error handling and fallback mechanisms
- [ ] Configuration management
- [ ] Monitoring dashboards
- [ ] Documentation and testing

## Cost Analysis

### Monthly Cost Estimate (100 sites/day)
- **Traditional extraction**: 80% of requests = FREE
- **LLM calls**: 20% × 100 sites × 30 days × $0.002/1k tokens × 0.5k avg = **$0.60/month**
- **Cache hit reduction**: 70% cache hit = **$0.18/month actual cost**

### Cost Controls
- **Daily limits**: Max $2/day spend limit
- **Rate limiting**: Max 1000 LLM calls/day
- **Emergency fallback**: Disable LLM if daily budget exceeded

## Risk Mitigation

### Technical Risks
- **LLM API failures**: Graceful degradation to traditional extraction
- **Cost overruns**: Daily spend limits and monitoring alerts
- **Performance degradation**: Cache warming and async processing

### Operational Risks
- **Model changes**: Version pinning and compatibility testing
- **Rate limiting**: Multiple provider support and request queuing
- **Data privacy**: No PII in LLM requests, local processing option

## Configuration

### Environment Variables
```bash
LLM_PROVIDER=openai              # openai|anthropic|local
LLM_MODEL=gpt-3.5-turbo         # Model selection
LLM_DAILY_BUDGET=2.00           # USD daily limit
CACHE_ENABLED=true              # Enable/disable caching
CACHE_TTL_DAYS=30               # Cache expiration
SEMANTIC_CONFIDENCE_THRESHOLD=0.7 # When to use LLM
```

## Success Definition

**MVP Success**: 25% improvement in menu item extraction accuracy with operational costs under $0.50/month and 95% uptime.

**Long-term Vision**: Fully semantic content understanding that adapts to new restaurant terminology without manual updates, serving as foundation for AI-powered content classification across the entire scraping pipeline.