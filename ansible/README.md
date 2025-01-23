Deploying the FabMob's trip planner with Ansible.

# Deploy
1. Set the OTP graphs and configs
Create a folder into the [files](./files) folder. Put the OTP graphes (graph.obj, streetGRaph.obj) and OTP configs (otp-config.json, build-config.json, etc.) into it.

2. Set an inventory file
See preexisting files into the [inventories](./inventories/) folder.

Note 'opentripplanner_local_data_folder' is the folder you created in previous step.    

3. Run the playbook
Replace the placeholders and execute the playbook using the following command:
```
# Replace 'inventories/planbook.yaml' with your inventory.
# Replace 'your_taxi_api_key' with your montreal taxi api key. If you do not have any, leave an arbitrary string.
ansible-playbook playbook.yaml -i inventories/planbook.yaml --extra-vars "taxi_api_key=your_taxi_api_key"
```