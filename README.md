# gcp-cloud-composer-pod-operator
Contains example dags and terraform code to create a composer with a node pool to run pods.
This is usually used within workshops with clients, but is also a resource for this blog post: <TODO>

# Installation
Make sure you have terraform installed (0.13)
Change vars.tf to reflect the project id you want to use
```bash
terraform plan -out planfile.plan
terraform apply "planfile.plan"
```

The terraform script might miss some api enablement, so you might have to do that manually. 

Note that the composer cluster is created with owner privileges.  you do not want this for production. 

# Manual steps.
Sync the dags folder to your dags-bucket manually.
![composer](https://github.com/ael-computas/gcp-cloud-composer-pod-operator/raw/main/media/dags_folder.png)
Click the dags location bucket to get the name of the bucket.

then run 
```bash
export BUCKET=gs://.....
gsutil cp -r composer/dags  gs://${BUCKET}
```

# Cleanup
```bash
terraform destroy
```

Note that terraform doesnt destroy the buckets created for composer, so you will have to do this manually.