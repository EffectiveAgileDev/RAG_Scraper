# Git Infrastructure Plan for RAG_Scraper Project

## Executive Summary

This document specifies the complete git infrastructure needed to support three parallel development streams: WTEG Client delivery, AI Development Industry expansion, and Platform Features enhancement. The plan provides specific branch strategies, label systems, and tagging conventions for professional project management.

## Current State Analysis

**Project Architecture**: Flask-based web scraper with 95%+ test coverage following TDD methodology
**Current Phase**: 4.3W.1 - Local file upload implementation complete  
**Active Industries**: Restaurant (live), AI/Agile Development (Q3 2025), 11 additional industries planned
**Technology Stack**: Flask 2.3.3, BeautifulSoup4, Playwright, pytest-bdd for ATDD

## Three Development Stream Requirements

### Stream 1: WTEG Client (Revenue Critical)
- **Priority**: P0 - Immediate revenue impact
- **Focus**: PDF processing, WTEG schema compliance, client deliverables
- **Timeline**: Sprint-based delivery cycles

### Stream 2: AI Development Industry (Demo Platform)  
- **Priority**: P1 - Business expansion for AgileAIDev.com
- **Focus**: AI/Agile industry implementation, demo capabilities
- **Timeline**: Q3 2025 target

### Stream 3: Platform Features (Technical Debt & Growth)
- **Priority**: P2 - Foundation and scalability  
- **Focus**: Semantic structuring, cloud deployment, multi-industry support
- **Timeline**: Continuous improvement

---

## 1. Git Branch Strategy

### Branch Hierarchy and Naming Conventions

#### Primary Branches
```bash
main                    # Production-ready code, protected branch
develop                 # Integration branch for all features
release/v{major}.{minor}.x  # Release maintenance branches
hotfix/*               # Critical production fixes
```

#### Feature Branches by Stream
```bash
# WTEG Client Stream (immediate revenue)
feature/wteg-{issue-number}-{description}
feature/wteg-pdf-enhancement
feature/wteg-cms-integration
feature/wteg-schema-validation

# AI Development Industry Stream  
feature/ai-industry-{issue-number}-{description}
feature/ai-industry-extraction
feature/ai-industry-knowledge-base
feature/ai-industry-demo-features

# Platform Features Stream
feature/platform-{issue-number}-{description}
feature/platform-semantic-structuring
feature/platform-cloud-deployment
feature/platform-multi-modal-processing
```

#### Integration Branches
```bash
integration/wteg-delivery     # WTEG client integration testing
integration/ai-industry       # AI industry feature integration  
integration/platform-release  # Platform feature integration
```

### Branch Creation Commands

```bash
# Create and switch to feature branch
git checkout develop
git pull origin develop
git checkout -b feature/wteg-123-pdf-processing
git push -u origin feature/wteg-123-pdf-processing

# Create release branch
git checkout main
git checkout -b release/v1.4.x
git push -u origin release/v1.4.x
```

### Branch Protection Rules
- `main`: Require PR reviews (2), status checks, no direct pushes
- `develop`: Require PR reviews (1), status checks  
- `release/*`: Require PR reviews (2), restrict to release managers
- All feature branches: Allow direct pushes by assignee

---

## 2. Git Labels System

### Priority Labels
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `priority/P0` | `#D73A49` | Critical - Production issue or revenue blocker | WTEG client issues, production bugs |
| `priority/P1` | `#FB8C00` | High - Important feature or significant bug | AI industry features, major enhancements |
| `priority/P2` | `#0366D6` | Medium - Standard feature or improvement | Platform features, technical debt |
| `priority/P3` | `#28A745` | Low - Nice to have or minor improvement | Documentation, minor enhancements |

### Development Stream Labels  
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `stream/wteg-client` | `#8B4513` | WTEG client-specific work | All WTEG deliverables |
| `stream/ai-industry` | `#4B0082` | AI Development industry features | AgileAIDev.com demo features |
| `stream/platform` | `#2E8B57` | Core platform improvements | Infrastructure, multi-industry |

