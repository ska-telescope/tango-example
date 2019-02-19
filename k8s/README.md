
Tango Example on Kubernetes
===========================

The following are a set of instructions of running the Tango examples on Kubernetes, and has been tested  on minikube v0.34.1 with k8s v1.13.3 on Ubuntu 18.04.

Minikube
========

Using [Minikube](https://kubernetes.io/docs/getting-started-guides/minikube/) enables us to create a single node stand alone Kubernetes cluster for testing purposes.  If you already have a cluster at your disposal, then you can skip forward to 'Running the Tango Examples on Kubernetes'.

The generic installation instructions are available at https://kubernetes.io/docs/tasks/tools/install-minikube/.

Minikube requires the Kubernetes runtime, and a host virtualisation layer such as kvm, virtualbox etc.  Please refer to the drivers list at https://github.com/kubernetes/minikube/blob/master/docs/drivers.md .

On Ubuntu 18.04 for desktop based development, the most straight forward installation pattern is to go with the `none` driver as the host virtualisation layer.  CAUTION:  this will install Kubernetes directly on your host and will destroy any existing Kubernetes related configuration you already have (eg: /etc/kubernetes, /var/lib/kubelet, /etc/cni, ...).    This is technically called 'running with scissors', but the trade off in the authors opinion is lower virtualisation overheads and simpler management of storage integration including Xauthority details etc.

The latest version of minikube is found here  https://github.com/kubernetes/minikube/releases .  Scroll down to the section for Linux, which will have instructions like:
```
curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.34.1/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
```

Now we need to bootstrap minikube so that we have a running cluster based on kvm:
```
sudo -E minikube start --vm-driver=none --extra-config=kubelet.resolv-conf=/var/run/systemd/resolve/resolv.conf
```
This will take some time setting up the vm, and bootstrapping Kubernetes.  You will see output like the following when done.
```
$ sudo -E minikube start --vm-driver=none --extra-config=kubelet.resolv-conf=/var/run/systemd/resolve/resolv.conf
😄  minikube v0.34.1 on linux (amd64)
🤹  Configuring local host environment ...

⚠️  The 'none' driver provides limited isolation and may reduce system security and reliability.
⚠️  For more information, see:
👉  https://github.com/kubernetes/minikube/blob/master/docs/vmdriver-none.md

⚠️  kubectl and minikube configuration will be stored in /home/piers
⚠️  To use kubectl or minikube commands as your own user, you may
⚠️  need to relocate them. For example, to overwrite your own settings:

    ▪ sudo mv /home/piers/.kube /home/piers/.minikube $HOME
    ▪ sudo chown -R $USER /home/piers/.kube /home/piers/.minikube

💡  This can also be done automatically by setting the env var CHANGE_MINIKUBE_NONE_USER=true
🔥  Creating none VM (CPUs=2, Memory=2048MB, Disk=20000MB) ...
📶  "minikube" IP address is 192.168.86.29
🐳  Configuring Docker as the container runtime ...
✨  Preparing Kubernetes environment ...
    ▪ kubelet.resolv-conf=/var/run/systemd/resolve/resolv.conf
🚜  Pulling images required by Kubernetes v1.13.3 ...
🚀  Launching Kubernetes v1.13.3 using kubeadm ... 
🔑  Configuring cluster permissions ...
🤔  Verifying component health .....
💗  kubectl is now configured to use "minikube"
🏄  Done! Thank you for using minikube!
```
The `--extra-config=kubelet.resolv-conf=/var/run/systemd/resolve/resolv.conf` flag is to deal with the coredns and loopback problems - you may not need this depending on your local setup.

Now fixup your permissions:
```
sudo chown -R ${USER} /home/${USER}/.minikube
sudo chgrp -R ${USER} /home/${USER}/.minikube
sudo chown -R ${USER} /home/${USER}/.kube
sudo chgrp -R ${USER} /home/${USER}/.kube
```

Once completed, minikube will also update your kubectl settings to include the context `current-context: minikube` in `~/.kube/config`.  Test that connectivity works with something like:
```
$ kubectl get pods -n kube-system
NAME                               READY   STATUS    RESTARTS   AGE
coredns-86c58d9df4-5ztg8           1/1     Running   0          3m24s
...


Helm Chart
----------

The Helm Chart based install of the Tango Examples relies on [Helm](https://docs.helm.sh/using_helm/#installing-helm) (surprise!).  The easiest way is using the install script:
```
https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash
```

Cleaning Up
-----------

Note on cleaning up:
```
minikube stop # stop minikube - this can be restarted with minikube start
minikube delete # destroy minikube - totally gone!
rm -rf ~/.kube # local minikube configuration cache
# remove all other minikube related installation files
sudo rm -rf /var/lib/kubeadm.yaml /data/minikube /var/lib/minikube /var/lib/kubelet /etc/kubernetes
```

Running the Tango Examples on Kubernetes
----------------------------------------

Once Helm is up and running (from above), change to the k8s/ directory.  The basic configuration for each component of the Tango Example is held in the `values.yaml` file.

Firstly, we need to initialise Helm (the Tiller component) in the namespace that we wish to use:

```
$ make launch-tiller KUBE_NAMESPACE=test
kubectl describe namespace test || kubectl create namespace test
Error from server (NotFound): namespaces "test" not found
namespace/test created
KUBE_NAMESPACE=test \
 envsubst < tiller-acls.yml | kubectl apply -n test -f -
serviceaccount/tiller created
clusterrolebinding.rbac.authorization.k8s.io/tiller created
helm init --service-account tiller \
  --tiller-namespace test \
  --upgrade
$HELM_HOME has been configured at /home/piers/.helm.

Tiller (the Helm server-side component) has been installed into your Kubernetes Cluster.

Please note: by default, Tiller is deployed with an insecure 'allow unauthenticated users' policy.
To prevent this, run `helm init` with the --tiller-tls-verify flag.
For more information on securing your installation see: https://docs.helm.sh/using_helm/#securing-your-helm-installation
Happy Helming!

```

Check that Helm is running happily with:
```
$ kubectl get deployment -n test
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
tiller-deploy   1/1     1            1           50s
```

Now for the main event - we launch the Tango Example with:
```
$ make deploy KUBE_NAMESPACE=test
```

This will give extensive output describing what has been deployed in the test namespace:
```
NAME:   test
LAST DEPLOYED: Tue Feb 19 17:42:07 2019
NAMESPACE: test
STATUS: DEPLOYED

RESOURCES:
==> v1/Pod(related)
NAME                             READY  STATUS   RESTARTS  AGE
databaseds-ska-tango-examples-0  1/1    Running  0         4s
tangodb-ska-tango-examples-0     1/1    Running  0         4s

==> v1/PersistentVolume
NAME                        CAPACITY  ACCESS MODES  RECLAIM POLICY  STATUS  CLAIM                            STORAGECLASS  REASON  AGE
pogo-ska-tango-examples     1Gi       RWO           Retain          Bound   test/tangodb-ska-tango-examples  standard      4s
tangodb-ska-tango-examples  1Gi       RWO           Retain          Bound   test/pogo-ska-tango-examples     standard      4s

==> v1/PersistentVolumeClaim
NAME                        STATUS  VOLUME                      CAPACITY  ACCESS MODES  STORAGECLASS  AGE
pogo-ska-tango-examples     Bound   tangodb-ska-tango-examples  1Gi       RWO           standard      4s
tangodb-ska-tango-examples  Bound   pogo-ska-tango-examples     1Gi       RWO           standard      4s

==> v1/Service
NAME                              TYPE       CLUSTER-IP      EXTERNAL-IP  PORT(S)          AGE
databaseds-ska-tango-examples     ClusterIP  None            <none>       10000/TCP        4s
tango-example-ska-tango-examples  NodePort   10.110.178.141  <none>       32678:32678/TCP  4s
tangodb-ska-tango-examples        ClusterIP  None            <none>       3306/TCP         4s

==> v1/Pod
NAME                              READY  STATUS   RESTARTS  AGE
astor-ska-tango-examples          1/1    Running  0         4s
tango-example-ska-tango-examples  1/1    Running  0         4s

==> v1/StatefulSet
NAME                           DESIRED  CURRENT  AGE
databaseds-ska-tango-examples  1        1        4s
tangodb-ska-tango-examples     1        1        4s
```

Please wait patiently - it will take time for the Container images to download, and for the database to initialise.  After some time, you can check what is running with:
```
watch kubectl get all,pv,pvc -n test
```

Which will give output like:
```
Every 2.0s: kubectl get all,pv,pvc -n test                                                                                            dragon: Tue Feb 19 17:46:49 2019

NAME                                   READY   STATUS    RESTARTS   AGE
pod/astor-ska-tango-examples           1/1     Running   2          4m42s
pod/databaseds-ska-tango-examples-0    1/1     Running   3          4m42s
pod/tango-example-ska-tango-examples   1/1     Running   4          4m42s
pod/tangodb-ska-tango-examples-0       1/1     Running   0          4m42s
pod/tiller-deploy-7c4f7db874-ppzz8     1/1     Running   0          11m

NAME                                       TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)           AGE
service/databaseds-ska-tango-examples      ClusterIP   None             <none>        10000/TCP         4m42s
service/tango-example-ska-tango-examples   NodePort    10.110.178.141   <none>        32678:32678/TCP   4m42s
service/tangodb-ska-tango-examples         ClusterIP   None             <none>        3306/TCP          4m42s
service/tiller-deploy                      ClusterIP   10.109.201.50    <none>        44134/TCP         11m

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/tiller-deploy   1/1     1            1           11m

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/tiller-deploy-7c4f7db874   1         1         1       11m

