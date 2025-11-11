"""
Web Interface for Testing Agent

A Flask-based web interface with buttons to interact with the testing agent.
"""

from flask import Flask, render_template, jsonify, request, send_file
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime
from src.agent import TestingAgent

app = Flask(__name__)

# Global testing agent instance
agent = TestingAgent()


@app.route('/')
def index():
    """Main page with buttons."""
    return render_template('index.html')


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


if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    Path('reports').mkdir(exist_ok=True)

    print("=" * 70)
    print("🚀 Testing Agent Web Interface")
    print("=" * 70)
    print("\n📍 Access the web interface at: http://localhost:5000")
    print("\n🔘 Available buttons:")
    print("   • Run Tests - Execute all tests and see results")
    print("   • Learn from Tests - Analyze existing passing tests")
    print("   • Generate Tests - Create new test suggestions")
    print("   • Analyze Coverage Gaps - Find untested code")
    print("\n" + "=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
