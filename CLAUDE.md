# Claude Code Git Worktree Workflow

This file documents the git worktree workflow for parallel Claude Code instances.

## Current Branch Status
- **Main integration branch**: `version_1` (not main)
- All feature work should eventually merge back to `version_1`

## Worktree Workflow

### Creating a New Feature Worktree
When asked to create a new worktree:
1. If no feature name is provided, ask: "What feature are you working on?" to properly name the branch
2. Create worktree: `git worktree add ../silent_agreement_v0_[feature-name] -b feature/[feature-name]`
3. **IMPORTANT**: Claude Code cannot switch to the worktree directory due to security restrictions
4. Provide the user with copy-paste commands to open new Claude Code instance
5. User must manually run the commands to start working in the new worktree

#### Commands to provide to user:
```bash
cd ../silent_agreement_v0_[feature-name]
claude
```

### Completing Feature Work
When told to close/merge a feature:
1. Ensure all work is committed
2. Switch back to main worktree: `cd /Users/graemeford/TBayLabs/silent_agreement_v0`
3. Switch to version_1 branch: `git checkout version_1`
4. Merge feature branch: `git merge feature/[feature-name]`
5. Delete worktree: `git worktree remove ../silent_agreement_v0_[feature-name]`
6. Delete feature branch: `git branch -d feature/[feature-name]`

### Next Steps After Completion
- If you know the next feature to work on, create a new worktree automatically
- Otherwise, ask for next instructions

## Notes
- This file (claude.local.md) is local only and not tracked by git
- Each Claude Code instance can work in parallel using separate worktrees
- Always merge back to `version_1`, not `main`