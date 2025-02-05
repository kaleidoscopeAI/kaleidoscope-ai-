security_deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {
                'name': 'security-system',
                'namespace': self.namespace
            },
            'spec': {
                'serviceName': 'security-system',
                'replicas': self.replicas,
                'selector': {
                    'matchLabels': {
                        'app': 'security-system'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'security-system'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'security',
                            'image': 'security-system:latest',
                            'resources': {
                                'limits': {
                                    'nvidia.com/gpu': '1' if self.gpu_enabled else '0'
                                },
                                'requests': {
                                    'memory': '4Gi',
                                    'cpu': '2'
                                }
                            },
                            'env': [{
                                'name': 'REDIS_HOST',
                                'value': 'redis-security'
                            }],
                            'volumeMounts': [{
                                'name': 'security-storage',
                                'mountPath': '/data'
                            }]
                        }],
                        'volumes': [{
                            'name': 'security-storage',
                            'persistentVolumeClaim': {
                                'claimName': 'security-storage'
                            }
                        }]
                    }
                },
                'volumeClaimTemplates': [{
                    'metadata': {
                        'name': 'security-storage'
                    },
                    'spec': {
                        'accessModes': ['ReadWriteOnce'],
                        'resources': {
                            'requests': {
                                'storage': '100Gi'
                            }
                        }
                    }
                }]
            }
        }

        redis_deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'redis-security',
                'namespace': self.namespace
            },
            'spec': {
                'replicas': 1,
                'selector': {
                    'matchLabels': {
                        'app': 'redis-security'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'redis-security'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'redis',
                            'image': 'redis:latest',
                            'ports': [{
                                'containerPort': 6379
                            }],
                            'volumeMounts': [{
                                'name': 'redis-data',
                                'mountPath': '/data'
                            }]
                        }],
                        'volumes': [{
                            'name': 'redis-data',
                            'persistentVolumeClaim': {
                                'claimName': 'redis-security-data'
                            }
                        }]
                    }
                }
            }
        }

        self.k8s_apps.create_namespaced_stateful_set(
            namespace=self.namespace,
            body=security_deployment
        )
        self.k8s_apps.create_namespaced_deployment(
            namespace=self.namespace,
            body=redis_deployment
        )

    def _deploy_model_servers(self):
        model_deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {
                'name': 'model-server',
                'namespace': self.namespace
            },
            'spec': {
                'serviceName': 'model-server',
                'replicas': self.replicas,
                'selector': {
                    'matchLabels': {
                        'app': 'model-server'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'model-server'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'model',
                            'image': 'model-server:latest',
                            'resources': {
                                'limits': {
                                    'nvidia.com/gpu': '1' if self.gpu_enabled else '0'
                                },
                                'requests': {
                                    'memory': '8Gi',
                                    'cpu': '4'
                                }
                            },
                            'env': [{
                                'name': 'MODEL_PATH',
                                'value': '/models'
                            }],
                            'volumeMounts': [{
                                'name': 'model-storage',
                                'mountPath': '/models'
                            }]
                        }],
                        'volumes': [{
                            'name': 'model-storage',
                            'persistentVolumeClaim': {
                                'claimName': 'model-storage'
                            }
                        }]
                    }
                },
                'volumeClaimTemplates': [{
                    'metadata': {
                        'name': 'model-storage'
                    },
                    'spec': {
                        'accessModes': ['ReadWriteOnce'],
                        'resources': {
                            'requests': {
                                'storage': '100Gi'
                            }
                        }
                    }
                }]
            }
        }

        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'model-server',
                'namespace': self.namespace
            },
            'spec': {
                'selector': {
                    'app': 'model-server'
                },
                'ports': [{
                    'protocol': 'TCP',
                    'port': 8000,
                    'targetPort': 8000
                }],
                'type': 'LoadBalancer'
            }
        }

        self.k8s_apps.create_namespaced_stateful_set(
            namespace=self.namespace,
            body=model_deployment
        )
        self.k8s_core.create_namespaced_service(
            namespace=self.namespace,
            body=service
        )

    def _deploy_api_gateway(self):
        gateway_deployment = {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'api-gateway',
                'namespace': self.namespace
            },
            'spec': {
                'replicas': self.replicas,
                'selector': {
                    'matchLabels': {
                        'app': 'api-gateway'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'api-gateway'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'gateway',
                            'image': 'api-gateway:latest',
                            'ports': [{
                                'containerPort': 8080
                            }],
                            'env': [{
                                'name': 'MODEL_SERVICE',
                                'value': 'model-server:8000'
                            }, {
                                'name': 'SECURITY_SERVICE',
                                'value': 'security-system:8000'
                            }],
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 15,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }

        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'api-gateway',
                'namespace': self.namespace
            },
            'spec': {
                'selector': {
                    'app': 'api-gateway'
                },
                'ports': [{
                    'protocol': 'TCP',
                    'port': 80,
                    'targetPort': 8080
                }],
                'type': 'LoadBalancer'
            }
        }

        self.k8s_apps.create_namespaced_deployment(
            namespace=self.namespace,
            body=gateway_deployment
        )
        self.k8s_core.create_namespaced_service(
            namespace=self.namespace,
            body=service
        )

    def _setup_autoscaling(self):
        hpa_model = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'model-server-hpa',
                'namespace': self.namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'StatefulSet',
                    'name': 'model-server'
                },
                'minReplicas': 1,
                'maxReplicas': 10,
                'metrics': [{
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 70
                        }
                    }
                }]
            }
        }

        hpa_security = {
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': 'security-system-hpa',
                'namespace': self.namespace
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'StatefulSet',
                    'name': 'security-system'
                },
                'minReplicas': 1,
                'maxReplicas': 5,
                'metrics': [{
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': 70
                        }
                    }
                }]
            }
        }

        self.k8s_client.create_namespaced_horizontal_pod_autoscaler(
            namespace=self.namespace,
            body=hpa_model
        )
        self.k8s_client.create_namespaced_horizontal_pod_autoscaler(
            namespace=self.namespace,
            body=hpa_security
        )

