#!/usr/bin/env bash
gcloud projects add-iam-policy-binding ${gcp_project_id} --member=user:$1 --role=roles/composer.user