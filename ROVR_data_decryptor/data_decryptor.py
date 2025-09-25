#!/usr/bin/env python3
"""
Data File Decryption Tool

Usage:
    python data_decryptor.py <encrypted_files_dir> <output_dir> <key_file_path>

Description:
    - encrypted_files_dir: Directory containing encrypted files, supports multi-level directory scanning
    - output_dir: Output directory for decrypted files, preserves original directory structure
    - key_file_path: Text file containing encryption keys, one key per line
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from Crypto.Cipher import AES
from tqdm import tqdm
import logging
from datetime import datetime


class DataDecryptor:
    """Data File Decryptor"""
    
    def __init__(self, input_dir: str, output_dir: str, key_file: str, error_log: str = None):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.key_file = Path(key_file)
        self.error_log = error_log or f"decryption_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Initialize key mapping dictionary {first_four_chars: full_key}
        self.key_mapping: Dict[str, str] = {}
        
        # Setup error logging
        self._setup_error_logging()
        
    def _setup_error_logging(self):
        """Setup error logging"""
        self.error_logger = logging.getLogger('decryption_errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # Create file handler
        handler = logging.FileHandler(self.error_log, encoding='utf-8')
        handler.setLevel(logging.ERROR)
        
        # Set format
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.error_logger.addHandler(handler)
        
    def validate_inputs(self) -> bool:
        """Validate input parameters"""
        print("🔍 Validating input parameters...")
        
        # Validate encrypted files directory
        if not self.input_dir.exists():
            print(f"❌ Error: Encrypted files directory does not exist: {self.input_dir}")
            return False
        if not self.input_dir.is_dir():
            print(f"❌ Error: Encrypted files path is not a directory: {self.input_dir}")
            return False
            
        # Validate key file
        if not self.key_file.exists():
            print(f"❌ Error: Key file does not exist: {self.key_file}")
            return False
        if not self.key_file.is_file():
            print(f"❌ Error: Key path is not a file: {self.key_file}")
            return False
            
        # Create output directory
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Output directory prepared: {self.output_dir}")
        except Exception as e:
            print(f"❌ Error: Cannot create output directory {self.output_dir}: {e}")
            return False
            
        print("✅ Input parameters validation passed")
        return True
        
    def load_keys(self) -> bool:
        """Load keys from key file"""
        print(f"🔑 Loading key file: {self.key_file}")
        
        try:
            with open(self.key_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            key_count = 0
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue
                    
                # Validate key format (32 characters)
                if len(line) != 32:
                    print(f"⚠️  Warning: Line {line_num} key length incorrect (should be 32 characters): {line}")
                    continue
                    
                # Extract first four characters as key
                prefix = line[:4]
                if prefix in self.key_mapping:
                    print(f"⚠️  Warning: Line {line_num} key prefix duplicated: {prefix}")
                
                self.key_mapping[prefix] = line
                key_count += 1
                
            print(f"✅ Successfully loaded {key_count} keys")
            return key_count > 0
            
        except Exception as e:
            print(f"❌ Error: Cannot read key file: {e}")
            return False
            
    def scan_encrypted_files(self) -> List[Path]:
        """Recursively scan encrypted files"""
        print(f"📁 Scanning encrypted files directory: {self.input_dir}")
        
        encrypted_files = []
        
        # Recursively scan .data and .gga files
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.data', '.gga']:
                encrypted_files.append(file_path)
                
        print(f"✅ Found {len(encrypted_files)} encrypted files")
        return encrypted_files
        
    def extract_key_prefix(self, file_path: Path) -> Optional[str]:
        """Extract key prefix from filename"""
        filename = file_path.name
        
        # Filename format: 20250915053307-1025040007-1-Debq.data
        # Extract first four characters of the last segment (excluding extension)
        pattern = r'^.+-(.{4})\.(data|gga)$'
        match = re.match(pattern, filename, re.IGNORECASE)
        
        if match:
            return match.group(1)
        else:
            return None
            
    def get_relative_path(self, file_path: Path) -> Path:
        """Get file path relative to input directory"""
        return file_path.relative_to(self.input_dir)
        
    def decrypt_file_aes_cfb(self, encrypted_file_path: Path, decrypted_file_path: Path, encryption_key: str) -> bool:
        """
        Decrypt file using AES CFB mode - consistent with Go version algorithm
        encryption_key: 32-character string, first 16 chars as key, last 16 chars as iv
        """
        try:
            # Extract key and iv from 32-character string
            if len(encryption_key) != 32:
                raise ValueError("Encryption key must be 32 characters long")
            
            key = encryption_key[:16].encode('utf-8')
            iv = encryption_key[16:].encode('utf-8')
            
            # Ensure output directory exists
            decrypted_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read entire encrypted file into memory
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            # Create AES CFB decryptor
            cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128)
            
            # Decrypt entire file at once
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Write decrypted file
            with open(decrypted_file_path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted_data)
            
            return True
            
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")
            
    def process_files(self, files: List[Path]) -> Tuple[int, int]:
        """Process file list, return success and failure counts"""
        success_count = 0
        error_count = 0
        
        print(f"🚀 Starting to process {len(files)} files...")
        
        # Use tqdm to display progress bar
        with tqdm(files, desc="Decryption Progress", unit="files") as pbar:
            for file_path in pbar:
                try:
                    # Update progress bar description
                    pbar.set_postfix_str(f"Processing: {file_path.name}")
                    
                    # Extract key prefix
                    key_prefix = self.extract_key_prefix(file_path)
                    if not key_prefix:
                        raise Exception(f"Cannot extract key prefix from filename: {file_path.name}")
                    
                    # Find key
                    if key_prefix not in self.key_mapping:
                        raise Exception(f"No corresponding key found, prefix: {key_prefix}")
                    
                    encryption_key = self.key_mapping[key_prefix]
                    
                    # Calculate output file path (preserve directory structure)
                    relative_path = self.get_relative_path(file_path)
                    output_file_path = self.output_dir / relative_path
                    
                    # Decrypt file
                    self.decrypt_file_aes_cfb(file_path, output_file_path, encryption_key)
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"File: {file_path} | Error: {str(e)}"
                    self.error_logger.error(error_msg)
                    
                    # Also display error in console (without interrupting progress bar)
                    tqdm.write(f"❌ {error_msg}")
                    
        return success_count, error_count
        
    def run(self) -> bool:
        """Run decryption tool"""
        print("🔓 Data File Decryption Tool Started")
        print("=" * 50)
        
        # Validate input parameters
        if not self.validate_inputs():
            return False
            
        # Load keys
        if not self.load_keys():
            return False
            
        # Scan files
        files = self.scan_encrypted_files()
        if not files:
            print("⚠️  No files found that need decryption")
            return True
            
        # Process files
        success_count, error_count = self.process_files(files)
        
        # Output result statistics
        print("\n" + "=" * 50)
        print("📊 Processing Result Statistics:")
        print(f"✅ Successfully decrypted: {success_count} files")
        print(f"❌ Decryption failed: {error_count} files")
        print(f"📁 Output directory: {self.output_dir}")
        
        if error_count > 0:
            print(f"📝 Error log: {self.error_log}")
            
        return error_count == 0


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Data File Decryption Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python data_decryptor.py /path/to/encrypted /path/to/output /path/to/keys.txt

Filename format:
    20250915053307-1025040007-1-Debq.data
    where "Debq" is the first four characters of the file's encryption key
        """
    )
    
    parser.add_argument('input_dir', help='Directory path containing encrypted files')
    parser.add_argument('output_dir', help='Output directory path for decrypted files')
    parser.add_argument('key_file', help='Device key file path')
    parser.add_argument('--error-log', help='Error log file path (optional)')
    
    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        return 1
        
    # Create decryptor instance
    decryptor = DataDecryptor(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        key_file=args.key_file,
        error_log=args.error_log
    )
    
    # Run decryption tool
    try:
        success = decryptor.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Program exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
