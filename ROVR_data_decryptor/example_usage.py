#!/usr/bin/env python3
"""
Decryption Tool Usage Example

This script demonstrates how to use the data_decryptor.py tool.
Please modify the paths according to your actual situation before use.
"""

import os
import subprocess
import tempfile
from pathlib import Path

def create_test_environment():
    """Create test environment"""
    print("🔧 Creating test environment...")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="decryptor_test_"))
    print(f"📁 Test directory: {temp_dir}")
    
    # Create input directory structure
    input_dir = temp_dir / "encrypted_files"
    output_dir = temp_dir / "decrypted_files"
    
    # Create some example directory structures
    (input_dir / "2024-09-01" / "device_001").mkdir(parents=True)
    (input_dir / "2024-09-01" / "device_002").mkdir(parents=True)
    (input_dir / "2024-09-02").mkdir(parents=True)
    
    # Create example encrypted files (just create empty files for demonstration)
    test_files = [
        "2024-09-01/device_001/20240901100000-1025040001-1-Debq.data",
        "2024-09-01/device_001/20240901100030-1025040001-2-Debq.data", 
        "2024-09-01/device_002/20240901100000-1025040002-1-AbCd.gga",
        "2024-09-02/20240902080000-1025040003-1-1234.data"
    ]
    
    for file_path in test_files:
        full_path = input_dir / file_path
        # Create some example encrypted content (this is just for demonstration, should be real encrypted binary data in practice)
        with open(full_path, 'w') as f:
            f.write("This is example encrypted file content - should be binary encrypted data in actual use")
    
    # Create key file
    key_file = temp_dir / "keys.txt"
    with open(key_file, 'w') as f:
        f.write("""# Example key file
# One 32-character key per line, first four characters used for filename matching

# Example key 1 - prefix: Debq (32 characters)
DebqXYZ12345678901234567890123456

# Example key 2 - prefix: AbCd (32 characters)  
AbCdEFG12345678901234567890123456

# Example key 3 - prefix: 1234 (32 characters)
12345678901234567890123456789012
""")
    
    return input_dir, output_dir, key_file, temp_dir

def run_decryptor_example():
    """Run decryption tool example"""
    print("🚀 Data File Decryption Tool Usage Example")
    print("=" * 50)
    
    # Create test environment
    input_dir, output_dir, key_file, temp_dir = create_test_environment()
    
    # Build command
    script_path = Path(__file__).parent / "data_decryptor.py"
    cmd = [
        "python3", str(script_path),
        str(input_dir),
        str(output_dir), 
        str(key_file),
        "--error-log", str(temp_dir / "errors.log")
    ]
    
    print(f"📋 Executing command:")
    print(" ".join(cmd))
    print()
    
    try:
        # Run decryption tool
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📤 Tool output:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Error output:")
            print(result.stderr)
            
        print(f"🔄 Return code: {result.returncode}")
        
        # Display result directory structure
        print("\n📁 Output directory structure:")
        if output_dir.exists():
            for item in sorted(output_dir.rglob("*")):
                if item.is_file():
                    relative_path = item.relative_to(output_dir)
                    print(f"  📄 {relative_path}")
        else:
            print("  (Output directory does not exist)")
            
        # Check error log
        error_log = temp_dir / "errors.log"
        if error_log.exists() and error_log.stat().st_size > 0:
            print(f"\n📝 Error log content:")
            with open(error_log, 'r') as f:
                print(f.read())
                
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        
    finally:
        print(f"\n🗂️ Test files saved at: {temp_dir}")
        print("💡 You can check these files to understand the tool's execution results")

def show_real_usage_example():
    """Show real usage example"""
    print("\n" + "=" * 50)
    print("📖 Real Usage Example")
    print("=" * 50)
    
    print("""
In actual use, you need to:

1. Prepare encrypted files directory:
   /path/to/your/encrypted_files/
   ├── 20250915053307-1025040007-1-Debq.data
   ├── 20250915053308-1025040007-2-Debq.data
   └── subfolder/
       └── 20250915053309-1025040008-1-AbCd.gga

2. Prepare key file (keys.txt):
   DebqXYZ123456789012345678901234
   AbCdEFG789012345678901234567890

3. Run command:
   python3 data_decryptor.py \\
       /path/to/your/encrypted_files \\
       /path/to/output \\
       /path/to/keys.txt

4. Check results:
   - Decrypted files will be saved in output directory
   - Maintain original directory structure
   - Error information recorded in log file
""")

if __name__ == "__main__":
    run_decryptor_example()
    show_real_usage_example()