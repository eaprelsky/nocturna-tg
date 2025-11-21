# Essential Git Commands
# Authorization

## SSH Key Setup

### Generate SSH Key
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# Or for older systems:
ssh-keygen -t rsa -b 4096 -C "your.email@example.com"
```

### Add SSH Key to SSH Agent
```bash
eval "$(ssh-agent -s)"          # Start SSH agent
ssh-add ~/.ssh/id_ed25519       # Add private key to agent
```

### Add Public Key to GitHub/GitLab
```bash
cat ~/.ssh/id_ed25519.pub       # Display public key to copy
# Copy the output and add it to your GitHub/GitLab account:
# GitHub: Settings → SSH and GPG keys → New SSH key
# GitLab: Preferences → SSH Keys → Add key
```

### Test SSH Connection
```bash
ssh -T git@github.com           # Test GitHub connection
ssh -T git@gitlab.com           # Test GitLab connection
```

## HTTPS Authentication

### Personal Access Tokens
For HTTPS authentication, use Personal Access Tokens instead of passwords:

#### GitHub
1. Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with appropriate permissions
3. Use token as password when prompted

#### GitLab
1. User Settings → Access Tokens
2. Create personal access token with required scopes
3. Use token as password

### Credential Storage
```bash
# Store credentials temporarily (15 minutes)
git config --global credential.helper cache

# Store credentials for longer (1 hour)
git config --global credential.helper 'cache --timeout=3600'

# Store credentials permanently (use with caution)
git config --global credential.helper store
```

## Switching Between HTTPS and SSH

### Change Remote URL to SSH
```bash
git remote set-url origin git@github.com:username/repository.git
```

### Change Remote URL to HTTPS
```bash
git remote set-url origin https://github.com/username/repository.git
```

### Check Current Remote URL
```bash
git remote -v                   # Show current remote URLs
```

## Basic Configuration
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Repository Management
```bash
git init                    # Initialize new repository
git clone <url>            # Clone remote repository
git remote add origin <url> # Add remote repository
```

## Basic Operations
```bash
git status                 # Check repository status
git add <file>            # Stage specific file
git add .                 # Stage all changes
git commit -m "message"   # Commit staged changes
git log                   # View commit history
```

## Branching
```bash
git branch                # List branches
git branch <name>         # Create new branch
git checkout <branch>     # Switch to branch
git checkout -b <name>    # Create and switch to new branch
git merge <branch>        # Merge branch into current
```

## Remote Operations
```bash
git pull                  # Fetch and merge remote changes
git push                  # Push commits to remote
git fetch                 # Download remote changes
git push -u origin <branch> # Push and set upstream
```

## Undoing Changes
```bash
git restore <file>        # Discard changes in working directory
git reset HEAD <file>     # Unstage changes
git revert <commit>       # Create new commit that undoes changes
git reset --hard <commit> # Reset to specific commit (caution!)
```

## Stashing
```bash
git stash                 # Save changes temporarily
git stash pop            # Apply and remove most recent stash
git stash list           # List all stashes
```

## Advanced
```bash
git rebase <branch>      # Reapply commits on top of another branch
git cherry-pick <commit> # Apply specific commit to current branch
git tag <name>           # Create tag
git blame <file>         # Show who changed what and when
```

## Tips
- Use `git status` frequently to check your working directory
- Write clear, descriptive commit messages
- Pull before pushing to avoid conflicts
- Create feature branches for new work
- Review changes with `git diff` before committing
