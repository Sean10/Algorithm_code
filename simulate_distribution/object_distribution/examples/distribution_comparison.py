import matplotlib.pyplot as plt
from object_distribution.simulators import (
    HashSimulator,
    DHTSimulator,
    DynamoSimulator,
    TieredCopysetSimulator,
    CrushSimulator
)

def run_comparison(num_objects=100000, num_nodes=100):
    simulators = {
        'Hash': HashSimulator(num_objects, num_nodes),
        'DHT': DHTSimulator(num_objects, num_nodes),
        'Dynamo': DynamoSimulator(num_objects, num_nodes),
        'TieredCopyset': TieredCopysetSimulator(num_objects, num_nodes),
        'CRUSH': CrushSimulator(num_objects, num_nodes)
    }

    distributions = ['normal', 'zipf']
    
    for dist_type in distributions:
        print(f"\nProcessing {dist_type} distribution...")
        
        results = {}
        for name, simulator in simulators.items():
            print(f"Running {name} simulation...")
            results[name] = simulator.simulate(dist_type)
            
        plot_results(results, dist_type)
        analyze_results(results, dist_type)

if __name__ == '__main__':
    run_comparison() 