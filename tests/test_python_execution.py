import requests

BASE_URL = "http://localhost:8088"

# Test cases for Python execution
def test_hello_world_python():
    """Test a simple hello world program in Python"""
    payload = {
        "code": """
name = input()
print(f"Hello, {name}!")
        """,
        "stdin_stdout": [
            {"stdin": "World", "stdout": "Hello, World!"},
            {"stdin": "CodeContests", "stdout": "Hello, CodeContests!"},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"]
    assert len(data["exec_outputs"]) == 2
    for output in data["exec_outputs"]:
        assert output["passed"]

def test_sum_two_numbers_python():
    """Test addition of two numbers in Python"""
    payload = {
        "code": """
a, b = map(int, input().split())
print(a + b)
        """,
        "stdin_stdout": [
            {"stdin": "5 7", "stdout": "12"},
            {"stdin": "10 -3", "stdout": "7"},
            {"stdin": "0 0", "stdout": "0"},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"]
    assert len(data["exec_outputs"]) == 3
    for output in data["exec_outputs"]:
        assert output["passed"]

def test_prime_check_python():
    """Test prime number checker in Python"""
    payload = {
        "code": """
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

n = int(input())
if is_prime(n):
    print("YES")
else:
    print("NO")
        """,
        "stdin_stdout": [
            {"stdin": "7", "stdout": "YES"},
            {"stdin": "15", "stdout": "NO"},
            {"stdin": "23", "stdout": "YES"},
            {"stdin": "4", "stdout": "NO"},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"]
    assert len(data["exec_outputs"]) == 4
    for output in data["exec_outputs"]:
        assert output["passed"]

def test_fibonacci_python():
    """Test Fibonacci sequence calculation in Python"""
    payload = {
        "code": """
n = int(input())

if n <= 0:
    print("0")
else:
    fib = [0] * (n + 1)
    fib[0] = 0
    
    if n >= 1:
        fib[1] = 1
    
    for i in range(2, n + 1):
        fib[i] = fib[i-1] + fib[i-2]
    
    print(fib[n])
        """,
        "stdin_stdout": [
            {"stdin": "5", "stdout": "5"},
            {"stdin": "10", "stdout": "55"},
            {"stdin": "1", "stdout": "1"},
            {"stdin": "0", "stdout": "0"},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"]
    assert len(data["exec_outputs"]) == 4
    for output in data["exec_outputs"]:
        assert output["passed"]

def test_syntax_error_python():
    """Test handling of Python syntax errors"""
    payload = {
        "code": """
print("Missing closing parenthesis"
        """,
        "stdin_stdout": [
            {"stdin": "", "stdout": ""},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert not data["all_passed"]
    assert not data["compile_output"]["passed"]
    assert "SyntaxError" in data["compile_output"]["stderr"]

def test_timeout_python():
    """Test handling of infinite loops in Python"""
    payload = {
        "code": """
while True:
    pass  # Infinite loop
        """,
        "stdin_stdout": [
            {"stdin": "", "stdout": ""},
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert not data["all_passed"]
    assert data["exec_outputs"][0]["timed_out"]

def test_complex_data_structures_python():
    """Test Python code working with complex data structures"""
    payload = {
        "code": """
import json

# Parse JSON input
data = json.loads(input())
# Process data
result = {
    "sum": sum(data["numbers"]),
    "product": 1,
    "has_negative": False
}

for num in data["numbers"]:
    result["product"] *= num
    if num < 0:
        result["has_negative"] = True

# Output JSON result
print(json.dumps(result))
        """,
        "stdin_stdout": [
            {
                "stdin": '{"numbers": [1, 2, 3, 4, 5]}',
                "stdout": '{"sum": 15, "product": 120, "has_negative": false}'
            },
            {
                "stdin": '{"numbers": [-1, 2, -3, 4]}',
                "stdout": '{"sum": 2, "product": 24, "has_negative": true}'
            }
        ],
        "language": "python",
    }
    response = requests.post(f"{BASE_URL}/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["all_passed"]
    assert len(data["exec_outputs"]) == 2
    for output in data["exec_outputs"]:
        assert output["passed"]