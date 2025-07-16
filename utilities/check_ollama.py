#!/usr/bin/env python3
"""
Check Ollama setup and available models
"""

import requests
import json

def check_ollama():
    """Check Ollama setup and available models"""
    
    print("🔍 Checking Ollama Setup...")
    print("=" * 50)
    
    try:
        # Check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama is running!")
            
            # Get available models
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"\n📋 Available Models ({len(models)}):")
                print("-" * 30)
                
                for i, model in enumerate(models, 1):
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    modified = model.get('modified_at', 'Unknown')
                    
                    # Convert size to human readable format
                    if size > 1024**3:
                        size_str = f"{size / (1024**3):.1f} GB"
                    elif size > 1024**2:
                        size_str = f"{size / (1024**2):.1f} MB"
                    else:
                        size_str = f"{size} bytes"
                    
                    print(f"{i}. {name}")
                    print(f"   Size: {size_str}")
                    print(f"   Modified: {modified[:19] if modified != 'Unknown' else 'Unknown'}")
                    print()
                
                # Check for recommended model
                model_names = [model['name'] for model in models]
                recommended_models = ['gemma3:4b', 'llama3.2:3b', 'llama3.1:8b']
                
                print("🎯 Recommended Models for Summarization:")
                print("-" * 40)
                
                for rec_model in recommended_models:
                    if rec_model in model_names:
                        print(f"✅ {rec_model} - Available")
                    else:
                        print(f"❌ {rec_model} - Not installed")
                        print(f"   Install with: ollama pull {rec_model}")
                
                # Test model if available
                test_model = None
                for rec_model in recommended_models:
                    if rec_model in model_names:
                        test_model = rec_model
                        break
                
                if test_model:
                    print(f"\n🧪 Testing {test_model}...")
                    print("-" * 30)
                    
                    test_prompt = "Summarize this in one sentence: The weather is sunny today and people are enjoying outdoor activities."
                    
                    payload = {
                        "model": test_model,
                        "prompt": test_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "num_predict": 50
                        }
                    }
                    
                    try:
                        test_response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
                        
                        if test_response.status_code == 200:
                            result = test_response.json()
                            summary = result.get('response', '').strip()
                            
                            if summary:
                                print(f"✅ Model test successful!")
                                print(f"Test summary: {summary}")
                            else:
                                print("❌ Model test failed - empty response")
                        else:
                            print(f"❌ Model test failed - HTTP {test_response.status_code}")
                    
                    except Exception as e:
                        print(f"❌ Model test failed: {e}")
                
            else:
                print("❌ No models found!")
                print("\nTo install a model, run:")
                print("ollama pull gemma3:4b")
        
        else:
            print(f"❌ Ollama responded with status code: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama!")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is installed")
        print("2. Start Ollama service")
        print("3. Check if it's running on http://localhost:11434")
    
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
    
    print("\n" + "=" * 50)
    print("Ollama check completed!")

if __name__ == "__main__":
    check_ollama()