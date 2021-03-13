# Copyright 2017 F5 Networks All rights reserved.
#
# Version v1.0.0 

"""Creates BIG-IP"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'
def GenerateConfig(context):
  resources = [{
      'name': 'net-' + context.env['deployment'],
      'type': 'compute.v1.network',
      'properties': {
          'IPv4Range': '10.0.0.1/24'
      }
  }, {
      'name': 'firewall-' + context.env['deployment'],
      'type': 'compute.v1.firewall',
      'properties': {
          'network': '$(ref.net-' + context.env['deployment'] + '.selfLink)',
          'sourceRanges': ['0.0.0.0/0'],
          'allowed': [{
              'IPProtocol': 'TCP',
              'ports': [80,22,443,8443]
          }]
      }
  }, {
      'name': 'webserver-' + context.env['deployment'],
      'type': 'compute.v1.instance',
      'properties': {
          'zone': context.properties['availabilityZone1'],
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/zones/',
                                  context.properties['availabilityZone1'], '/machineTypes/',
                                  context.properties['instanceType']]),
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/',
                                          'debian-cloud/global/',
                                          'images/family/debian-8'])
              }
          }],
          'networkInterfaces': [{
              'network': '$(ref.net-' + context.env['deployment']
                         + '.selfLink)',
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'metadata': {
              'items': [{
                  'key': 'startup-script',
                  'value': ''.join(['#!/bin/bash\n',
                                    'INSTANCE=$(curl http://metadata.google.',
                                    'internal/computeMetadata/v1/instance/',
                                    'hostname -H "Metadata-Flavor: Google")\n',
                                    'echo "<html><header><title>Hello from ',
                                    'Deployment Manager!</title></header>',
                                    '<body><h2>Hello from $INSTANCE</h2><p>',
                                    'Google Deployment Manager and F5 bids you good day!</p>',
                                    '</body></html>" > index.html\n',
                                    'sudo python -m SimpleHTTPServer 80\n'])
              }]
          }
      }
  }, {
      'name': 'bigip1-' + context.env['deployment'],
      'type': 'compute.v1.instance',
      'properties': {
          'zone': context.properties['availabilityZone1'],
          'machineType': ''.join([COMPUTE_URL_BASE, 'projects/',
                                  context.env['project'], '/zones/',
                                  context.properties['availabilityZone1'], '/machineTypes/',
                                  context.properties['instanceType']]),
          'disks': [{
              'deviceName': 'boot',
              'type': 'PERSISTENT',
              'boot': True,
              'autoDelete': True,
              'initializeParams': {
                  'sourceImage': ''.join([COMPUTE_URL_BASE, 'projects/f5-7626-networks-public',
                                          '/global/images/',
                                          context.properties['imageName'],
                                         ])
              }
          }],
          'networkInterfaces': [{
              'network': '$(ref.net-' + context.env['deployment'] + '.selfLink)',
              'accessConfigs': [{
                  'name': 'External NAT',
                  'type': 'ONE_TO_ONE_NAT'
              }]
          }],
          'metadata': {
              'items': [{
                  'key': 'output',
                  'value': 'Testing',  
                  'key': 'startup-script',
                  'value': (''.join(['#!/bin/bash\n',
                                    'if [ -f /config/startupFinished ]; then\n',
                                    '    exit\n',
                                    'fi\n',
                                    'mkdir -p /config/cloud/gce\n',
                                    'cat <<\'EOF\' > /config/installCloudLibs.sh\n',
                                    '#!/bin/bash\n',
                                    'echo about to execute\n',
                                    'checks=0\n',
                                    'while [ $checks -lt 120 ]; do echo checking mcpd\n',
                                    '    tmsh -a show sys mcp-state field-fmt | grep -q running\n',
                                    '    if [ $? == 0 ]; then\n',
                                    '        echo mcpd ready\n',
                                    '        break\n',
                                    '    fi\n',
                                    '    echo mcpd not ready yet\n',
                                    '    let checks=checks+1\n',
                                    '    sleep 10\n',
                                    'done\n',
                                    'echo loading verifyHash script\n',
                                    'if ! tmsh load sys config merge file /config/verifyHash; then\n',
                                    '    echo cannot validate signature of /config/verifyHash\n',
                                    '    exit\n',
                                    'fi\n',
                                    'echo loaded verifyHash\n',
                                    'declare -a filesToVerify=(\"/config/cloud/f5-cloud-libs.tar.gz\")\n',
                                    'for fileToVerify in \"${filesToVerify[@]}\"\n',
                                    'do\n',
                                    '    echo verifying \"$fileToVerify\"\n',
                                    '    if ! tmsh run cli script verifyHash \"$fileToVerify\"; then\n',
                                    '        echo \"$fileToVerify\" is not valid\n',
                                    '        exit 1\n',
                                    '    fi\n',
                                    '    echo verified \"$fileToVerify\"\n',
                                    'done\n',
                                    'mkdir -p /config/cloud/gce/node_modules\n',
                                    'echo expanding f5-cloud-libs.tar.gz\n',
                                    'tar xvfz /config/cloud/f5-cloud-libs.tar.gz -C /config/cloud/gce/node_modules\n',
                                    'touch /config/cloud/cloudLibsReady\n',
                                    'EOF\n',                                   
                                    'cat <<\'EOF\' > /config/verifyHash\n',
                                    'cli script /Common/verifyHash {\n',
                                    '    proc script::run {} {\n',
                                    '        if {[catch {\n',
                                    '            set hashes(f5-cloud-libs.tar.gz) 862f7c19396088ab012fda7c2b262621c17f134b1d39d7a4d0b765eaf92f3ddc7354716a4f546fabb866df9876e1baed5799ae4a2c9d0ea6f01f79a38b9d3b3e\n',
                                    '            set hashes(f5-cloud-libs-aws.tar.gz) 2566f515fb46d89f5a245079b0efdad60fd78327c352e567bd5d573eb2ee0093d167a2f054b2408bd7df49c5debc4218074fdb50cfe135bb80ccc6c303a03f72\n',
                                    '            set hashes(f5-cloud-libs-azure.tar.gz) 9d4dc6779a5d25253832598d42681defa54c5f4521a70ba8e053179c262cdf0d5c8d6a3d458ea21da1d95212792b099bf2721ddbe175eed035cd1e00647124cf\n',
                                    '            set hashes(asm-policy-linux.tar.gz) 63b5c2a51ca09c43bd89af3773bbab87c71a6e7f6ad9410b229b4e0a1c483d46f1a9fff39d9944041b02ee9260724027414de592e99f4c2475415323e18a72e0\n',
                                    '            set hashes(f5.http.v1.2.0rc4.tmpl) 47c19a83ebfc7bd1e9e9c35f3424945ef8694aa437eedd17b6a387788d4db1396fefe445199b497064d76967b0d50238154190ca0bd73941298fc257df4dc034\n',
                                    '            set hashes(f5.http.v1.2.0rc6.tmpl) 811b14bffaab5ed0365f0106bb5ce5e4ec22385655ea3ac04de2a39bd9944f51e3714619dae7ca43662c956b5212228858f0592672a2579d4a87769186e2cbfe\n',
                                    '            set hashes(f5.http.v1.2.0rc7.tmpl) 21f413342e9a7a281a0f0e1301e745aa86af21a697d2e6fdc21dd279734936631e92f34bf1c2d2504c201f56ccd75c5c13baa2fe7653213689ec3c9e27dff77d\n',
                                    '            set hashes(f5.aws_advanced_ha.v1.3.0rc1.tmpl) 9e55149c010c1d395abdae3c3d2cb83ec13d31ed39424695e88680cf3ed5a013d626b326711d3d40ef2df46b72d414b4cb8e4f445ea0738dcbd25c4c843ac39d\n',
                                    '            set hashes(f5.aws_advanced_ha.v1.4.0rc1.tmpl) de068455257412a949f1eadccaee8506347e04fd69bfb645001b76f200127668e4a06be2bbb94e10fefc215cfc3665b07945e6d733cbe1a4fa1b88e881590396\n',
                                    '            set hashes(asm-policy.tar.gz) 2d39ec60d006d05d8a1567a1d8aae722419e8b062ad77d6d9a31652971e5e67bc4043d81671ba2a8b12dd229ea46d205144f75374ed4cae58cefa8f9ab6533e6\n',
                                    '            set hashes(deploy_waf.sh) 4db3176b45913a5e7ccf42ab9c7ac9d7de115cdbd030b9e735946f92456b6eb433087ed0e98ac4981c76d475cd38f4de49cd98c063e13d50328a270e5b3daa4a\n',
                                    '            set hashes(f5.policy_creator.tmpl) 54d265e0a573d3ae99864adf4e054b293644e48a54de1e19e8a6826aa32ab03bd04c7255fd9c980c3673e9cd326b0ced513665a91367add1866875e5ef3c4e3a\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            set file_path [lindex $tmsh::argv 1]\n',
                                    '            set file_name [file tail $file_path]\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            if {![info exists hashes($file_name)]} {\n',
                                    '                tmsh::log err \"No hash found for $file_name\"\n',
                                    '                exit 1\n',
                                    '            }\n',
                                    'EOF\n',
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' >> /config/verifyHash\n',
                                    '            set expected_hash $hashes($file_name)\n',
                                    '            set computed_hash [lindex [exec /usr/bin/openssl dgst -r -sha512 $file_path] 0]\n',
                                    '            if { $expected_hash eq $computed_hash } {\n',
                                    '                exit 0\n',
                                    '            }\n',
                                    '            tmsh::log err \"Hash does not match for $file_path\"\n',
                                    '            exit 1\n',
                                    '        }]} {\n',
                                    '            tmsh::log err {Unexpected error in verifyHash}\n',
                                    '            exit 1\n',
                                    '        }\n',
                                    '    }\n',
                                    '    script-signature VwqAYsu1/TM/B7OPgCB2SXyiQ5s0MJH6qqzrypWaoZcRtXc9w9jNz8YwmqQyFn7TWTqCCLxmnMT4bmLzqNIYWesegv7w5KcBMwA8C0NTOebjHLkqKPzr2P68NiVzPN1/gxp3Y2i2e9zpnvy8PXcWRK3PkauO8lVSE7TJ07/uydvjg9t3GEjN449TUIZ+fx0NhqxS9VD6HDqv66FKgVcAeiomqrB2YQeawE4oShnbV2ULBP9IN8X/Rp9cb2gw1IPYZcLneP/rtgkMHOPmnzPV4u+tEowPzIjAo9mTV2J7e4z50peN3vdD7ThO1aPdcd5dfxbRqWZtlyV/pDPPHVVEdg==\n',
                                    '    signing-key /Common/f5-irule\n',
                                    '}\n',
                                    'EOF\n',                                    
                                    'echo -e "" >> /config/verifyHash\n',
                                    'cat <<\'EOF\' > /config/waitThenRun.sh\n',
                                    '#!/bin/bash\n',
                                    'while true; do echo \"waiting for cloud libs install to complete\"\n',
                                    '    if [ -f /config/cloud/cloudLibsReady ]; then\n',
                                    '        break\n',
                                    '    else\n',
                                    '        sleep 10\n',
                                    '    fi\n',
                                    'done\n',
                                    '\"$@\"\n',
                                    'EOF\n',
                                    'cat <<\'EOF\' > /config/cloud/gce/custom-config.sh\n',
                                    '#!/bin/bash\n',
                                    'date\n',
                                    'echo \'starting tmsh config\'\n',
                                    'tmsh save /sys config\n',
                                    'date\n',
                                    '### START CUSTOM TMSH CONFIGURTION\n',
                                    'tmsh create ltm pool demo-pool members add { 10.0.0.3:80 } monitor http\n',
                                    'tmsh create ltm virtual /Common/demp-80 { destination 10.0.0.2:80 ip-protocol tcp pool /Common/demo-pool profiles replace-all-with { tcp { } http { } }  source 0.0.0.0/0 source-address-translation { type automap } translate-address enabled translate-port enabled }\n',
                                    '### END CUSTOM TMSH CONFIGURATION\n',
                                    'EOF\n',
                                    'cat <<\'EOF\' > /config/cloud/gce/rm-password.sh\n',
                                    '#!/bin/bash\n',
                                    'date\n',
                                    'echo \'starting rm-password.sh\'\n',
                                    'rm /config/cloud/gce/.adminPassword\n',
                                    'date\n',
                                    'EOF\n',
                                    'curl -s -f --retry 20 -o /config/cloud/f5-cloud-libs.tar.gz https://raw.githubusercontent.com/F5Networks/f5-cloud-libs/v3.0.2/dist/f5-cloud-libs.tar.gz\n',
                                    'chmod 755 /config/verifyHash\n',
                                    'chmod 755 /config/installCloudLibs.sh\n',
                                    'chmod 755 /config/waitThenRun.sh\n',
                                    'chmod 755 /config/cloud/gce/custom-config.sh\n',
                                    'chmod 755 /config/cloud/gce/rm-password.sh\n',
                                    'nohup /config/installCloudLibs.sh &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --signal PASSWORD_CREATED --file f5-rest-node --cl-args \'/config/cloud/gce/node_modules/f5-cloud-libs/scripts/generatePassword --file /config/cloud/gce/.adminPassword\' --log-level verbose -o /var/log/generatePassword.log &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --wait-for PASSWORD_CREATED --signal ADMIN_CREATED --file /config/cloud/gce/node_modules/f5-cloud-libs/scripts/createUser.sh --cl-args \'--user admin --password-file /config/cloud/gce/.adminPassword\' --log-level debug -o /var/log/createUser.log &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/onboard.js --port 8443 --ssl-port ',
                                    context.properties['manGuiPort'],
                                    ' --wait-for ADMIN_CREATED -o /var/log/onboard.log --log-level debug --no-reboot --host localhost --user admin --password-url file:///config/cloud/gce/.adminPassword --ntp 0.us.pool.ntp.org --ntp 1.us.pool.ntp.org --tz UTC --dns ',
                                    context.properties['bigipDns'],
                                    ' --module ltm:nominal --license ',
                                    context.properties['licenseKey1'],
                                    ' --ping &>> /var/log/cloudlibs-install.log < /dev/null &\n',                                   
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --file /config/cloud/gce/custom-config.sh --cwd /config/cloud/gce -o /var/log/custom-config.log --log-level debug --wait-for ONBOARD_DONE --signal CUSTOM_CONFIG_DONE &>> /var/log/cloudlibs-install.log < /dev/null &\n',
                                    'nohup /config/waitThenRun.sh f5-rest-node /config/cloud/gce/node_modules/f5-cloud-libs/scripts/runScript.js --file /config/cloud/gce/rm-password.sh --cwd /config/cloud/gce -o /var/log/rm-password.log --log-level debug --wait-for CUSTOM_CONFIG_DONE --signal PASSWORD_REMOVED &>> /var/log/cloudlibs-install.log < /dev/null &\n',        
                                    'touch /config/startupFinished\n',
                                    ])
                            )
              }]
          }
      }
  }]
  outputs = [{
      'name': 'bigipIP',
      'value': ''.join(['$(ref.' + context.env['name'] + '-' + context.env['deployment'] + '.bigipIP)'])
  }] 
  return {'resources': resources}