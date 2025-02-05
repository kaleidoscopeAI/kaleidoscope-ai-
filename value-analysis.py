import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import time
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ResourceMetrics:
    cpu_utilization: float
    memory_usage: float
    network_bandwidth: float
    storage_iops: float

@dataclass
class CostMetrics:
    infrastructure_cost: float
    operational_cost: float
    maintenance_cost: float
    incident_cost: float

class ValueAnalyzer:
    def __init__(self, node_count: int):
        self.node_count = node_count
        self.baseline_costs = self._calculate_baseline_costs()
        self.optimized_costs = None
        self.resource_savings = None
        
    def _calculate_baseline_costs(self) -> CostMetrics:
        # Traditional infrastructure costs
        infra_cost = self.node_count * 1000  # $1000 per node/month
        ops_cost = self.node_count * 200     # $200 per node/month ops
        maintenance = self.node_count * 150   # $150 per node/month maintenance
        incident = self.node_count * 300      # $300 per node/month incidents
        
        return CostMetrics(
            infrastructure_cost=infra_cost,
            operational_cost=ops_cost,
            maintenance_cost=maintenance,
            incident_cost=incident
        )
    
    def analyze_optimized_system(self, workload_data: List[Dict]) -> Tuple[float, Dict]:
        resource_metrics = self._measure_resource_usage(workload_data)
        self.optimized_costs = self._calculate_optimized_costs(resource_metrics)
        self.resource_savings = self._calculate_resource_savings(resource_metrics)
        
        roi = self._calculate_roi()
        savings_breakdown = self._generate_savings_breakdown()
        
        return roi, savings_breakdown
    
    def _measure_resource_usage(self, workload_data: List[Dict]) -> ResourceMetrics:
        with ThreadPoolExecutor(max_workers=self.node_count) as executor:
            futures = []
            for workload in workload_data:
                futures.append(executor.submit(self._process_workload, workload))
            
            results = [future.result() for future in futures]
        
        return ResourceMetrics(
            cpu_utilization=np.mean([r.cpu_utilization for r in results]),
            memory_usage=np.mean([r.memory_usage for r in results]),
            network_bandwidth=np.mean([r.network_bandwidth for r in results]),
            storage_iops=np.mean([r.storage_iops for r in results])
        )
    
    def _process_workload(self, workload: Dict) -> ResourceMetrics:
        # Simulate workload processing and measure resource usage
        cpu_usage = workload['complexity'] * 0.7 + np.random.uniform(0, 0.3)
        memory_usage = workload['data_size'] / 1000 + np.random.uniform(0, 0.2)
        network_usage = workload['throughput'] * 0.8 + np.random.uniform(0, 0.2)
        storage_usage = workload['io_ops'] * 0.9 + np.random.uniform(0, 0.1)
        
        return ResourceMetrics(
            cpu_utilization=min(cpu_usage, 1.0),
            memory_usage=min(memory_usage, 1.0),
            network_bandwidth=min(network_usage, 1.0),
            storage_iops=min(storage_usage, 1.0)
        )
    
    def _calculate_optimized_costs(self, metrics: ResourceMetrics) -> CostMetrics:
        # Calculate costs with system optimization
        efficiency_factor = np.mean([
            metrics.cpu_utilization,
            metrics.memory_usage,
            metrics.network_bandwidth,
            metrics.storage_iops
        ])
        
        # Optimized node count based on resource efficiency
        optimized_nodes = int(self.node_count * (0.6 + efficiency_factor * 0.4))
        
        return CostMetrics(
            infrastructure_cost=optimized_nodes * 800,  # 20% infrastructure savings
            operational_cost=optimized_nodes * 120,     # 40% operational savings
            maintenance_cost=optimized_nodes * 100,     # 33% maintenance savings
            incident_cost=optimized_nodes * 150         # 50% incident reduction
        )
    
    def _calculate_resource_savings(self, metrics: ResourceMetrics) -> Dict:
        return {
            'cpu_savings': (1 - metrics.cpu_utilization) * 100,
            'memory_savings': (1 - metrics.memory_usage) * 100,
            'network_savings': (1 - metrics.network_bandwidth) * 100,
            'storage_savings': (1 - metrics.storage_iops) * 100
        }
    
    def _calculate_roi(self) -> float:
        total_baseline = sum([
            self.baseline_costs.infrastructure_cost,
            self.baseline_costs.operational_cost,
            self.baseline_costs.maintenance_cost,
            self.baseline_costs.incident_cost
        ])
        
        total_optimized = sum([
            self.optimized_costs.infrastructure_cost,
            self.optimized_costs.operational_cost,
            self.optimized_costs.maintenance_cost,
            self.optimized_costs.incident_cost
        ])
        
        implementation_cost = self.node_count * 500  # One-time cost per node
        monthly_savings = total_baseline - total_optimized
        
        # Calculate 12-month ROI
        annual_savings = monthly_savings * 12
        roi = ((annual_savings - implementation_cost) / implementation_cost) * 100
        
        return roi
    
    def _generate_savings_breakdown(self) -> Dict:
        return {
            'monthly_savings': {
                'infrastructure': self.baseline_costs.infrastructure_cost - self.optimized_costs.infrastructure_cost,
                'operational': self.baseline_costs.operational_cost - self.optimized_costs.operational_cost,
                'maintenance': self.baseline_costs.maintenance_cost - self.optimized_costs.maintenance_cost,
                'incident': self.baseline_costs.incident_cost - self.optimized_costs.incident_cost
            },
            'resource_utilization': self.resource_savings,
            'node_reduction': self.node_count - int(self.node_count * 0.6)
        }

def main():
    # Example usage with 100 nodes
    analyzer = ValueAnalyzer(100)
    
    # Generate sample workload data
    workload_data = [
        {
            'complexity': np.random.uniform(0.4, 0.9),
            'data_size': np.random.uniform(100, 1000),
            'throughput': np.random.uniform(0.3, 0.8),
            'io_ops': np.random.uniform(0.2, 0.7)
        }
        for _ in range(1000)  # 1000 workload samples
    ]
    
    # Calculate ROI and savings
    roi, savings = analyzer.analyze_optimized_system(workload_data)
    
    print(f"12-Month ROI: {roi:.2f}%")
    print("\nMonthly Savings Breakdown:")
    for category, amount in savings['monthly_savings'].items():
        print(f"{category.title()}: ${amount:,.2f}")
    
    print("\nResource Utilization Improvements:")
    for resource, saving in savings['resource_utilization'].items():
        print(f"{resource.replace('_', ' ').title()}: {saving:.1f}%")
    
    print(f"\nNode Count Reduction: {savings['node_reduction']} nodes")

if __name__ == "__main__":
    main()
