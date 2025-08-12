#!/usr/bin/env python3
"""
Remove the problematic 'nationality' field from mathematicians.json
Previous pipeline defaulted everyone to "European" or "French" which is inaccurate.
"""

import json
from pathlib import Path
from datetime import datetime

def load_json(file_path: Path) -> dict:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path: Path, data: dict, indent: int = 2) -> None:
    """Save JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def main():
    """Remove nationality field from mathematicians data"""
    print("=== Removing Nationality Field ===")
    
    # Load mathematicians data
    frontend_path = Path('../frontend/public/data/mathematicians.json')
    pipeline_path = Path('data/json/mathematicians.json')
    
    mathematicians = load_json(frontend_path)
    print(f"Loaded {len(mathematicians)} mathematicians")
    
    # Count nationality values before removal
    nationality_counts = {}
    total_with_nationality = 0
    
    for mathematician_id, data in mathematicians.items():
        if 'nationality' in data:
            nationality = data['nationality']
            nationality_counts[nationality] = nationality_counts.get(nationality, 0) + 1
            total_with_nationality += 1
    
    print(f"\n=== Current Nationality Distribution ===")
    for nationality, count in sorted(nationality_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{count:2d}: {nationality}")
    
    print(f"\nTotal mathematicians with nationality field: {total_with_nationality}")
    
    # Remove nationality field from all mathematicians
    removed_count = 0
    for mathematician_id, data in mathematicians.items():
        if 'nationality' in data:
            del data['nationality']
            removed_count += 1
    
    print(f"\n=== Results ===")
    print(f"Removed nationality field from {removed_count} mathematicians")
    
    # Add metadata about the cleanup
    for mathematician_id, data in mathematicians.items():
        if 'data_source' not in data:
            data['data_source'] = 'wikipedia_lm_studio_pipeline'
        
        # Update processed timestamp
        data['nationality_removed_at'] = datetime.now().isoformat()
    
    # Save both files
    save_json(frontend_path, mathematicians)
    print(f"✓ Updated: {frontend_path}")
    
    # Update pipeline copy if it exists
    if pipeline_path.exists():
        save_json(pipeline_path, mathematicians)
        print(f"✓ Updated: {pipeline_path}")
    
    # Verify removal
    verification = load_json(frontend_path)
    remaining_with_nationality = sum(1 for data in verification.values() if 'nationality' in data)
    
    print(f"\n=== Verification ===")
    print(f"Remaining mathematicians with nationality field: {remaining_with_nationality}")
    
    if remaining_with_nationality == 0:
        print("✅ Successfully removed all nationality fields")
    else:
        print("⚠️  Some nationality fields still remain")
    
    # Show sample mathematician entry structure
    sample_key = list(mathematicians.keys())[0]
    sample_keys = list(mathematicians[sample_key].keys())
    print(f"\n=== Sample Entry Structure ({sample_key}) ===")
    for key in sorted(sample_keys):
        print(f"  - {key}")

if __name__ == '__main__':
    main()