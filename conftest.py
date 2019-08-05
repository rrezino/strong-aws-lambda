import sys
from os.path import abspath, dirname, join

module_path = join(abspath(dirname(__file__)), 'strong_aws_lambda_pkg')
sys.path.insert(0, module_path)