NAME                                             READY   AGE
statefulset.apps/databaseds-ska-tango-examples   1/1     4m42s
statefulset.apps/tangodb-ska-tango-examples      1/1     4m42s

NAME                                          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                             STORAGECLASS   REASON   AGE
persistentvolume/pogo-ska-tango-examples      1Gi        RWO            Retain           Bound    test/tangodb-ska-tango-examples   standard                4m42s
persistentvolume/tangodb-ska-tango-examples   1Gi        RWO            Retain           Bound    test/pogo-ska-tango-examples      standard                4m42s

NAME                                               STATUS   VOLUME                       CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/pogo-ska-tango-examples      Bound    tangodb-ska-tango-examples   1Gi        RWO            standard       4m42s
persistentvolumeclaim/tangodb-ska-tango-examples   Bound    pogo-ska-tango-examples      1Gi        RWO            standard       4m42s

```

If everything goes according to plan, then the Tango Control System GUI will spring into life, and you will be able to navigate to the `PowerSupply` agent to verify that the Tango Example is up an running.

To clean up the Helm Chart release:
```
$make delete KUBE_NAMESPACE=test
```

Debugging with VSCode
---------------------

It is also possible to invoke the python debugger - `ptvsd`.  This is done by passing the DEBUG flag:
```
$ make deploy KUBE_NAMESPACE=test REMOTE_DEBUG=true
```

This will kick off the tango-example with the debugger listening on port 32678, which is bound to a k8s Service NodePort of 32678.  To attach to the debugger, add an entry to launch.json  like the following, and execute:
```
...
        {
            "name": "Python: Remote 32678",
            "type": "python",
            "request": "attach",
            "port": 32678,
            "host": "0.0.0.0",
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ]
        },
...
```