@serve.deployment(
    num_replicas=3,
    ray_actor_options={"num_gpus": 1}
)
class ModelServingEndpoint:
    def __init__(self, model: nn.Module, security_system: IntegratedSecuritySystem):
        self.model = model
        self.security_system = security_system
        self.request_counter = prom.Counter(
            'model_requests_total',
            'Total model inference requests'
        )
        self.processing_time = prom.Histogram(
            'model_processing_seconds',
            'Time spent on model inference'
        )

    async def __call__(self, request):
        self.request_counter.inc()
        with self.processing_time.time():
            data = await request.json()
            
            market_tensor = torch.tensor(data['market_data']).cuda()
            molecule_tensor = torch.tensor(data['molecule_data']).cuda()
            sensor_tensor = torch.tensor(data['sensor_data']).cuda()
            
            security_status = self.security_system.process_data(
                market_tensor, molecule_tensor, sensor_tensor
            )
            
            if security_status['threat_level'] < 2:
                with torch.no_grad():
                    market_pred, molecule_pred, sensor_pred, uncertainties = \
                        self.model(market_tensor, molecule_tensor, sensor_tensor)
                    
                    return {
                        'market_predictions': market_pred.cpu().numpy().tolist(),
                        'molecule_predictions': molecule_pred.cpu().numpy().tolist(),
                        'sensor_predictions': sensor_pred.cpu().numpy().tolist(),
                        'uncertainties': uncertainties.cpu().numpy().tolist(),
                        'security_status': security_status
                    }
            else:
                return {'error': 'Security check failed', 'status': security_status}

app = FastAPI()
deployment_manager = DeploymentManager()

@app.on_event("startup")
async def startup():
    await deployment_manager.deploy()

@app.post("/predict")
async def predict(data: Dict, background_tasks: BackgroundTasks):
    handle = serve.get_deployment("ModelServingEndpoint").get_handle()
    return await handle.remote(data)

@app.get("/metrics")
async def metrics():
    return prom.generate_latest()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
