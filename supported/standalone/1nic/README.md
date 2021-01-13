# Deploying the BIG-IP in Google Cloud - Single NIC

[![Slack Status](https://f5cloudsolutions.herokuapp.com/badge.svg)](https://f5cloudsolutions.herokuapp.com)

**Contents**

 - [Introduction](#introduction) 
 - [Prerequisites](#prerequisites-and-notes)
 - [Security](#security)
 - [Deploying the Template](#deploying-the-template)
 - [Configuration Example](#config)
 
 
## Introduction
This solution uses a Google Deployment Manger Template to launch a single NIC deployment a BIG-IP VE in an Google Virtual Private Cloud. Traffic flows from the BIG-IP VE to the application servers.  This is the standard Cloud design where the compute instance of
F5 is running with a single interface, which processes both management and data plane traffic.  This is a traditional model in the cloud where the deployment is considered one-armed.
 
The **existing stack** Google Deployment Manager template incorporates an existing Networking. If you would like to run a *full stack* which creates and configures the BIG-IP, the Google Cloud infrastructure, as well as a backend webserver, see the templates located in the *learning-stacks* folder in the **experimental** directory.


## Prerequisites and notes
The following are prerequisites and configuration notes for the F5 single NIC GDM template:
  - You just have installed the Google Cloud SDK (https://cloud.google.com/sdk/downloads)
  - An F5 Networks BYOL license available
  - A network with one subnet
  - Key pair for SSH access to BIG-IP VE (you can create or import this in Google Cloud)
  - An Google Firewall rule with the following inbound rules:
    - Port 22 for SSH access to the BIG-IP VE
    - Port 8443 (or other port) for accessing the BIG-IP web-based Configuration utility
    - A port for accessing your applications via the BIG-IP virtual server
  - This solution uses the SSH key to enable access to the BIG-IP system. If you want access to the BIG-IP web-based Configuration utility, you must first SSH into the BIG-IP VE using the SSH key you provided in the template.  You can then create a user account with admin-level permissions on the BIG-IP VE to allow access if necessary.
  - You must use a BIG-IP instance that has at least 2 vCPU and 4 GB memory. For each additional vCPU, add at least 2 GB of memory. Note: Because of this requirement, the *n1-highcpu* instance types are not supported.

  
### Security
This GDM template downloads helper code to configure the BIG-IP system. If your organization is security conscious and you want to verify the integrity of the template, you can open the GDM template (**f5-existing-stack-byol-1nic-bigip.py**) and ensure the following lines are present. See [Security Detail](#securitydetail) for the exact code in each of the following sections.
  - In the */config/verifyHash* section: **script-signature** and then a hashed signature
  - In the */config/installCloudLibs.sh* section **"tmsh load sys config merge file /config/verifyHash"**
  
  Additionally, F5 provides checksums for all of our supported Google Deployment Manager templates. For instructions and the checksums to compare against, see https://devcentral.f5.com/codeshare/checksums-for-f5-supported-cft-and-arm-templates-on-github-1014.
  


### Help 
Because this template has been created and fully tested by F5 Networks, it is fully supported by F5. This means you can get assistance if necessary from F5 Technical Support.

We encourage you to use our [Slack channel](https://f5cloudsolutions.herokuapp.com) for discussion and assistance on F5 CloudFormation templates.  This channel is typically monitored Monday-Friday 9-5 PST by F5 employees who will offer best-effort support. 



## Deploying the template
This solution uses a YAML file for containing the parameters necessary to deploy the BIG-IP instance in Google Cloud.  The YAML file (**f5-existing-stack-byol-1nic-bigip.yaml**) resides in this repository.  You ***must edit the YAML file*** to include information for your deployment before using the file to launch the BIG-IP VE instance.
1. Make sure you have completed all of the [prerequisites](#prerequisites). 
2. [Edit the parameters](#edit-the-yaml-file) in the **f5-existing-stack-byol-1nic-bigip.yaml** YAML file in this repository as described in this section.
3. [Save the YAML file](#save-the-yaml-file).
4. [Deploy the BIG-IP VE](#deploy-the-big-ip-ve) from the command line. 

### Edit the YAML file
After completing the prerequisites, edit the YAML file.  You must replace the following parameters with the appropriate values:


| Parameter | Description |
| --- | --- |
| availabilityZone1 | The availability zone where you want to deploy the BIG-IP VE instance, such as **us-west1-a** |
| licenseKey1 | Your F5 BIG-IP BYOL license key |
| instanceType | The BIG-IP instance type you want to use, such as **n1-standard-2** |
| subnet1 | The name of your subnet |
| bigipDns | The IP address of the DNS Server, example 4.4.4.4, currently required; subnet DHCP assigned DNS also added. |

Example of the YAML file:


```yaml 
imports:
- path: f5-existing-stack-byol-1nic-bigip.py
resources:
- name: bigip-1nic-setup
  type: f5-existing-stack-byol-1nic-bigip.py
  properties:
   availabilityZone1: <your_zone>
   ### Zone to deploy BIG-IP and supporting resources, for example us-west1-a
   licenseKey1: <your_lic_key>
   ### BIG-IP license key
   imageName: f5-byol-bigip-13-0-0-0-0-177-best-jan-23-2017-10-28am
   ### BIG-IP build to use
   instanceType: n1-standard-2
   ### Instance type assigned to BIG-IP
   subnet1: <your_subnet_name>
   ### Network BIG-IP should use
   manGuiPort: '8443'
   ### BIG-IP Management Port, the default is 8443
   bigipDns: '<your_server>'
   ### DNS Server, example 4.4.4.4, currently required; subnet DHCP assigned DNS also added.
```

### Save the YAML file
After you have edited the YAML file with the appropriate values, save the YAML file in a location accessible from the gcloud command line.

### Deploy the BIG-IP VE
The final task is to deploy the BIG-IP VE by running the following command from the **gcloud** command line:

```gcloud deployment-manager deployments create <your-deployment-name> --config <your-file-name.yaml>```

Keep in mind the following:  
+ *your-deployment-name*<br>This name must be unique.<br> 
+ *your-file-name.yaml*<br>  If your file is not in the same directory as the Google SDK, include the full file path in the command.


<br>



## Configuration Example <a name="config"></a>

The following is a simple configuration diagram for this single NIC deployment. In this scenario, all access to the BIG-IP VE appliance is through the same IP address and virtual network interface (vNIC).  This interface processes both management and data plane traffic.

![Single NIC configuration example](images/google_setup.png)
### Documentation
The ***BIG-IP Virtual Edition and Google Cloud Platform: Setup*** guide (https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-ve-setup-google-cloud-platform-13-0-0.html) details how to create the configuration manually without using the template.  This document also describes the configuration in more detail.


## Security Details <a name="securitydetail"></a>
This section has the entire code snippets for each of the lines you should ensure are present in your template file if you want to verify the integrity of the helper code in the template.

**/config/verifyHash section**

Note the hashes and script-signature may be different in your template. The important thing to check is that there is a script-signature line present in the location.<br>


```json
"/config/verifyHash": {
                "content": {
                  "Fn::Join": [
                    "\n",
                    [
                      "cli script /Common/verifyHash {",
                      "proc script::run {} {",
                      "    set file_path  [lindex $tmsh::argv 1]",
                      "    set expected_hash 73d01a6b4f27032fd31ea7eba55487430ed858feaabd949d4138094c26ce5521b4578c8fc0b20a87edc8cb0d9f28b32b803974ea52b10038f068e6a72fdb2bbd",
                      "    set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]",
                      "    if { $expected_hash eq $computed_hash } {",
                      "        exit 0",
                      "    }",
                      "    exit 1",
                      "}",
                      "    script-signature OGvFJVFxyBm/YlpBsOf8/AIyo5+p7luzrE11v8t7wJ1u24MBeit5pL/McqLxjydPJplymTcJ0qDEtXPZv09TTUF5hrF0g1pJ+z70omzJ6J9kOfOO8lyWP4XU/qM+ywEgAGoc8o8kGjKX01XcmB1e3rq6Mj5gE7CEkxKEcNzF3n5nDIFyBbpG6pJ8kg/7f6gtU14bJo0+ipNAiX+gBmT/10aUKKeJESU5wz+QqnEOE1WuTzdURArxditpk0+qqROZaSULD61w72hEy7kBC/miO+As7q8wjM5/H2yUHLoFLmBWP0jMWqIuzqnG+tgAFjJbZ1UJJDzWiYZK1TG1MsxfPg==",
                      "}"
                    ]
                  ]
                },
                "mode": "000755",
                "owner": "root",
                "group": "root"
              }
```
<br><br>
**/config/installCloudLibs.sh section**


```json
"/config/installCloudLibs.sh": {
                "content": {
                  "Fn::Join": [
                    "\n",
                    [
                      "#!/bin/bash",
                      "echo about to execute",
                      "checks=0",
                      "while [ $checks -lt 120 ]; do echo checking mcpd",
                      "    tmsh -a show sys mcp-state field-fmt | grep -q running",
                      "    if [ $? == 0 ]; then",
                      "        echo mcpd ready",
                      "        break",
                      "    fi",
                      "    echo mcpd not ready yet",
                      "    let checks=checks+1",
                      "    sleep 10",
                      "done",
                      "echo loading verifyHash script",
                      "tmsh load sys config merge file /config/verifyHash",
                      "if [ $? != 0 ]; then",
                      "    echo cannot validate signature of /config/verifyHash",
                      "    exit",
                      "fi",
                      "echo loaded verifyHash",
                      "echo verifying f5-cloud-libs.targ.gz",
                      "tmsh run cli script verifyHash /config/cloud/f5-cloud-libs.tar.gz",
                      "if [ $? != 0 ]; then",
                      "    echo f5-cloud-libs.tar.gz is not valid",
                      "    exit",
                      "fi",
                      "echo verified f5-cloud-libs.tar.gz",
                      "echo expanding f5-cloud-libs.tar.gz",
                      "tar xvfz /config/cloud/f5-aws-autoscale-cluster.tar.gz -C /config/cloud",
                      "tar xvfz /config/cloud/asm-policy-linux.tar.gz -C /config/cloud",
                      "tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/aws/node_modules",
                      "cd /config/cloud/aws/node_modules/f5-cloud-libs",
                      "echo installing dependencies",
                      "npm install --production /config/cloud/f5-cloud-libs-aws.tar.gz",
                      "touch /config/cloud/cloudLibsReady"
                    ]
                  ]
                },
                "mode": "000755",
                "owner": "root",
                "group": "root"
              }
```




## Filing Issues
If you find an issue, we would love to hear about it. 
You have a choice when it comes to filing issues:
  - Use the **Issues** link on the GitHub menu bar in this repository for items such as enhancement or feature requests and non-urgent bug fixes. Tell us as much as you can about what you found and how you found it.
  - Contact F5 Technical support via your typical method for more time sensitive changes and other issues requiring immediate support.



## Copyright

Copyright 2014-2017 F5 Networks Inc.


## License


Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must have
completed and submitted the `F5 Contributor License Agreement`