### Type Labels
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `type/feature` | `#0366D6` | New feature implementation | New functionality |
| `type/enhancement` | `#7057FF` | Improvement to existing feature | Performance, UX improvements |
| `type/bug` | `#D73A49` | Bug fix | Error corrections |
| `type/refactor` | `#F9D71C` | Code refactoring without behavior change | Clean code improvements |
| `type/test` | `#FBCA04` | Test-related work | TDD, test coverage |
| `type/docs` | `#0075CA` | Documentation updates | README, API docs |
| `type/security` | `#B60205` | Security-related changes | Vulnerability fixes |

### Component Labels
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `component/scraper` | `#FF6B35` | Web scraping engine | BeautifulSoup, Playwright |
| `component/file-generator` | `#FF9F1C` | File generation system | RAG output, PDF generation |
| `component/web-interface` | `#2EC4B6` | Flask web UI | Frontend, API routes |
| `component/ai-integration` | `#9B59B6` | AI/LLM features | OpenAI, Claude integration |
| `component/wteg` | `#8B4513` | WTEG-specific module | CMS integration, WTEG schema |
| `component/processors` | `#F72585` | Multi-modal processors | PDF, image, HTML processing |
| `component/config` | `#4D5DB5` | Configuration management | Settings, industry config |
| `component/testing` | `#FBCA04` | Testing infrastructure | pytest, BDD, coverage |

### Status Labels
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `status/needs-review` | `#FBCA04` | Ready for code review | PR ready state |
| `status/in-progress` | `#0366D6` | Currently being worked on | Active development |
| `status/blocked` | `#D73A49` | Cannot proceed due to dependency | Waiting for external factor |
| `status/testing` | `#28A745` | In testing phase | QA, acceptance testing |
| `status/ready-to-merge` | `#2E8B57` | Approved and ready for merge | Final approval state |

### Client/Demo Labels  
| Label Name | Color | Description | Usage |
|------------|-------|-------------|--------|
| `client/wteg` | `#8B4513` | Where To Eat Guide client | WTEG-specific deliverables |
| `demo/agileaidev` | `#4B0082` | AgileAIDev.com demo features | AI industry showcase |
| `internal/platform` | `#2E8B57` | Internal platform development | Core improvements |

### GitHub Label Creation Commands

```bash
# Priority labels
gh label create "priority/P0" --color "D73A49" --description "Critical - Production issue or revenue blocker"
gh label create "priority/P1" --color "FB8C00" --description "High - Important feature or significant bug"  
gh label create "priority/P2" --color "0366D6" --description "Medium - Standard feature or improvement"
gh label create "priority/P3" --color "28A745" --description "Low - Nice to have or minor improvement"

# Stream labels
gh label create "stream/wteg-client" --color "8B4513" --description "WTEG client-specific work"
gh label create "stream/ai-industry" --color "4B0082" --description "AI Development industry features"
gh label create "stream/platform" --color "2E8B57" --description "Core platform improvements"

# Type labels
gh label create "type/feature" --color "0366D6" --description "New feature implementation"
gh label create "type/enhancement" --color "7057FF" --description "Improvement to existing feature"
gh label create "type/bug" --color "D73A49" --description "Bug fix"
gh label create "type/refactor" --color "F9D71C" --description "Code refactoring without behavior change"
gh label create "type/test" --color "FBCA04" --description "Test-related work"
gh label create "type/docs" --color "0075CA" --description "Documentation updates"
gh label create "type/security" --color "B60205" --description "Security-related changes"

# Component labels  
gh label create "component/scraper" --color "FF6B35" --description "Web scraping engine"
gh label create "component/file-generator" --color "FF9F1C" --description "File generation system"
gh label create "component/web-interface" --color "2EC4B6" --description "Flask web UI"
gh label create "component/ai-integration" --color "9B59B6" --description "AI/LLM features"
gh label create "component/wteg" --color "8B4513" --description "WTEG-specific module"
gh label create "component/processors" --color "F72585" --description "Multi-modal processors"
gh label create "component/config" --color "4D5DB5" --description "Configuration management"
gh label create "component/testing" --color "FBCA04" --description "Testing infrastructure"

# Status labels
gh label create "status/needs-review" --color "FBCA04" --description "Ready for code review"
gh label create "status/in-progress" --color "0366D6" --description "Currently being worked on"
gh label create "status/blocked" --color "D73A49" --description "Cannot proceed due to dependency"
gh label create "status/testing" --color "28A745" --description "In testing phase"
gh label create "status/ready-to-merge" --color "2E8B57" --description "Approved and ready for merge"

# Client/Demo labels
gh label create "client/wteg" --color "8B4513" --description "Where To Eat Guide client"
gh label create "demo/agileaidev" --color "4B0082" --description "AgileAIDev.com demo features"
gh label create "internal/platform" --color "2E8B57" --description "Internal platform development"
```

