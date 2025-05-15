import os
import subprocess
import time

print("\n==== Kentucky Driver's Manual Test Bank Generator (with Enhanced Auto-Fix) ====\n")

# Step 1: Run the standard generator 
print("Step 1: Generating questions using simple_generator.py...\n")
start_time = time.time()
subprocess.run(["python", "simple_generator.py", "--num_questions", "450"])

# Step 2: Run the enhanced fix script to improve question quality
print("\nStep 2: Fixing questions with enhanced algorithm...\n")
subprocess.run(["python", "enhanced_fix_questions.py", "--input", "output/test_bank.json", "--output", "output/enhanced_test_bank.json"])

# Step 3: Run QC on the enhanced fixed questions
print("\nStep 3: Running quality control on enhanced fixed questions...\n")
enhanced_path = os.path.join("output", "enhanced_test_bank.json")
subprocess.run(["python", "question_qc.py", "--input", enhanced_path, "--output", enhanced_path])

end_time = time.time()
total_time = end_time - start_time
print(f"\nAll steps completed in {total_time:.1f} seconds!")
print("\nFinal output files:")
print("- output/test_bank.json (raw generated questions)")
print("- output/enhanced_test_bank.json (questions with banned phrases properly rewritten)")
print("- output/qc_report.json (quality control report)")
print("- output/coverage_report.json (section coverage report)")
print("- output/stats.txt (question statistics)") 