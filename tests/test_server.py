import requests
import time
import json

# Sample C++ solutions for code contest problems

# Solution 1: A simple "Hello World" to test basic functionality
hello_world = {
    "code": """
    #include <iostream>
    
    int main() {
        std::string name;
        std::getline(std::cin, name);
        std::cout << "Hello, " << name << "!" << std::endl;
        return 0;
    }
    """,
    "stdin_stdout": [
        {"stdin": "World", "stdout": "Hello, World!\n"},
        {"stdin": "CodeContests", "stdout": "Hello, CodeContests!\n"},
    ],
    "language": "cpp",
}

# Solution 2: Sum of two numbers
sum_two_numbers = {
    "code": """
    #include <iostream>
    
    int main() {
        int a, b;
        std::cin >> a >> b;
        std::cout << a + b << std::endl;
        return 0;
    }
    """,
    "stdin_stdout": [
        {"stdin": "5 7", "stdout": "12\n"},
        {"stdin": "10 -3", "stdout": "7\n"},
        {"stdin": "0 0", "stdout": "0\n"},
    ],
    "language": "cpp",
}

# Solution 3: Check if number is prime
prime_check = {
    "code": """
    #include <iostream>
    #include <cmath>
    
    bool is_prime(int n) {
        if (n <= 1)
            return false;
        if (n <= 3)
            return true;
        if (n % 2 == 0 || n % 3 == 0)
            return false;
        for (int i = 5; i * i <= n; i += 6) {
            if (n % i == 0 || n % (i + 2) == 0)
                return false;
        }
        return true;
    }
    
    int main() {
        int n;
        std::cin >> n;
        if (is_prime(n))
            std::cout << "YES" << std::endl;
        else
            std::cout << "NO" << std::endl;
        return 0;
    }
    """,
    "stdin_stdout": [
        {"stdin": "7", "stdout": "YES\n"},
        {"stdin": "15", "stdout": "NO\n"},
        {"stdin": "23", "stdout": "YES\n"},
        {"stdin": "4", "stdout": "NO\n"},
    ],
    "language": "cpp",
}

# Solution 4: Fibonacci sequence
fibonacci = {
    "code": """
    #include <iostream>
    #include <vector>
    
    int main() {
        int n;
        std::cin >> n;
        
        if (n <= 0) {
            std::cout << "0" << std::endl;
            return 0;
        }
        
        std::vector<long long> fib(n + 1);
        fib[0] = 0;
        
        if (n >= 1) {
            fib[1] = 1;
        }
        
        for (int i = 2; i <= n; ++i) {
            fib[i] = fib[i-1] + fib[i-2];
        }
        
        std::cout << fib[n] << std::endl;
        
        return 0;
    }
    """,
    "stdin_stdout": [
        {"stdin": "5", "stdout": "5\n"},
        {"stdin": "10", "stdout": "55\n"},
        {"stdin": "1", "stdout": "1\n"},
        {"stdin": "0", "stdout": "0\n"},
    ],
    "language": "cpp",
}

# Tests list
tests = [
    ("Hello World", hello_world),
    ("Sum Two Numbers", sum_two_numbers),
    ("Prime Check", prime_check),
    ("Fibonacci", fibonacci),
]


def run_test(name, test_data):
    print(f"\nRunning test: {name}")
    print("-" * 40)

    start_time = time.time()

    # Send request to the server
    try:
        response = requests.post(
            "http://localhost:8080/execute", json=test_data, timeout=30
        )

        elapsed = time.time() - start_time
        print(f"Response time: {elapsed:.2f} seconds")

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
            return False

        result = response.json()

        # Print metrics
        print(f"Compilation time: {result['compile_output']['time_seconds']} secs")
        print(f"Execution time: {[x['time_seconds']for x in result['exec_outputs']]} secs")

        # Check test results
        results = result.get("exec_outputs", [])
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get("passed", False))

        print(f"Tests passed: {passed_tests}/{total_tests}")

        for i, (test_result, test_case) in enumerate(zip(results, test_data["stdin_stdout"])):
            status = "✅ Passed" if test_result.get("passed", False) else "❌ Failed"
            print(f"  Test {i + 1}: {status}")
            if not test_result.get("passed", False):
                print(f"    Expected: '{test_case.get('stdout', '')}'")
                print(f"    Actual:   '{test_result.get('stdout', '')}'")

        return passed_tests == total_tests

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    print("Testing code execution server with CodeContests problems")
    print("=" * 60)

    all_passed = True
    total_passed = 0

    for name, test_data in tests:
        if run_test(name, test_data):
            total_passed += 1
        else:
            all_passed = False

    print("\nSummary")
    print("=" * 60)
    print(f"Tests passed: {total_passed}/{len(tests)}")

    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️ Some tests failed. Check the results above.")


if __name__ == "__main__":
    main()