---

## 3. Git Tags and Release Strategy

### Version Numbering Scheme
**Format**: `v{MAJOR}.{MINOR}.{PATCH}[-{SUFFIX}]`

- **MAJOR**: Breaking changes, new industry support
- **MINOR**: New features, enhancements  
- **PATCH**: Bug fixes, small improvements
- **SUFFIX**: `alpha`, `beta`, `rc1`, `hotfix`

### Release Categories

#### Production Releases
```bash
v1.4.0    # Current stable (Phase 4.3W.1 complete)
v1.4.1    # Patch release (bug fixes)
v1.5.0    # Minor release (WTEG enhancements)
v2.0.0    # Major release (AI industry support)
```

#### Client Delivery Tags
```bash
v1.4.0-wteg-delivery-20250725    # WTEG client milestone
v1.5.0-wteg-cms-integration      # WTEG CMS features
v2.0.0-ai-industry-demo          # AI industry demo
```

#### Development Milestone Tags
```bash
v1.5.0-alpha.1    # Early AI industry development
v1.5.0-beta.1     # AI industry testing phase  
v1.5.0-rc.1       # Release candidate
v2.0.0-demo       # AgileAIDev.com demo version
```

### Tag Creation Examples

```bash
# Production release
git tag -a v1.4.1 -m "Patch release: WTEG PDF processing fixes"
git push origin v1.4.1

# Client delivery
git tag -a v1.4.0-wteg-delivery-20250725 -m "WTEG client delivery milestone"
git push origin v1.4.0-wteg-delivery-20250725

# Development milestone
git tag -a v2.0.0-alpha.1 -m "Alpha release: AI industry extraction pipeline"
git push origin v2.0.0-alpha.1
```

### Release Branch Strategy

```bash
# Create release branch for v1.5.0
git checkout develop
git checkout -b release/v1.5.x
git push -u origin release/v1.5.x

# Tag release
git tag -a v1.5.0 -m "Release v1.5.0: WTEG enhancements and AI industry alpha"
git push origin v1.5.0

# Merge to main
git checkout main
git merge release/v1.5.x --no-ff
git push origin main

# Merge changes back to develop
git checkout develop  
git merge main
git push origin develop
```

---

## 4. Workflow Integration

### Pull Request Templates

#### Feature PR Template
```markdown
## Description
Brief description of changes

## Development Stream
- [ ] WTEG Client (priority/P0)
- [ ] AI Industry (priority/P1)  
- [ ] Platform Features (priority/P2)

## Type of Change
- [ ] New feature
- [ ] Enhancement
- [ ] Bug fix
- [ ] Refactor

## Testing
- [ ] Unit tests added/updated
- [ ] ATDD scenarios added/updated
- [ ] Manual testing completed
- [ ] Coverage maintained (95%+)

## Checklist
- [ ] Code follows TDD red-green-refactor
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] Breaking changes noted
```

### Issue Templates

#### WTEG Client Issue Template
```markdown
---
name: WTEG Client Issue
about: Issue related to WTEG client deliverables
title: '[WTEG] '
labels: 'stream/wteg-client, priority/P0, client/wteg'
assignees: ''
---

## Client Impact
Revenue impact and urgency level

## Description
Detailed description of the issue

## Acceptance Criteria
- [ ] Specific deliverable requirements
- [ ] Testing requirements
- [ ] Documentation requirements

## Priority Justification
Why this is P0/P1/P2
```

