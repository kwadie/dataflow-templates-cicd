#
# Copyright (C) 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
"""A word-counting workflow using Flex Templates."""

import sys
import argparse
import logging
from pipeline import wordcount

FORMATS = {'text', 'parquet', 'avro'}

if __name__ == '__main__':

    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input',
        dest='input',
        default='gs://dataflow-samples/shakespeare/kinglear.txt',
        help='Input file to process.')
    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to.')
    parser.add_argument('--format',
                        dest='format',
                        default='text',
                        help='Supported output file formats: %s.' % FORMATS)

    known_args, pipeline_args = parser.parse_known_args(sys.argv)

    if known_args.format not in FORMATS:
        raise ValueError('--format should be one of: %s' % FORMATS)

    wordcount.run(known_args, pipeline_args)
