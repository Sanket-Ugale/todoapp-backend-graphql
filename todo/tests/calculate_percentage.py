import os
import xml.etree.ElementTree as ET

def calculate_pass_percentage(report_dir):
    total_tests = 0
    total_failures = 0

    for report_file in os.listdir(report_dir):
        if report_file.endswith('.xml'):
            tree = ET.parse(os.path.join(report_dir, report_file))
            root = tree.getroot()
            for testcase in root.iter('testcase'):
                total_tests += 1
                if testcase.find('failure') is not None:
                    total_failures += 1

    pass_percentage = ((total_tests - total_failures) / total_tests) * 100 if total_tests > 0 else 0
    return pass_percentage, total_tests, total_failures

if __name__ == "__main__":
    report_dir = 'test-reports'
    pass_percentage, total_tests, total_failures = calculate_pass_percentage(report_dir)
    
    print(f'Total Tests: {total_tests}')
    print(f'Failures: {total_failures}')
    print(f'Pass Percentage: {pass_percentage:.2f}%')
