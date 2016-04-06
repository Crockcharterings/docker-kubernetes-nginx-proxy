import operator
import os

from bunch import Bunch
from jinja2 import Environment, FileSystemLoader
from pykube.config import KubeConfig
from pykube.http import HTTPClient
from pykube.objects import Service

def render(data):
  dir = os.path.dirname(__file__)
  env = Environment(loader=FileSystemLoader(os.path.join(dir, 'templates')), lstrip_blocks=True)
  template = env.get_template('nginx.tmpl')
  return template.render(services=data)

def str2bool(str):
  if str in ['true', 'True']:
    return True
  return False

def parse_service(service):
  data = Bunch(service.annotations)
  data.ip = service.obj['spec']['clusterIP']
  data.proxy_web_socket = str2bool(data.proxy_web_socket)
  data.proxy_http = str2bool(data.proxy_http)
  data.proxy_https = str2bool(data.proxy_https)
  data.proxy_https_redirect = str2bool(data.proxy_https_redirect)
  data.port = service.obj['spec']['ports'][0]['port']
  return data

if __name__ == "__main__":
  config = KubeConfig.from_service_account()
  api = HTTPClient(config)

  services = Service.objects(api) \
                  .filter(namespace='default', selector={'proxied': 'true'})

  data = []
  for service in services:
    data.append(parse_service(service))

  result = render(data)

  with open('/etc/nginx/nginx.conf', 'w') as file:
    file.write(result)

