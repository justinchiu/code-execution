import datasets
import requests
import time
import json
import asyncio
import aiohttp
import google.auth
import google.auth.transport.requests
from typing import List, Dict, Any

# Load the same CodeContests dataset
dataset = datasets.load_dataset("deepmind/code_contests", trust_remote_code=True)
train = dataset["test"]

def get_tests(test_dict: dict) -> list[dict]:
    return [dict(stdin=input, stdout=output) for input, output in zip(test_dict["input"], test_dict["output"])]

def get_solutions(problems):
    solutions = []
    for problem in problems:
        for language, solution in zip(problem["solutions"]["language"], problem["solutions"]["solution"]):
            if language == 2:  # C++ solutions
                tests = get_tests(problem["public_tests"]) + get_tests(problem["private_tests"]) + get_tests(problem["generated_tests"])
                solutions.append(dict(code=solution, language="cpp", stdin_stdout=tests))
                if len(solutions) == 10:
                    return solutions

problems = get_solutions(train)

# Function to get identity token for Cloud Run authentication
def get_id_token_for_cloud_run():
    from google.cloud import run_v2
    from google.oauth2 import service_account
    import os
    
    # First try to authenticate using Application Default Credentials
    try:
        from google.auth.transport.requests import Request
        from google.oauth2 import id_token
        
        # The audience is the URL of your Cloud Run service without path
        audience = "https://code-execution-936673687579.us-east1.run.app"
        
        # Try to get a token using Application Default Credentials
        token = id_token.fetch_id_token(Request(), audience)
        print("Successfully authenticated using application default credentials")
        return token
    except Exception as e:
        print(f"Application default credentials failed: {str(e)}")
        
    # If that fails, check if there's a service account file specified
    service_account_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_file and os.path.exists(service_account_file):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            return credentials.id_token
        except Exception as e:
            print(f"Service account authentication failed: {str(e)}")
    
    # Try interactive authentication as a last resort
    print("Could not authenticate automatically. Please run 'gcloud auth application-default login' manually.")
    return None

# The audience is the URL of your Cloud Run service
CLOUD_RUN_URL = "https://code-execution-936673687579.us-east1.run.app/execute"

# Try different authentication approaches
auth_headers = {}

# 1. Try to get an authentication token
try:
    id_token = get_id_token_for_cloud_run()
    if id_token:
        auth_headers["Authorization"] = f"Bearer {id_token}"
        print("Added Bearer token to headers")
except Exception as e:
    print(f"Bearer token authentication error: {str(e)}")

# 2. Add various custom headers that might be required
# Common API key header names
auth_headers["X-API-Key"] = "some-api-key-placeholder"  # Replace with actual API key if available
auth_headers["api-key"] = "some-api-key-placeholder"  # Another common format
auth_headers["x-functions-key"] = "some-api-key-placeholder"  # Azure format
auth_headers["x-goog-api-key"] = "some-api-key-placeholder"  # Google format

# Add CORS headers
auth_headers["Origin"] = "https://code-execution-936673687579.us-east1.run.app"
auth_headers["Access-Control-Request-Method"] = "POST"

print("Added custom authentication headers")

# 3. Try with no authentication
print("Authentication headers prepared:", auth_headers)

# 4. Let's also try with a different method - URL parameter for API key
CLOUD_RUN_URL_WITH_KEY = f"{CLOUD_RUN_URL}?key=some-api-key-placeholder"  # Replace with actual API key if available

# Sequential execution
def run_sequential():
    print("\nRunning sequential tests")
    print("-" * 60)
    
    start_time = time.time()
    total_passed = 0
    
    # First try a simplified test to check connectivity and authentication
    print("Trying initial connectivity test...")
    try:
        # Just a simple health check first with minimal payload
        simple_test = {"code": "int main() { return 0; }", "language": "cpp", "stdin_stdout": [{"stdin": "", "stdout": ""}]}
        print("Testing with regular URL and auth headers")
        response = requests.post(
            CLOUD_RUN_URL, 
            json=simple_test, 
            headers=auth_headers,
            timeout=30
        )
        print(f"Initial test response: Status {response.status_code}")
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            
            # Try alternative URL with key in querystring
            print("Testing with URL key parameter")
            response = requests.post(
                CLOUD_RUN_URL_WITH_KEY, 
                json=simple_test, 
                headers={},  # No auth headers here, using key in URL
                timeout=30
            )
            print(f"Alternative URL test response: Status {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Initial connectivity test failed: {str(e)}")
    
    # Determine which URL to use based on the initial test
    use_url_with_key = False  # Set this to True if the URL with key works better
    
    for i, test_data in enumerate(problems):
        try:
            print(f"Running test {i+1}/{len(problems)}")
            
            # Use either the regular URL with auth headers or the URL with key parameter
            if use_url_with_key:
                response = requests.post(
                    CLOUD_RUN_URL_WITH_KEY, 
                    json=test_data, 
                    headers={},  # No auth headers
                    timeout=300
                )
            else:
                response = requests.post(
                    CLOUD_RUN_URL, 
                    json=test_data, 
                    headers=auth_headers,
                    timeout=300
                )
            
            if response.status_code == 200:
                result = response.json()
                passed_tests = sum(1 for r in result.get("exec_outputs", []) if r.get("passed", False))
                total_tests = len(result.get("exec_outputs", []))
                compile_time = result.get("compile_output", {}).get("time_seconds", 0)
                execution_times = [output.get("time_seconds", 0) for output in result.get("exec_outputs", [])]
                total_exec_time = sum(execution_times)
                print(f"  Test {i+1}: Passed {passed_tests}/{total_tests} test cases, Compile: {compile_time:.3f}s, Execution: {total_exec_time:.3f}s")
                
                if passed_tests == total_tests:
                    total_passed += 1
            elif response.status_code == 403:
                print(f"  Test {i+1}: Failed with status code 403 - Forbidden. This might indicate authentication issues.")
                try:
                    error_content = response.text
                    print(f"  Error response: {error_content}")
                    print(f"  Request headers: {response.request.headers}")
                except Exception as e:
                    print(f"  Error retrieving response details: {str(e)}")
            else:
                print(f"  Test {i+1}: Failed with status code {response.status_code}")
                try:
                    error_content = response.text
                    print(f"  Error response: {error_content[:200]}...")
                except:
                    pass
                
        except Exception as e:
            print(f"  Test {i+1}: Error - {str(e)}")
    
    elapsed = time.time() - start_time
    print(f"\nSequential execution completed in {elapsed:.2f} seconds")
    print(f"Tests passed: {total_passed}/{len(problems)}")
    
    return elapsed, total_passed

