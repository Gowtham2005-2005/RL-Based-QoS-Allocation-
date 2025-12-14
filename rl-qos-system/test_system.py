#!/usr/bin/env python3
"""
System Test Script
Verifies all components are working before training
"""

import sys
import os


def test_python_version():
    """Check Python version"""
    print("Testing Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (need 3.8+)")
        return False


def test_imports():
    """Test required packages"""
    packages = {
        'torch': 'PyTorch (Deep Learning)',
        'numpy': 'NumPy (Numerical Computing)',
        'pandas': 'Pandas (Data Processing)',
        'matplotlib': 'Matplotlib (Plotting)',
        'yaml': 'PyYAML (Configuration)',
        'tqdm': 'tqdm (Progress Bars)'
    }
    
    all_ok = True
    
    for package, description in packages.items():
        print(f"Testing {description}...", end=" ")
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print("✓")
        except ImportError:
            print(f"✗ (run: pip install {package})")
            all_ok = False
    
    return all_ok


def test_project_structure():
    """Check project structure"""
    print("\nTesting project structure...", end=" ")
    
    required_files = [
        'config/rl_config.yaml',
        'config/network_config.yaml',
        'config/qos_policies.yaml',
        'src/rl_agent/ddqn_agent.py',
        'src/environment/network_env.py',
        'src/training/train.py',
        'demo_windows.py'
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"✗ Missing files:")
        for f in missing:
            print(f"  - {f}")
        return False
    else:
        print("✓ All files present")
        return True


def test_agent_import():
    """Test DDQN agent"""
    print("Testing DDQN agent import...", end=" ")
    
    try:
        sys.path.append('.')
        from src.rl_agent.ddqn_agent import DDQNAgent
        print("✓")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_environment():
    """Test network environment"""
    print("Testing network environment...", end=" ")
    
    try:
        from src.environment.network_env import NetworkEnvironment
        env = NetworkEnvironment()
        state = env.reset()
        
        # Test one step
        action = 0
        next_state, reward, done = env.step(action)
        
        print("✓")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_agent_creation():
    """Test agent creation"""
    print("Testing agent creation...", end=" ")
    
    try:
        from src.rl_agent.ddqn_agent import DDQNAgent
        agent = DDQNAgent(config_path='config/rl_config.yaml')
        
        # Test action selection
        import numpy as np
        state = np.random.rand(8)
        action = agent.select_action(state, epsilon=0.0)
        
        print("✓")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_directories():
    """Create necessary directories"""
    print("Creating data directories...", end=" ")
    
    dirs = [
        'data/models',
        'data/training_logs',
        'data/network_traces'
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print("✓")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RL-QoS System - System Test")
    print("=" * 60 + "\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Required Packages", test_imports),
        ("Project Structure", test_project_structure),
        ("Agent Import", test_agent_import),
        ("Environment", test_environment),
        ("Agent Creation", test_agent_creation),
        ("Data Directories", test_directories)
    ]
    
    results = []
    
    print("Running tests...\n")
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} - {name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All systems ready!")
        print("\nNext steps:")
        print("  1. Run: python demo_windows.py")
        print("  2. Select option 1 to start training")
        print("  3. Wait 30-60 minutes for training")
        print("  4. Test your trained agent!")
        return 0
    else:
        print("\n✗ Some tests failed!")
        print("\nFix the errors above, then run this test again.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
