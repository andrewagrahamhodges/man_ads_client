node("x2go") {
  deleteDir()
  checkout scm
  stage("Create Certificates") {
      sh "mkdir -p client/java/certificate"
      sh "keytool -genkey -keystore client/java/certificate/keystore -alias ulteo -dname \"CN=manconsulting.co.uk, OU=MAN, O=MAN, L=UK, S=UK, C=UK\"   -storepass 123456  -keypass 123456"
      sh "keytool -selfcert -keystore client/java/certificate/keystore -alias ulteo -storepass 123456 -keypass 123456"
  }
  stage("Build") {
    dir("client/java/") {
        sh "./autogen"
        sh "ant ovdNativeClient"
        sh "cp -r windlls.zip build/resources"
        dir("build/resources") {
            sh "unzip windlls.zip && rm -rf windlls.zip"
        }
        sh "ant ovdNativeClient.jar"
        sh "ant ovdIntegratedLauncher.jar"
    }
    dir("client/java/jars") {
        sh "mv ../../../openjdk/* ."
        //archiveArtifacts '*.jar'
    }
    
    dir("client/OVDIntegratedLauncher"){
        sh "./autogen"
        sh "make"
        sh "mv -f UlteoOVDIntegratedLauncher ADSIntegratedLauncher"
        //archiveArtifacts 'ADSIntegratedLauncher'
    }
    
   dir("client/java/jars") {
   parallel (
     "Linux64" : {
       sh "java -jar packr.jar --platform linux64 --jdk openjdk-1.7.0-u80-unofficial-linux-amd64-installer.zip --executable ADSNativeClient --classpath OVDNativeClient.jar --mainclass org.ulteo.ovd.client.NativeClient --output ADSNativeClient_linux64"
       sh "cp -r ../../OVDIntegratedLauncher/ADSIntegratedLauncher ."
       sh "zip -r ADSNativeClient_linux64.zip ADSNativeClient_linux64"
     },
     "Linux32" : {
       sh "java -jar packr.jar --platform linux32 --jdk openjdk-1.7.0-u80-unofficial-linux-i586-image.zip --executable ADSNativeClient --classpath OVDNativeClient.jar --mainclass org.ulteo.ovd.client.NativeClient --output ADSNativeClient_linux32"
       sh "cp -r ../../OVDIntegratedLauncher/ADSIntegratedLauncher ."
       sh "zip -r ADSNativeClient_linux32.zip ADSNativeClient_linux32"

       },
     "Windows" : {
       sh "java -jar packr.jar --platform windows32 --jdk openjdk-1.7.0-u80-unofficial-windows-i586-image.zip --executable ADSNativeClient --classpath OVDNativeClient.jar --mainclass org.ulteo.ovd.client.NativeClient --output ADSNativeClient_Windows"
       sh "cp -r ../windlls.zip ADSNativeClient_Windows"
       dir("ADSNativeClient_Windows") {
         sh "cp -r ../../../../ADSNativeClient.BAT ."
         sh "cp -r ../../../../invisible.vbs ."
         sh "unzip windlls.zip && rm -rf windlls.zip"
       }
       sh "rm -rf ADSNativeClient_Windows/{jre,ADSNativeClient.exe,config.json}"
       sh "zip -r ADSNativeClient_Windows.zip ADSNativeClient_Windows"
       },
     "Mac" : {
       sh "java -jar packr.jar --platform mac --jdk openjdk-1.7.0-u80-unofficial-macosx-x86_64-image.zip --executable ADSNativeClient --classpath OVDNativeClient.jar --mainclass org.ulteo.ovd.client.NativeClient --output ADSNativeClient_mac.app"
       sh "zip -r ADSNativeClient_mac.zip ADSNativeClient_mac.app"

     }
   )
   }
   /* dir("client/java/jars") {
       archiveArtifacts 'ADSNativeClient_*.zip'
   }*/
   stage("Installers & Package") {
   dir("client/java/jars") {
   parallel (
     "Windows Installer" : {
       sh "msi-packager ADSNativeClient_Windows/ ADSNativeClient_Installer.msi -n  \"MAN Application Delivery System\" -v 2.1 -m \"MAN CONSULTING LTD\" -a x86 -u 34 -i ../icons/icon.ico -e invisible.vbs"    
}
   )
   archiveArtifacts '*.msi'
   stash allowEmpty: true, name: 'ADSNativeClient_Installer.msi', useDefaultExcludes: false
   }

   }

    

  }
}
node("master") {
   deleteDir()
   unstash 'ADSNativeClient_Installer.msi'
   sh "curl -v -i -X POST -H \"Content-Type:application/json\" -H \"Authorization: token ${github_token}\" https://api.github.com/repos/bacgroup/man-ads-client/releases -d '{\"tag_name\":\"man-ads-client_${BUILD_NUMBER}\",\"target_commitish\": \"${BRANCH_NAME}\",\"name\": \"MAN ADS Client Build ${BUILD_NUMBER}\",\"body\": \"MAN Consulting Software\",\"draft\": false,\"prerelease\": true}'"
   sh "for i in *.msi; do bash $HOME/github-release.sh github_api_token=${github_token} owner=bacgroup repo=man-ads-client tag=man-ads-client_${BUILD_NUMBER} filename=./\$i; done"
}
