terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 3.38"
    }
  }
}

resource "google_service_account" "composer-worker-sa" {
  account_id   = "composer-env-account"
  display_name = "Test Service Account for Composer Environment"
  project = var.gcp_project_id
}

resource "google_project_iam_member" "composer-worker" {
  project = var.gcp_project_id
  role   = "roles/composer.worker"
  member = "serviceAccount:${google_service_account.composer-worker-sa.email}"
}

resource "google_project_iam_member" "composer-owner" {
  project = var.gcp_project_id
  role   = "roles/owner"
  member = "serviceAccount:${google_service_account.composer-worker-sa.email}"
}

resource "google_secret_manager_secret" "secret-composer-sa" {
  secret_id = "airflow-variables-composer_worker_sa"

  labels = {
    label = "my-label"
  }

  replication {
    automatic = true
  }
  project = var.gcp_project_id
}

resource "google_service_account_key" "composer-worker-key" {
  service_account_id = google_service_account.composer-worker-sa.name
}

resource "google_secret_manager_secret_version" "secret-version-composer" {
  secret = google_secret_manager_secret.secret-composer-sa.id

  secret_data = base64decode(google_service_account_key.composer-worker-key.private_key)
}

resource "google_composer_environment" "composer" {
  project = var.gcp_project_id
  name   = "composer-main"
  region = "europe-west1"

  config {
    node_count = 3

    node_config {
      zone         = "europe-west1-c"
      machine_type = "n1-standard-1"
      service_account  = google_service_account.composer-worker-sa.name
    }

    software_config {
      image_version = "composer-1.12.3-airflow-1.10.10"
      python_version = "3"

      airflow_config_overrides = {
        scheduler-catchup_by_default = "False"
        #secrets-backend = "airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend"
      }

      pypi_packages = {
        jira = ""
      }
      env_variables = {
        GCP_PROJECT_ID = var.gcp_project_id
      }
    }
  }
  depends_on = [google_project_iam_member.composer-worker]
}

resource "google_container_node_pool" "composer-node-pool" {
  name       = "memory-heavy"
  project = var.gcp_project_id
  location   = "europe-west1-c"
  cluster    = reverse(split("/",google_composer_environment.composer.config.0.gke_cluster))[0]
  node_count = 0

  autoscaling {
    max_node_count = 1
    min_node_count = 0
  }

  node_config {
    machine_type = "n1-highmem-2"

    taint {
      effect = "NO_SCHEDULE"
      key = "workshop"
      value = "custom"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}

resource "google_container_cluster" "primary" {
  project = var.gcp_project_id
  name               = "machinelearning"
  location           = "europe-west1-c"
  initial_node_count = 2

  master_auth {
    username = ""
    password = ""

    client_certificate_config {
      issue_client_certificate = false
    }
  }

  node_config {
    service_account  = google_service_account.composer-worker-sa.email
    machine_type = "e2-medium"
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  timeouts {
    create = "30m"
    update = "40m"
  }
}