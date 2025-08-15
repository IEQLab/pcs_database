import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def count_all_files_including_hidden(root_path: str):
    """
    Count ALL files including .git, hidden files, and system files.
    This matches what Git/Overleaf would see when importing.
    """
    stats = {
        'total_files': 0,
        'git_files': 0,
        'hidden_files': 0,
        'large_directories': {},
        'all_files_list': []
    }
    
    print(f"🔍 Counting ALL files (including hidden) in: {root_path}")
    print("-" * 60)
    
    for root, dirs, files in os.walk(root_path):
        # Count all files (no exclusions)
        for file_name in files:
            file_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(file_path, root_path)
            
            stats['total_files'] += 1
            stats['all_files_list'].append(rel_path)
            
            # Track .git files
            if '.git' in rel_path:
                stats['git_files'] += 1
            
            # Track hidden files (start with .)
            if file_name.startswith('.'):
                stats['hidden_files'] += 1
        
        # Count files per directory
        current_dir = os.path.relpath(root, root_path)
        if current_dir == '.':
            current_dir = 'root'
        
        file_count = len(files)
        if file_count > 0:
            stats['large_directories'][current_dir] = file_count
    
    return stats


def check_git_repository_size():
    """Check .git directory specifically."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    git_dir = os.path.join(repo_root, '.git')
    
    if not os.path.exists(git_dir):
        return {'exists': False, 'files': 0}
    
    git_files = 0
    git_size = 0
    
    for root, dirs, files in os.walk(git_dir):
        git_files += len(files)
        for file in files:
            try:
                git_size += os.path.getsize(os.path.join(root, file))
            except:
                pass
    
    return {
        'exists': True,
        'files': git_files,
        'size_mb': git_size / (1024 * 1024)
    }


def analyze_overleaf_import_issue():
    """Analyze why Overleaf import might be failing."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    print("🚨 OVERLEAF IMPORT ISSUE ANALYSIS")
    print("=" * 60)
    
    # Count all files (including hidden)
    all_stats = count_all_files_including_hidden(repo_root)
    
    # Check .git specifically
    git_stats = check_git_repository_size()
    
    print(f"\n📊 COMPLETE FILE COUNT:")
    print(f"   Total files (including ALL hidden): {all_stats['total_files']:,}")
    print(f"   .git directory files: {git_stats['files']:,}" if git_stats['exists'] else "   .git directory: Not found")
    print(f"   Other hidden files: {all_stats['hidden_files'] - git_stats['files']:,}")
    
    print(f"\n🔍 DIRECTORY BREAKDOWN (files per directory):")
    sorted_dirs = sorted(all_stats['large_directories'].items(), 
                        key=lambda x: x[1], reverse=True)
    
    for dir_name, count in sorted_dirs[:20]:
        if count > 10:  # Only show directories with significant file counts
            print(f"   {dir_name:<50} {count:>6,} files")
    
    print(f"\n🎯 OVERLEAF LIMITS ANALYSIS:")
    
    # Overleaf known limits (as of 2024/2025)
    overleaf_limits = {
        'free_account': 60,      # Very restrictive
        'personal_plan': 2000,   # Standard limit
        'group_plan': 10000,     # Higher limit
        'institutional': 10000   # Varies by institution
    }
    
    total_files = all_stats['total_files']
    
    print(f"   Your repository: {total_files:,} files")
    print(f"   Overleaf Free: {overleaf_limits['free_account']} files max ❌")
    print(f"   Overleaf Personal: {overleaf_limits['personal_plan']} files max", 
          "❌" if total_files > overleaf_limits['personal_plan'] else "✅")
    print(f"   Overleaf Group/Institutional: {overleaf_limits['group_plan']} files max", 
          "❌" if total_files > overleaf_limits['group_plan'] else "✅")
    
    # Git-specific issues
    if git_stats['exists']:
        print(f"\n🔧 GIT REPOSITORY ISSUES:")
        print(f"   .git directory: {git_stats['files']:,} files ({git_stats['size_mb']:.1f} MB)")
        print(f"   🚨 LIKELY CAUSE: Overleaf cannot import Git repositories directly!")
        print(f"   💡 SOLUTION: Export without .git history")
    
    # Specific file type issues
    large_files = []
    for file_path in all_stats['all_files_list'][:100]:  # Check first 100 files
        full_path = os.path.join(repo_root, file_path)
        try:
            size = os.path.getsize(full_path)
            if size > 50 * 1024 * 1024:  # >50MB
                large_files.append((file_path, size / (1024 * 1024)))
        except:
            pass
    
    if large_files:
        print(f"\n📁 LARGE FILES (>50MB) - May cause issues:")
        for file_path, size_mb in large_files[:5]:
            print(f"   {size_mb:.1f} MB - {file_path}")
    
    print(f"\n💡 RECOMMENDED SOLUTIONS:")
    
    if git_stats['exists']:
        print(f"   1. 🎯 MAIN ISSUE: Use 'Download ZIP' instead of Git import")
        print(f"      - GitHub → Code → Download ZIP")
        print(f"      - This excludes .git directory ({git_stats['files']:,} files)")
    
    manuscript_count = all_stats['large_directories'].get('manuscript', 0) + \
                      all_stats['large_directories'].get('manuscript/src', 0)
    
    if manuscript_count > 0:
        print(f"   2. ✅ ALTERNATIVE: Import only manuscript/ directory ({manuscript_count:,} files)")
        print(f"      - Much smaller and focused on LaTeX work")
    
    if total_files > 2000:
        print(f"   3. ⚠️  UPGRADE: Consider Overleaf Group plan for larger repositories")
    
    return all_stats


def main():
    """Main analysis function."""
    print("🔍 Overleaf Import Issue Analyzer")
    analyze_overleaf_import_issue()
    
    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY: Most likely issue is Git repository import.")
    print("   Try: GitHub → Code → Download ZIP → Import ZIP to Overleaf")
    print("=" * 60)


if __name__ == "__main__":
    main()