# Parallel execution with aiohttp
async def execute_code_async(session, test_data, index, use_url_with_key=False):
    try:
        # Use either the regular URL with auth headers or the URL with key parameter
        if use_url_with_key:
            url = CLOUD_RUN_URL_WITH_KEY
            headers = {}  # No auth headers when using key in URL
        else:
            url = CLOUD_RUN_URL
            headers = auth_headers
            
        async with session.post(
            url, 
            json=test_data, 
            headers=headers,
            timeout=300
        ) as response:
            
            if response.status == 200:
                result = await response.json()
                passed_tests = sum(1 for r in result.get("exec_outputs", []) if r.get("passed", False))
                total_tests = len(result.get("exec_outputs", []))
                compile_time = result.get("compile_output", {}).get("time_seconds", 0)
                execution_times = [output.get("time_seconds", 0) for output in result.get("exec_outputs", [])]
                total_exec_time = sum(execution_times)
                print(f"  Test {index+1}: Passed {passed_tests}/{total_tests} test cases, Compile: {compile_time:.3f}s, Execution: {total_exec_time:.3f}s")
                
                return passed_tests == total_tests
            elif response.status == 403:
                print(f"  Test {index+1}: Failed with status code 403 - Forbidden. This might indicate authentication issues.")
                try:
                    error_content = await response.text()
                    print(f"  Error response: {error_content[:200]}...")
                except:
                    pass
                return False
            else:
                print(f"  Test {index+1}: Failed with status code {response.status}")
                try:
                    error_content = await response.text()
                    print(f"  Error response: {error_content[:200]}...")
                except:
                    pass
                return False
                
    except Exception as e:
        print(f"  Test {index+1}: Error - {str(e)}")
        return False

async def run_parallel():
    print("\nRunning parallel tests")
    print("-" * 60)
    
    start_time = time.time()
    
    # First try a simplified test to check connectivity and authentication
    print("Trying initial connectivity test for parallel execution...")
    use_url_with_key = False
    
    try:
        simple_test = {"code": "int main() { return 0; }", "language": "cpp", "stdin_stdout": [{"stdin": "", "stdout": ""}]}
        async with aiohttp.ClientSession() as session:
            # Test with regular URL first
            async with session.post(
                CLOUD_RUN_URL, 
                json=simple_test, 
                headers=auth_headers,
                timeout=30
            ) as response:
                print(f"Initial parallel test response: Status {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error response: {error_text}")
                    
                    # Try with URL key parameter
                    async with session.post(
                        CLOUD_RUN_URL_WITH_KEY, 
                        json=simple_test, 
                        headers={},
                        timeout=30
                    ) as alt_response:
                        print(f"Alternative URL test response: Status {alt_response.status}")
                        if alt_response.status == 200:
                            use_url_with_key = True
                            print("Using URL with key for parallel tests")
                        else:
                            error_text = await alt_response.text()
                            print(f"Error response: {error_text}")
    except Exception as e:
        print(f"Initial parallel connectivity test failed: {str(e)}")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, test_data in enumerate(problems):
            print(f"Starting test {i+1}/{len(problems)}")
            task = execute_code_async(session, test_data, i, use_url_with_key)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    total_passed = sum(1 for r in results if r)
    
    print(f"\nParallel execution completed in {elapsed:.2f} seconds")
    print(f"Tests passed: {total_passed}/{len(problems)}")
    
    return elapsed, total_passed

async def main():
    print("Comparing sequential vs parallel execution performance")
    print("=" * 80)
    
    # Run sequential tests
    seq_time, seq_passed = run_sequential()
    
    # Run parallel tests
    parallel_time, parallel_passed = await run_parallel()
    
    # Print summary
    print("\nPerformance Comparison")
    print("=" * 80)
    print(f"Sequential execution: {seq_time:.2f} seconds, {seq_passed}/{len(problems)} tests passed")
    print(f"Parallel execution:   {parallel_time:.2f} seconds, {parallel_passed}/{len(problems)} tests passed")
    
    speedup = seq_time / parallel_time if parallel_time > 0 else float('inf')
    print(f"Speedup factor: {speedup:.2f}x")

if __name__ == "__main__":
    asyncio.run(main())
