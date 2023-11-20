# How to setup the repo with Azure DevOps

This template supports Azure ML as a platform for ML, and Azure DevOps as a platform for operationalization. Therefore, we assume that you already have an Azure DevOps project in place, and have cloned the repository into the DevOps project.

In order to setup the repository, you need to complete few steps.

**Predeployment Setup**

**Assumption:**
You have setup an app registration, granted the resulting service principal, at least Contributor, and User Access Administrator on the target subscription.
**Use this document as a reference: [Create a Microsoft Entra application and service principal that can access resources](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal)

**Step n.** Create a service connection. You can use [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) as a reference. Use Azure Resource Manager as service connection type, and use the Manual option when creating the service connection.

**Step n.** Create a new variable group, mlops_platform_dev_vg, add "AZURE_RM_SVC_CONNECTION" variable with the name of the service connection created above. 
Information about variable groups in Azure DevOps can be found in [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic).

**Step n.** Create a *development* branch and make it as default one to make sure that all PRs should go towards to it. This template assumes that the team works at a *development* branch as a primary source for coding and improving the model quality. Later, you can implement Azure Pipeline that moves code from the *development* branch into qa/main or executes a release process right away. Release management is not in scope of this template.

**General Infrastructure instructions**
**Step n.** In the development branch, for the properties below, supply a value or accept the default in the infra_config.json:
**Note: It is important to set a unique version number to avoid attempting to deploy resources that already exist.**
- NAMESPACE: a base name used to construct consistent azure resource names.
- PROJECTCODE: a string used to construct consistent azure resource names project modifier.
- VERSION: a three-digit version string used to uniqueify azure resource names, ml endpoints, and ml deployments.
- AZURE_RM_SVC_CONNECTION: the name of service connection to be used to execute all Azure DevOps pipelines.
- RESOURCE_GROUP_NAME: the resource group to which azure resources will be deployed.
- CLUSTER_NAME: the name of the compute resource for pr deployment for training and inferencing in the azure machine learning resource
- BATCH_CLUSTER_NAME: the name of the compute resource for batch inferencing in the azure machine learning resource

**Step n.** In the development branch, set values or accept the defaults for variables in the model_config.json file. The pipeline uses multiple variables and they should be set for both 'pr' and 'dev' plus any additional environments. Also, set the variables for all models (i.e. nyc_taxi, london_taxi)

- ML_MODEL_CONFIG_NAME: The unique model name used internally by the pipelines.
- ENV_NAME: name of the environment. e.g pr, dev, test, prod.
- CLUSTER_REGION: a location/region where the cluster should be created.
- CONDA_PATH: a location of the conda file (mlops/nyc_taxi/environment/conda.yml).
- DISPLAY_BASE_NAME: a run base name (see EXPERIMENT_BASE_NAME for details).
- ENV_BASE_IMAGE_NAME: a base image for the environment (ex.: mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04).
- ENVIRONMENT_NAME: a name of the Azure ML environment.
- EXPERIMENT_BASE_NAME: an experiment base name. This parameter as well as two more parameters below we are using as a background to form unique names for experiments, runs and models. You can find a rule for the names implemented as powershell code in [here](../devops/pipeline/templates/variables_template.yml). By default we are using the branch name as well as build id to form the names that helps us to differentiate experiments, runs and models working in a big team of data scientists and software engineers. The EXPERIMENT_TYPE variable from the template is hard coded in _dev_pipeline.yml files.
- MODEL_BASE_NAME: a model base name (see EXPERIMENT_BASE_NAME for details).
- BATCH_DEPLOYMENT_CONFIG: relative path to the batch_config.json file.
- REALTIME_DEPLOYMENT_CONFIG: relative path to the realtime_config.json file.
- DATA_CONFIG_PATH: relative path to the data_config.json.

**Step n.**  In all batch_config.json and realtime_config.json files, provide a unique name for the following properties.
- BATCH_CLUSTER_NAME: The unique name for a cluster to be used for batch inferencing. 
**Note: Since this cluster is created by the Infrastructure deployment, the name must match the value for BATCH_CLUSTER_NAME in /config/infra_config.yml**
- ENDPOINT_NAME
- DEPLOYMENT_NAME

**Step n.** Create an azure pipeline to deploy the infrastructure.  Your pipeline should be based on either a bicep (infra_provision_bicep_pipeline.yml) or a terraform (infra_provision_terraform_pipeline.yml) Azure Pipelines yaml file. 

**Step n.** Create one or more Azure Pipelines to setup build validation for the any of the use cases listed below:
- nyc_taxi_pr_dev_pipeline.yml
- london_taxi_pr_dev_pipeline.yml

**Step n.** Create one or more Azure Pipelines to setup continuous integration for the any of the use cases listed below:
- nyc_taxi_ci_dev_pipeline.yml
- london_taxi_ci_dev_pipeline.yml

More details about how to create a basic Azure Pipeline can be found [here](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs).

**Step n.** Setup a branch policy for the *development* branch. At this stage we have one or more Azure Pipeline(s) that should be executed on every PR to the *development* branch. At the same time successful completion of the build is not a requirement. So, it's important to add our PR build as a policy. Pay special attention that model_pr.yml](../devops/pipeline/model_pr.yml) has various paths in place. We are using these paths to limit number of runs if the current PR doesn't affect ML component (for example, PR modifies a documentation file). Therefore, setting up the policy you need to make sure that you are using the same set of paths in the *Path filter* field.

More details about how to create a policy can be found [here](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser).

**Step n. (Optional)** It's a common practice to execute a training job on the full dataset once a PR has been merged into the development branch. At the same time, the training process can take a long time (many hours or even days) and Azure DevOps agent will not be able to let you know about the status due to timeout settings. So, it's very hard to implement a single CI Build that is waiting for a new model (training results) and execute other steps after that (model approval, model movement into qa environment, model deployment etc).

Azure ML provides a solution that allows us to implement a *server* task in Azure DevOps Build and wait for the result of the pipeline training job with no Azure DevOps agent holding. Thanks to that it's possible to wait for results any amount of time and execute all other steps right after completion of the Azure ML training job. As for now, the feature is in active development, but you can [visit this link](https://github.com/Azure/azure-mlops-automation) to check the status and find how to get access. This new Azure ML feature can be included in your CI Build thanks to the extension that Azure ML team built or you can use RestAPITask for a direct REST call. In this template we implemented a version with the extension.


**Manual Execution**

**Provision Infrastructure**
- Execute the infrastructure provision pipeline (infra_provision_bicep_pipeline.yml OR infra_provision_terraform_pipeline.yml).

**Run PR pipeline**
- Execute any of the Azure Pipelines created above for build validation

**Run CI pipeline**
- Execute any of the Azure Pipelines created above for continuous integration
