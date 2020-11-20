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

FROM gcr.io/dataflow-templates-base/python3-template-launcher-base

RUN mkdir -p /dataflow/template
WORKDIR /dataflow/template

COPY wordcount/pipeline /dataflow/template/pipeline
COPY wordcount/setup.py /dataflow/template/setup.py
COPY wordcount/main.py /dataflow/template/main.py

RUN pip install avro-python3 pyarrow==0.11.1 apache-beam[gcp]==2.24.0

# Entry point for the Dataflow job.
# By setting this variable, no need for setting DATAFLOW_PYTHON_COMMAND_SPEC=python_command_spec.json.
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/dataflow/template/main.py"
