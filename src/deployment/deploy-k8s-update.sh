ansible-playbook deploy-register-docker-images.yml -i inventory.yml
ansible-playbook update-k8s-containers.yml -i inventory-prod.yml