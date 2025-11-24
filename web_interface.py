"""
Web Interface for Testing Agent

A Flask-based web interface with buttons to interact with the testing agent.
"""

from flask import Flask, render_template, jsonify, request, send_file
import subprocess
import os
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from src.agent import TestingAgent
from src.training_service import TrainingService

app = Flask(__name__)

# Global testing agent instance
agent = TestingAgent()

# Global training service instance
training_service = TrainingService()


@app.route('/')
def index():
    """Main page with buttons."""
    return render_template('index.html')


@app.route('/training')
def training_page():
    """Training plan page with nomination features."""
    return render_template('training.html')


@app.route('/run-tests', methods=['POST'])
def run_tests():
    """Run all tests and return results."""
    try:
        result = agent.run_tests()

        return jsonify({
            'success': True,
            'passed': result.passed,
            'failed': result.failed,
            'skipped': result.skipped,
            'errors': result.errors,
            'total': result.total,
            'duration': result.duration,
            'coverage': result.coverage,
            'success_rate': result.success_rate(),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'failures': result.failures
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/run-tests-from-url', methods=['POST'])
def run_tests_from_url():
    """Run tests from a URL or repository against the current project."""
    try:
        data = request.json
        test_suite_url = data.get('test_suite_url')
        test_type = data.get('test_type', 'local')
        test_pattern = data.get('test_pattern')

        if not test_suite_url:
            return jsonify({
                'success': False,
                'error': 'Test suite URL is required'
            }), 400

        # Handle different source types
        test_source_path = None
        cleanup_needed = False
        temp_test_dir = None

        if test_type == 'local':
            # Use local path directly
            test_source_path = test_suite_url
            if not Path(test_source_path).exists():
                return jsonify({
                    'success': False,
                    'error': f'Local path not found: {test_source_path}'
                }), 404

        elif test_type in ['github', 'git']:
            # Clone the repository to a temporary directory
            temp_dir = tempfile.mkdtemp(prefix='test_suite_')
            cleanup_needed = True

            try:
                # Convert GitHub URL to git URL if needed
                git_url = test_suite_url
                if test_type == 'github' and 'github.com' in test_suite_url:
                    if not test_suite_url.endswith('.git'):
                        # Convert https://github.com/user/repo to git URL
                        if '/tree/' in test_suite_url:
                            # Handle branch URLs
                            git_url = test_suite_url.split('/tree/')[0] + '.git'
                        else:
                            git_url = test_suite_url.rstrip('/') + '.git'

                print(f"Cloning test suite from {git_url} to {temp_dir}")

                # Clone the repository
                result = subprocess.run(
                    ['git', 'clone', '--depth', '1', git_url, temp_dir],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                if result.returncode != 0:
                    return jsonify({
                        'success': False,
                        'error': f'Failed to clone repository: {result.stderr}'
                    }), 500

                test_source_path = temp_dir

            except subprocess.TimeoutExpired:
                if cleanup_needed and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                return jsonify({
                    'success': False,
                    'error': 'Repository clone timed out (5 minutes)'
                }), 500
            except Exception as e:
                if cleanup_needed and Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                return jsonify({
                    'success': False,
                    'error': f'Error cloning repository: {str(e)}'
                }), 500

        # Now we have test_source_path pointing to the test suite
        # Copy those tests to a temporary location in current project to run them
        try:
            # Create a temporary test directory in the current project
            project_temp_test_dir = Path('tests_external_temp')
            project_temp_test_dir.mkdir(exist_ok=True)
            temp_test_dir = project_temp_test_dir

            # Find test files in the source
            source_path = Path(test_source_path)
            test_files = []

            # Look for test files
            if source_path.is_file():
                if 'test' in source_path.name:
                    test_files = [source_path]
            else:
                # Search for test directories and files
                for pattern_to_search in ['**/test*.py', '**/*test.py', '**/tests/**/*.py']:
                    test_files.extend(source_path.glob(pattern_to_search))

            if not test_files:
                return jsonify({
                    'success': False,
                    'error': 'No test files found in the provided test suite'
                }), 404

            # Copy test files to temporary directory
            copied_files = []
            for test_file in test_files:
                if test_pattern and not Path(test_file).match(test_pattern):
                    continue

                # Copy file maintaining structure
                dest_file = project_temp_test_dir / test_file.name
                shutil.copy2(test_file, dest_file)
                copied_files.append(dest_file)
                print(f"Copied test file: {test_file.name}")

            if not copied_files:
                return jsonify({
                    'success': False,
                    'error': f'No test files matched the pattern: {test_pattern}'
                }), 404

            print(f"Copied {len(copied_files)} test files to {project_temp_test_dir}")

            # Run tests from the temporary directory in current project context
            result = agent.run_tests(
                path=str(project_temp_test_dir),
                pattern=test_pattern
            )

            response_data = {
                'success': True,
                'passed': result.passed,
                'failed': result.failed,
                'skipped': result.skipped,
                'errors': result.errors,
                'total': result.total,
                'duration': result.duration,
                'coverage': result.coverage,
                'success_rate': result.success_rate(),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'failures': result.failures,
                'test_files_count': len(copied_files)
            }

            return jsonify(response_data)

        finally:
            # Clean up temporary test directory in current project
            if temp_test_dir and temp_test_dir.exists():
                try:
                    shutil.rmtree(temp_test_dir)
                    print(f"Cleaned up temporary test directory: {temp_test_dir}")
                except Exception as e:
                    print(f"Warning: Failed to clean up {temp_test_dir}: {e}")

            # Clean up cloned repository
            if cleanup_needed and test_source_path and Path(test_source_path).exists():
                try:
                    shutil.rmtree(test_source_path)
                    print(f"Cleaned up cloned repository: {test_source_path}")
                except Exception as e:
                    print(f"Warning: Failed to clean up {test_source_path}: {e}")

    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/learn-from-tests', methods=['POST'])
def learn_from_tests():
    """Learn patterns from existing passing tests."""
    try:
        stats = agent.learn_from_passing_tests()

        return jsonify({
            'success': True,
            'stats': stats,
            'message': f"Learned from {stats['total_patterns']} existing tests"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/generate-tests', methods=['POST'])
def generate_tests():
    """Generate test suggestions."""
    try:
        learn = request.json.get('learn', True) if request.json else True

        suggestions = agent.generate_test_suggestions(
            save_to_file=True,
            output_file='web_test_suggestions.md',
            learn_from_existing=learn
        )

        return jsonify({
            'success': True,
            'count': len(suggestions),
            'message': f"Generated {len(suggestions)} test suggestions",
            'file': 'web_test_suggestions.md'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analyze-gaps', methods=['POST'])
def analyze_gaps():
    """Analyze test coverage gaps."""
    try:
        gaps = agent.analyze_coverage_gaps()

        return jsonify({
            'success': True,
            'gaps': gaps,
            'message': f"Found {len(gaps)} functions without tests"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get-report/<report_type>')
def get_report(report_type):
    """Get generated report file."""
    try:
        if report_type == 'html':
            report_path = Path('reports/latest_report.html')
        elif report_type == 'json':
            report_path = Path('reports/latest_report.json')
        elif report_type == 'suggestions':
            report_path = Path('web_test_suggestions.md')
        else:
            return jsonify({'success': False, 'error': 'Invalid report type'}), 400

        if report_path.exists():
            return send_file(report_path, as_attachment=False)
        else:
            return jsonify({'success': False, 'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/write-and-run-tests', methods=['POST'])
def write_and_run_tests():
    """Generate tests, write them to a file, and run them."""
    try:
        # Step 1: Generate test suggestions
        print("Generating test suggestions...")
        suggestions = agent.generate_test_suggestions(
            save_to_file=True,
            output_file='web_test_suggestions.md',
            learn_from_existing=True
        )

        if not suggestions:
            return jsonify({
                'success': False,
                'error': 'No test suggestions generated'
            }), 400

        # Step 2: Write to test file
        print("Writing tests to file...")
        test_file = agent.write_generated_tests_to_file(
            suggestions,
            output_file='tests/test_generated.py'
        )

        # Step 3: Run the generated tests
        print("Running generated tests...")
        result = agent.run_generated_tests(test_file)

        return jsonify({
            'success': True,
            'suggestions_count': len(suggestions),
            'tests_written': min(20, len(suggestions)),  # Limit to 20 tests
            'test_file': test_file,
            'test_results': {
                'passed': result.passed,
                'failed': result.failed,
                'skipped': result.skipped,
                'errors': result.errors,
                'total': result.total,
                'duration': result.duration,
                'success_rate': result.success_rate(),
                'stdout': result.stdout,
                'stderr': result.stderr
            },
            'message': f"Generated {len(suggestions)} suggestions, wrote {min(20, len(suggestions))} tests, and executed them"
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/run-generated-tests', methods=['POST'])
def run_generated_tests():
    """Run the previously generated test file."""
    try:
        test_file = 'tests/test_generated.py'

        if not Path(test_file).exists():
            return jsonify({
                'success': False,
                'error': 'No generated test file found. Please generate tests first.'
            }), 404

        result = agent.run_generated_tests(test_file)

        return jsonify({
            'success': True,
            'test_file': test_file,
            'passed': result.passed,
            'failed': result.failed,
            'skipped': result.skipped,
            'errors': result.errors,
            'total': result.total,
            'duration': result.duration,
            'success_rate': result.success_rate(),
            'stdout': result.stdout,
            'stderr': result.stderr,
            'message': f"Executed generated tests: {result.passed}/{result.total} passed"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status')
def status():
    """Get current status of the testing agent."""
    try:
        # Get basic stats
        stats = {
            'test_framework': agent.config.test_framework,
            'test_directory': agent.config.test_directory,
            'coverage_threshold': agent.config.coverage_threshold,
            'reports_exist': Path('reports').exists(),
            'generated_tests_exist': Path('tests/test_generated.py').exists(),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Training Plan and Nomination Routes

@app.route('/training-plans')
def get_training_plans():
    """Get all training plans with their areas of work."""
    try:
        plans = training_service.get_all_training_plans()
        return jsonify({
            'success': True,
            'plans': [plan.to_dict() for plan in plans]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/training-plans/<plan_id>')
def get_training_plan(plan_id):
    """Get a specific training plan."""
    try:
        plan = training_service.get_training_plan(plan_id)
        if not plan:
            return jsonify({
                'success': False,
                'error': f'Training plan not found: {plan_id}'
            }), 404
        return jsonify({
            'success': True,
            'plan': plan.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/employees')
def get_employees():
    """Get all employees for nomination dropdown."""
    try:
        employees = training_service.get_all_employees()
        return jsonify({
            'success': True,
            'employees': [emp.to_dict() for emp in employees]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/nominate', methods=['POST'])
def nominate_employee():
    """Nominate an employee for training and send email notification."""
    try:
        data = request.json

        training_plan_id = data.get('training_plan_id')
        aow_id = data.get('aow_id')
        employee_id = data.get('employee_id')
        nominated_by = data.get('nominated_by', 'HR Admin')
        priority = data.get('priority', 'medium')
        notes = data.get('notes', '')

        if not all([training_plan_id, aow_id, employee_id]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: training_plan_id, aow_id, employee_id'
            }), 400

        result = training_service.nominate_employee(
            training_plan_id=training_plan_id,
            aow_id=aow_id,
            employee_id=employee_id,
            nominated_by=nominated_by,
            priority=priority,
            notes=notes
        )

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/nominations')
def get_nominations():
    """Get all nominations."""
    try:
        nominations = training_service.get_all_nominations()

        # Enrich with employee and training info
        enriched = []
        for nom in nominations:
            emp = training_service.get_employee(nom.employee_id)
            plan = training_service.get_training_plan(nom.training_plan_id)
            aow = training_service.get_aow(nom.training_plan_id, nom.aow_id)

            nom_dict = nom.to_dict()
            nom_dict['employee_name'] = emp.name if emp else 'Unknown'
            nom_dict['training_plan_name'] = plan.name if plan else 'Unknown'
            nom_dict['aow_name'] = aow.name if aow else 'Unknown'
            enriched.append(nom_dict)

        return jsonify({
            'success': True,
            'nominations': enriched
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/nominations/<nomination_id>/status', methods=['PUT'])
def update_nomination_status(nomination_id):
    """Update nomination status."""
    try:
        data = request.json
        status = data.get('status')

        if not status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400

        result = training_service.update_nomination_status(nomination_id, status)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/training-summary')
def get_training_summary():
    """Get summary of training nominations."""
    try:
        summary = training_service.get_training_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    Path('reports').mkdir(exist_ok=True)

    print("=" * 70)
    print("Testing Agent Web Interface")
    print("=" * 70)
    print("\nAccess the web interface at: http://localhost:5000")
    print("\nAvailable Pages:")
    print("   - Home (/) - Testing Agent dashboard")
    print("   - Training (/training) - Training Plan Management")
    print("\nTesting Features:")
    print("   - Run Tests - Execute all tests and see results")
    print("   - Learn from Tests - Analyze existing passing tests")
    print("   - Generate Tests - Create new test suggestions")
    print("   - Analyze Coverage Gaps - Find untested code")
    print("   - Run Generated Tests - Execute generated test cases")
    print("\nTraining Features:")
    print("   - View Training Plans with Areas of Work")
    print("   - Nominate Employees for Training")
    print("   - Send Email Notifications")
    print("   - Track Nomination Status")
    print("\n" + "=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
