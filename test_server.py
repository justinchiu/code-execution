import requests
import json
import time

def test_cpp_execution():
    # Sample C++ code that reads input and outputs it
    code = """
    #include <iostream>
    #include <string>
    
    int main() {
        std::string input;
        std::getline(std::cin, input);
        std::cout << "Hello, " << input << "!" << std::endl;
        return 0;
    }
    """
    
    # Test data
    test_data = {
        "code": code,
        "stdin_stdout": [
            {"stdin": "World", "stdout": "Hello, World!"},
            {"stdin": "FastAPI", "stdout": "Hello, FastAPI!"}
        ],
        "language": "cpp"
    }
    
    # Send request to the server
    response = requests.post(
        "http://localhost:8080/execute",
        json=test_data
    )
    
    # Print the response
    print(f"Status code: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Check test results
    results = response.json().get("results", [])
    all_passed = all(result.get("passed", False) for result in results)
    print(f"\nAll tests passed: {all_passed}")
    
    # Print metrics
    metrics = response.json().get("metrics", {})
    print(f"Compilation time: {metrics.get('compilation_time_ms', 0):.2f} ms")
    print(f"Execution time: {metrics.get('execution_time_ms', 0):.2f} ms")

if __name__ == "__main__":
    # Wait a bit for the server to start if needed
    print("Testing C++ code execution...")
    test_cpp_execution()