import datasets
import requests
import time
import json
import asyncio
import aiohttp
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
                if len(solutions) == 100:
                    return solutions

problems = get_solutions(train)

# Sequential execution
def run_sequential():
    print("\nRunning sequential tests")
    print("-" * 60)
    
    start_time = time.time()
    total_passed = 0
    
    for i, test_data in enumerate(problems):
        try:
            print(f"Running test {i+1}/{len(problems)}")
            response = requests.post(
                "https://code-execution-936673687579.us-east1.run.app/execute", 
                json=test_data, 
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
            else:
                print(f"  Test {i+1}: Failed with status code {response.status_code}")
                
        except Exception as e:
            print(f"  Test {i+1}: Error - {str(e)}")
    
    elapsed = time.time() - start_time
    print(f"\nSequential execution completed in {elapsed:.2f} seconds")
    print(f"Tests passed: {total_passed}/{len(problems)}")
    
    return elapsed, total_passed

# Parallel execution with aiohttp
async def execute_code_async(session, test_data, index):
    try:
        async with session.post(
            "https://code-execution-936673687579.us-east1.run.app/execute", 
            json=test_data, 
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
            else:
                print(f"  Test {index+1}: Failed with status code {response.status}")
                return False
                
    except Exception as e:
        print(f"  Test {index+1}: Error - {str(e)}")
        return False

async def run_parallel():
    print("\nRunning parallel tests")
    print("-" * 60)
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, test_data in enumerate(problems):
            print(f"Starting test {i+1}/{len(problems)}")
            task = execute_code_async(session, test_data, i)
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
