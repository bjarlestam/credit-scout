import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from credit_scout.main import cli

if __name__ == '__main__':
    cli() 