import os
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def count_repository_files(root_path: str, exclude_patterns=None):
    """
    Count files and directories in the repository.
    
    Args:
        root_path: Repository root directory
        exclude_patterns: List of patterns to exclude (e.g., ['.git', '__pycache__', '.venv'])
    
    Returns:
        Dictionary with file counts and statistics
    """
    if exclude_patterns is None:
        exclude_patterns = [
            '.git', '__pycache__', '.venv', 'venv', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build',
            '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd'
        ]
    
    stats = {
        'total_files': 0,
        'total_dirs': 0,
        'total_size_bytes': 0,
        'file_types': defaultdict(int),
        'largest_files': [],
        'directory_counts': defaultdict(int),
        'excluded_items': 0
    }
    
    def should_exclude(path_str):
        """Check if path should be excluded based on patterns."""
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                # Wildcard pattern
                if path_str.endswith(pattern[1:]):
                    return True
            else:
                # Directory or exact match
                if pattern in path_str:
                    return True
        return False
    
    print(f"🔍 Scanning repository: {root_path}")
    print(f"📋 Exclude patterns: {exclude_patterns}")
    print("-" * 60)
    
    # Walk through all files and directories
    for root, dirs, files in os.walk(root_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
        
        # Count directories
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, root_path)
            
            if not should_exclude(rel_path):
                stats['total_dirs'] += 1
                # Count files per directory
                parent_dir = os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else 'root'
                stats['directory_counts'][parent_dir] += 1
        
        # Count files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(file_path, root_path)
            
            if should_exclude(rel_path):
                stats['excluded_items'] += 1
                continue
            
            try:
                file_size = os.path.getsize(file_path)
                stats['total_files'] += 1
                stats['total_size_bytes'] += file_size
                
                # File extension statistics
                ext = Path(file_name).suffix.lower()
                if not ext:
                    ext = '[no extension]'
                stats['file_types'][ext] += 1
                
                # Track largest files
                stats['largest_files'].append((rel_path, file_size))
                
                # Directory file count
                parent_dir = os.path.dirname(rel_path) if os.path.dirname(rel_path) != '.' else 'root'
                stats['directory_counts'][parent_dir] += 1
                
            except (OSError, IOError):
                # Skip files that can't be accessed
                stats['excluded_items'] += 1
    
    # Sort largest files
    stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
    stats['largest_files'] = stats['largest_files'][:20]  # Keep top 20
    
    return stats


def format_size(bytes_size):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def print_report(stats):
    """Print detailed file count report."""
    print("\n" + "=" * 60)
    print("📊 REPOSITORY FILE COUNT REPORT")
    print("=" * 60)
    
    print(f"\n📁 SUMMARY:")
    print(f"   Total Files: {stats['total_files']:,}")
    print(f"   Total Directories: {stats['total_dirs']:,}")
    print(f"   Total Size: {format_size(stats['total_size_bytes'])}")
    print(f"   Excluded Items: {stats['excluded_items']:,}")
    
    print(f"\n📋 FILE TYPES (Top 15):")
    sorted_types = sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True)
    for ext, count in sorted_types[:15]:
        print(f"   {ext:<15} {count:>6,} files")
    
    print(f"\n📂 DIRECTORIES WITH MOST FILES (Top 15):")
    sorted_dirs = sorted(stats['directory_counts'].items(), key=lambda x: x[1], reverse=True)
    for dir_name, count in sorted_dirs[:15]:
        print(f"   {dir_name:<40} {count:>6,} items")
    
    print(f"\n🔍 LARGEST FILES (Top 10):")
    for file_path, size in stats['largest_files'][:10]:
        print(f"   {format_size(size):<10} {file_path}")
    
    print(f"\n🚨 OVERLEAF IMPORT ANALYSIS:")
    print(f"   • Overleaf file limit: ~2,000-3,000 files (typical)")
    print(f"   • Your repository: {stats['total_files']:,} files")
    
    if stats['total_files'] > 3000:
        print(f"   ❌ EXCEEDS LIMIT - Repository too large for Overleaf")
        print(f"   💡 Suggestions:")
        print(f"      - Exclude data/ directory ({stats['directory_counts'].get('data', 0):,} items)")
        print(f"      - Exclude figure/ directory ({stats['directory_counts'].get('figure', 0):,} items)")
        print(f"      - Exclude image/ directory ({stats['directory_counts'].get('image', 0):,} items)")
        print(f"      - Keep only manuscript/ and reference/ directories")
    elif stats['total_files'] > 2000:
        print(f"   ⚠️  BORDERLINE - May exceed some Overleaf limits")
        print(f"   💡 Consider excluding large directories")
    else:
        print(f"   ✅ WITHIN LIMITS - Should import successfully")


def main():
    """Main function to run file count analysis."""
    # Repository root (two levels up from this script)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    print("🔍 Repository File Counter for Overleaf Import Analysis")
    print(f"📁 Repository: {repo_root}")
    
    # Standard exclusions for code repositories
    exclude_patterns = [
        '.git', '__pycache__', '.venv', 'venv', 'node_modules',
        '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build',
        '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd', '*.egg-info',
        '.coverage', '.vscode', '.idea', '*.log'
    ]
    
    # Count files
    stats = count_repository_files(repo_root, exclude_patterns)
    
    # Print report
    print_report(stats)
    
    # Additional analysis for manuscript-only import
    print(f"\n📝 MANUSCRIPT-ONLY ANALYSIS:")
    manuscript_dir = os.path.join(repo_root, "manuscript")
    reference_dir = os.path.join(repo_root, "reference")
    
    manuscript_files = 0
    reference_files = 0
    
    if os.path.exists(manuscript_dir):
        for root, dirs, files in os.walk(manuscript_dir):
            manuscript_files += len(files)
    
    if os.path.exists(reference_dir):
        for root, dirs, files in os.walk(reference_dir):
            reference_files += len(files)
    
    total_manuscript = manuscript_files + reference_files
    print(f"   manuscript/ directory: {manuscript_files:,} files")
    print(f"   reference/ directory: {reference_files:,} files")
    print(f"   Total for LaTeX work: {total_manuscript:,} files")
    
    if total_manuscript < 1000:
        print(f"   ✅ RECOMMENDED: Import only manuscript/ and reference/ directories")
    else:
        print(f"   ⚠️  Even manuscript subset is large: {total_manuscript:,} files")


if __name__ == "__main__":
    main()
