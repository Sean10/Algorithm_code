def test_import():
    try:
        from object_distribution.simulators import (
            HashSimulator,
            DHTSimulator,
            DynamoSimulator,
            TieredCopysetSimulator,
            CrushSimulator
        )
        print("Import successful!")
        return True
    except ImportError as e:
        print(f"Import failed: {e}")
        return False

def test_cli():
    import subprocess
    try:
        result = subprocess.run(
            ['python', '-m', 'object_distribution.cli', '--num-objects', '1000', '--num-nodes', '10'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("CLI execution successful!")
            return True
        else:
            print(f"CLI execution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"CLI execution failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing installation...")
    test_import()
    test_cli() 