#### AI Industry Issue Template  
```markdown
---
name: AI Industry Feature
about: Feature for AI Development industry implementation
title: '[AI-INDUSTRY] '
labels: 'stream/ai-industry, priority/P1, demo/agileaidev'
assignees: ''
---

## Demo Requirements
AgileAIDev.com showcase needs

## Description
Feature description and business value

## Technical Approach
Implementation strategy

## Success Criteria
- [ ] Demo-ready functionality
- [ ] Performance benchmarks met
- [ ] Documentation complete
```

### Automated Workflows

#### Label Assignment Automation
```yaml
# .github/workflows/label-automation.yml
name: Auto Label Assignment
on:
  pull_request:
    types: [opened, edited]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - name: Label by branch pattern
        uses: actions/labeler@v4
        with:
          configuration-path: .github/labeler.yml
```

#### Labeler Configuration
```yaml
# .github/labeler.yml
'stream/wteg-client':
  - 'feature/wteg-*'
  - 'hotfix/wteg-*'

'stream/ai-industry':
  - 'feature/ai-industry-*'

'stream/platform':
  - 'feature/platform-*'

'component/scraper':
  - 'src/scraper/**/*'

'component/wteg':
  - 'src/wteg/**/*'

'type/test':
  - 'tests/**/*'
```

---

## 5. Implementation Timeline

### Phase 1: Infrastructure Setup (Week 1)
- [ ] Create branch structure
- [ ] Set up GitHub labels using provided commands
- [ ] Configure branch protection rules
- [ ] Create PR/issue templates

### Phase 2: Process Implementation (Week 2)  
- [ ] Train team on new workflows
- [ ] Set up automated labeling
- [ ] Create initial release tags
- [ ] Document procedures

### Phase 3: Stream Integration (Week 3-4)
- [ ] Migrate existing issues to new labels
- [ ] Establish release cadence
- [ ] Set up monitoring and metrics
- [ ] Refine based on usage

---

## 6. Monitoring and Metrics

### Key Performance Indicators
- **WTEG Stream Velocity**: Issues completed per sprint
- **AI Industry Progress**: Features delivered toward Q3 2025 target
- **Platform Health**: Technical debt reduction rate
- **Release Cadence**: Time from feature complete to production

### Dashboard Tracking
- Issues by stream and priority
- Pull request cycle time
- Test coverage by component
- Release deployment success rate

### Weekly Review Process
1. **Monday**: Stream priority review and planning
2. **Wednesday**: Cross-stream dependency check
3. **Friday**: Release readiness assessment

---

## 7. Risk Mitigation

### Branch Conflicts
- **Risk**: Multiple streams modifying same components
- **Mitigation**: Regular develop branch integration, conflict resolution procedures

### Client Delivery Pressure
- **Risk**: WTEG urgency compromising code quality  
- **Mitigation**: Dedicated WTEG integration branch, protected TDD workflow

### Resource Allocation
- **Risk**: Stream priority conflicts
- **Mitigation**: Clear P0/P1/P2 definitions, escalation procedures

---

## 8. Success Criteria

### Technical Success
- [ ] Zero deployment failures due to branch conflicts
- [ ] 95%+ test coverage maintained across all streams
- [ ] TDD workflow preserved during high-pressure deliveries

### Business Success  
- [ ] WTEG client deliverables on time
- [ ] AI industry demo ready for Q3 2025
- [ ] Platform scalability improved for multi-industry support

### Process Success
- [ ] Development team velocity improved
- [ ] Clear visibility into stream progress
- [ ] Reduced context switching between priorities

---

## Conclusion

This git infrastructure plan provides the foundation for managing three parallel development streams while maintaining code quality and delivery commitments. The combination of strategic branching, comprehensive labeling, and disciplined release management will enable successful execution of the RAG_Scraper roadmap.

**Next Steps**: 
1. Execute Phase 1 infrastructure setup using provided commands
2. Begin migrating current issues to new label system
3. Establish first WTEG client delivery milestone using release tagging strategy

*Generated for RAG_Scraper project following TDD methodology and Agile best practices*