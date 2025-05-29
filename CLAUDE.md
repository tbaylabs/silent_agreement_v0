# Claude Code Git Worktree Workflow

This file documents the git worktree workflow for parallel Claude Code instances.

## Current Branch Status
- **Main integration branch**: `version_1` (not main)
- All feature work should eventually merge back to `version_1`

## Why This Workflow Exists
Due to Claude Code's security restrictions:
- Claude cannot change directories or delete directories it's currently working in
- All directory navigation and worktree cleanup must be done by the user
- Claude provides copy-paste commands for the user to execute manually

## Worktree Workflow

### Creating a New Feature Worktree
When asked to create a new worktree:
1. If no feature name is provided, ask: "What feature are you working on?" to properly name the branch
2. Create worktree: `git worktree add ../silent_agreement_v0_[feature-name] -b feature/[feature-name]`
3. Provide the user with copy-paste commands to open new Claude Code instance

#### Commands to provide to user for new worktree:
```bash
cd ../silent_agreement_v0_[feature-name]
claude
```

### Completing Feature Work and Transitioning
When told a feature is complete and to move to a new feature:

#### Step 1: Claude's Actions
1. Ensure all work is committed in current worktree
2. Create the new worktree: `git worktree add ../silent_agreement_v0_[new-feature-name] -b feature/[new-feature-name]`

#### Step 2: User Manual Actions
Claude will provide commands for the user to copy-paste:
```bash
# Navigate to new worktree
cd ../silent_agreement_v0_[new-feature-name]

# Switch to version_1 branch and merge completed feature
git checkout version_1
git merge feature/[completed-feature-name]

# Delete the completed feature branch
git branch -d feature/[completed-feature-name]

# Remove the old worktree directory
rm -rf ../silent_agreement_v0_[completed-feature-name]

# Start Claude in new worktree
claude
```

### Completing Feature Work Without New Feature
When told to close/merge a feature without starting a new one:

#### Step 1: Claude's Actions
1. Ensure all work is committed

#### Step 2: User Manual Actions
Claude will provide commands for the user to copy-paste:
```bash
# Navigate back to main worktree
cd /Users/graemeford/TBayLabs/silent_agreement_v0

# Switch to version_1 branch and merge feature
git checkout version_1
git merge feature/[feature-name]

# Delete the feature branch
git branch -d feature/[feature-name]

# Remove the worktree directory
rm -rf ../silent_agreement_v0_[feature-name]

# Start Claude in main directory
claude
```

## Running Scripts in Worktrees

When working in a git worktree, Python scripts need to be run with the correct module path. Use this approach:

```bash
# From within the worktree directory, run scripts with inline PYTHONPATH
PYTHONPATH=. python scripts/run_base_eval.py <model> <test_mode>

# Example: Quick test with Groq Llama 3.3
PYTHONPATH=. python scripts/run_base_eval.py groq/llama-3.3-70b-versatile quick-test
```

This sets the Python path for just that command execution, allowing the script to find the project modules.

## Notes
- This file (CLAUDE.md) is tracked by git and contains project instructions
- Each Claude Code instance can work in parallel using separate worktrees
- Always merge back to `version_1`, not `main`
- All directory navigation and cleanup requires manual user action due to Claude's security restrictions
- Use `PYTHONPATH=.` prefix when running Python scripts in worktrees