# Setting Up Claude Code Reviews

This repository uses Claude Code for automated PR reviews. Follow these steps to enable it:

## Prerequisites

1. **Install Claude GitHub App**
   - Go to [Claude Code GitHub App](https://github.com/apps/claude-code)
   - Install it on your repository

2. **Get API Key**
   - Option A: Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
   - Option B: Use Claude Code OAuth token

## Repository Setup

1. **Add Secret**
   - Go to Settings → Secrets and variables → Actions
   - Add new repository secret: `ANTHROPIC_API_KEY`
   - Paste your API key

2. **Workflows Already Configured**
   This repository includes two workflows:
   
   - `.github/workflows/claude-review.yml` - Responds to @claude mentions
   - `.github/workflows/pr-review.yml` - Auto-reviews new PRs

## Usage

### Automatic Reviews
Every new PR automatically gets reviewed when opened or updated.

### Manual Reviews
Comment `@claude` followed by your question in any PR or issue:
```
@claude Can you review the error handling in this PR?
```

### Review Focus Areas
Claude will check:
- Python code quality and best practices
- Home Assistant Add-on conventions
- Security vulnerabilities
- Error handling
- Test coverage
- Documentation completeness

## Customization

Edit `.github/workflows/pr-review.yml` to customize the review prompt or criteria.