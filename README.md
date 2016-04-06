# docker-kubernetes-nginx-proxy

Kubernetes automatic service proxy based on annotations. It uses the Kubernetes API to query the services.

 * Docker Hub URL: https://hub.docker.com/r/robertdolca/kubernetes-nginx-proxy/
 * Image name: `robertdolca/kubernetes-nginx-proxy`

It gets all the services using this selector `proxied=true`. It configures the proxy based on the following annotation:


```
# Domain name used for the virtual host
proxy_host: example.com

# Path to proxy
proxy_path: /

# This flag enables web sockets
proxy_web_socket: 'false'

# Enable http proxy
proxy_http: 'true'

# Enable https proxy and certificate configuration
proxy_https: 'true'
proxy_ssl_cert: example.com/fullchain.pem
proxy_ssl_key: example.com/privkey.pem

# Redirect http to https
proxy_https_redirect: 'true'
```

The service's cluster IP and port are automatically detected. If the service has multiple ports it will use the first one.

The proxy expects the certificates to be present at `/etc/nginx/ssl`. You can use a persistent volume, config map or a secret mounted with the volumes plugin.

## Sample configuration

Service that needs to be proxies

```
apiVersion: v1
kind: Service
metadata:
  name: jenkins
  labels:
    run: jenkins
    proxied: 'true'
  annotations:
    proxy_host: example.com
    proxy_path: /
    proxy_web_socket: 'false'
    proxy_http: 'true'
    proxy_https: 'true'
    proxy_https_redirect: 'true'
    proxy_ssl_cert: example.com/fullchain.pem
    proxy_ssl_key: example.com/privkey.pem
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 8080
      name: http
  selector:
    run: jenkins
```

Proxy pod and replication controller

```
apiVersion: v1
kind: ReplicationController
metadata:
  name: proxy
  labels:
    run: proxy
spec:
  replicas: 1
  selector:
    run: proxy
  template:
    metadata:
      name: proxy
      labels:
        run: proxy
    spec:
      containers:
        - image: robertdolca/kubernetes-nginx-proxy
          name: proxy
          ports:
            - containerPort: 80
              name: http
            - containerPort: 443
              name: https
          volumeMounts:
            - name: example-com
              mountPath: /etc/nginx/ssl/example.com
              readOnly: true
      volumes:
        - name: example-com
          configMap:
            name: example-com
```

Config map to store the certificates

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-com
data:
  fullchain.pem: |-
    -----BEGIN CERTIFICATE-----
    abc
    -----END CERTIFICATE-----
  privkey.pem: |-
    -----BEGIN PRIVATE KEY-----
    abc
    -----END PRIVATE KEY-----
```

Proxy service

```
apiVersion: v1
kind: Service
metadata:
  name: proxy
  labels:
    run: proxy
spec:
  type: LoadBalancer
  ports:
    - port: 80
      name: http
    - port: 443
      name: https
  selector:
    run: proxy
```

## TODO

 * Create a new configuration and reload nginx when services' configuration change
 * Gracefully ignore services that are not correctly annotated
 * Add an annotation to specify which port to use if the service being proxied exposes more than one (using named ports).

## Credits

 This project was inspired by [fbrbovic/kubernetes-reverseproxy](https://github.com/fbrbovic/kubernetes-reverseproxy).
