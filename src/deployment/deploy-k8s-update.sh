ansible-playbook deploy-register-docker-images.yml -i inventory.yml
ansible-playbook deploy-k8s-create-cluster.yml -i inventory.yml
ansible-playbook deploy-k8s-setup-containers.yml -i inventory-prod.yml
# ansible-playbook update-k8s-containers.yml -i inventory-prod.yml