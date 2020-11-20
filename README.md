# Dataflow Flex Template CICD

This is a proof-of-concept for continuously deploying a Dataflow job using [Flex Template](https://cloud.google.com/dataflow/docs/guides/templates/overview#flex-templated-dataflow-jobs) and Cloud Build.

It extends the work in [DataflowTemplates/flex-wordcount-python](https://github.com/GoogleCloudPlatform/DataflowTemplates/tree/master/v2/flex-wordcount-python) by: 
* Adding the CICD pipeline and usage.
* Demonstrating how to template a Python pipeline with multiple file dependencies.


## Overview
The Wordcount pipeline demonstrates how to use Flex Templates in Dataflow to create a template out of practically any Dataflow pipeline. This pipeline
does not use any [ValueProvider](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/options/value_provider.py) to accept user inputs and is built like any other non-templated
Dataflow pipeline. This pipeline also allows the user to change the job
graph depending on the value provided for an option at runtime
(*--format=text|avro|parquet*)

We make the pipeline ready for reuse by "packaging" the pipeline artifacts
in a Docker container. In order to simplify the process of packaging the pipeline into a container we
utilize [Google Cloud Build](https://cloud.google.com/cloud-build/).

We preinstall all the dependencies needed to *compile and execute* the pipeline
into a container using a custom [Dockerfile](Dockerfile).

In this example, we are using the following base image for Python 3:

`gcr.io/dataflow-templates-base/python3-template-launcher-base`

We will utilize Google Cloud Builds ability to build a container using a Dockerfile as documented in the [quickstart](https://cloud.google.com/cloud-build/docs/quickstart-docker).

In addition, we will use a CICD pipeline on Cloud Build to update the flex template automatically.

## Dataflow Pipeline
* [wordcount.py](wordcount/pipeline/wordcount.py) - The Wordcount pipeline is a batch pipeline which performs a wordcount on an input text file (via --input flag) and writes the word count to GCS. The output format is determined by the value of the --format flag which can be set to either text, avro or parquet.
* [main.py](wordcount/main.py) - The entry point of the pipeline to parse command arguments and call ```wordcount.run(params)```
* [setup.py](wordcount/setup.py) - To package the pipeline and distribute it to the workers. Without this file, main.py won't be able to import wordcount.py at runtime. [[source]](https://beam.apache.org/documentation/sdks/python-pipeline-dependencies/#multiple-file-dependencies) 


## Getting started
To run the CICD pipeline end-to-end:

1. Create a fork/copy of this repo on Github or Cloud Source Repositories, or start a new one.
2. Trigger a manual or automated build as explained in the [CICD](#CICD) section.
3. Run the template as explained in the [Running Flex Templates](#Running-flex-templates) section.
4. Monitor the job progress in the Dataflow job history page.


## CICD
### Steps
The CICD pipeline is defined in [cloudbuild.yaml](cloudbuild.yaml) to be executed by Cloud Build. It follows the following steps:
1. Build and register a container image via Cloud Build as defined in the [Dockerfile](Dockerfile). The container packages the Dataflow pipeline and its dependencies and acts as the Dataflow Flex Template
2. Build the Dataflow template by creating a spec.json file on GCS including the container image ID and the pipeline metadata based on [metadata.json](wordcount/spec/metadata.json). The template could be run later on by pointing to this spec.json file 

### Substitution variables
Cloud Build provides default variables such as $PROJECT_ID that could be used in the build YAML file. User defined variables could also be used in the form of $_USER_VARIABLE.

In this project the following variables are used:
- $_TARGET_GCR_IMAGE: The GCR image name to be submitted to Cloud Build (not URI) (e.g wordcount-flex-template)
- $_TEMPLATE_GCS_LOCATION: GCS location to store the template spec file (e.g. gs://bucket/dir/). The spec file path is required later on to submit run commands to Dataflow

These variables must be set during manual build execution or via a build trigger

### Manual builds

In the repo root directory, set the following variables:
```
TEMPLATE_GCS_LOCATION=gs://bucket/dir/spec.json
TARGET_GCR_IMAGE=word_count_flex_template_python
REGION=<GCP REGION>
INPUT=gs://dataflow-samples/shakespeare/kinglear.txt
OUTPUT=gs://bucket/dir/
FORMAT=text
SETUP_FILE=/dataflow/template/setup.py
```

Then run the following command:

```
gcloud builds submit --config=cloudbuild.yaml --substitutions=_TARGET_GCR_IMAGE=$TARGET_GCR_IMAGE,_TEMPLATE_GCS_LOCATION=$TEMPLATE_GCS_LOCATION
```


### Triggering builds automatically
To trigger a build on certain actions (e.g. commits to master)
1. Go to Cloud Build > Triggers > Create Trigger. If you're using Github, choose the "Connect Repository" option.     
2. Configure the trigger
3. Point the trigger to the [cloudbuild.yaml](cloudbuild.yaml) file in the repository
4. Add the substitution variables as explained in the [Substitution variables](#substitution-variables) section.


## Running Flex Templates
After deploying the template, one can run it using this command: (after setting the required variables as in [Manual Builds](#manual-builds))
```
 gcloud dataflow flex-template run "wordcount-flex-template-`date +%Y%m%d-%H%M%S`" \
 --template-file-gcs-location $TEMPLATE_GCS_LOCATION \
 --region $REGION \
 --parameters input=$INPUT \
 --parameters output=$OUTPUT \
 --parameters format=$FORMAT \
 --parameters setup_file=$SETUP_FILE
```
Note that the parameter setup_file must be included in [metadata.json](wordcount/spec/metadata.json) and passed to the pipeline. It enables working with multiple Python modules/files and it's set to the path of 
[setup.py](wordcount/setup.py) inside the docker container. 

