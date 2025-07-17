import subprocess
import os

current_dir = os.getcwd()

# Target project directory
project_dir = '/home/jeff/projects/bbochat'
os.chdir(project_dir)

# Use the venv's python to run pip
venv_python = os.path.join(project_dir, '.venv', 'bin', 'python')
subprocess.run([venv_python, '-m', 'pip', 'install', '-U', 'pip'])

subprocess.run(f'source deactivate', shell=True)
os.chdir(current_dir)
subprocess.run(f'source .venv/bin/activate', shell=True)
