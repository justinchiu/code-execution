import datasets
import requests
import time
import json

# Sample C++ solutions for code contest problems
dataset = datasets.load_dataset("deepmind/code_contests", trust_remote_code=True)
train = dataset["train"]

def get_tests(test_dict: dict) -> list[dict]:
    return [dict(stdin=input, stdout=output) for input, output in zip(test_dict["input"], test_dict["output"])]

def get_solutions(problems):
    solutions = []
    for problem in problems:
        for language, solution in zip(problem["solutions"]["language"], problem["solutions"]["solution"]):
            if language == 2:
                tests = get_tests(problem["public_tests"]) + get_tests(problem["private_tests"]) + get_tests(problem["generated_tests"])
                solutions.append(dict(code=solution, language="cpp", stdin_stdout=tests))
                if len(solutions) == 5:
                    return solutions

problems = get_solutions(train)

def run_test(name, test_data):
    print(f"\nRunning test: {name}")
    print("-" * 40)

    start_time = time.time()

    # Send request to the server
    try:
        response = requests.post(
            "http://localhost:8088/execute", json=test_data, timeout=30
        )

        elapsed = time.time() - start_time
        print(f"Response time: {elapsed:.2f} seconds")

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
            return False

        result = response.json()
        import pdb; pdb.set_trace()

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

    for i, test_data in enumerate(problems):
        if run_test(i, test_data):
            total_passed += 1
        else:
            all_passed = False

    print("\nSummary")
    print("=" * 60)
    print(f"Tests passed: {total_passed}/{len(problems)}")

    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️ Some tests failed. Check the results above.")


if __name__ == "__main__":
    main()
