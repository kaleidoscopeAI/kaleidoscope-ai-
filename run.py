# run.py

import click
import logging
from pathlib import Path
from core.engine import KaleidoscopeEngine
from analysis.molecular.structure_analyzer import StructureAnalyzer
from analysis.biological.pathway_analyzer import PathwayAnalyzer

@click.group()
def cli():
    """Kaleidoscope AI System - Command Line Interface"""
    pass

@cli.command()
@click.option('--port', default=5000, help='Port for the web interface')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def serve(port, debug):
    """Start the web interface"""
    from main import main
    click.echo(f"Starting Kaleidoscope AI System on port {port}...")
    main()

@cli.command()
@click.argument('input_file')
@click.option('--type', type=click.Choice(['molecular', 'pathway', 'discovery']), 
              required=True, help='Type of analysis to perform')
@click.option('--output', default='results', help='Output directory for results')
def analyze(input_file, type, output):
    """Analyze input data"""
    try:
        # Initialize engine
        engine = KaleidoscopeEngine()
        
        # Create output directory
        output_path = Path(output)
        output_path.mkdir(exist_ok=True)
        
        click.echo(f"Analyzing {input_file}...")
        
        if type == 'molecular':
            analyzer = StructureAnalyzer()
            results = analyzer.analyze_file(input_file)
        elif type == 'pathway':
            analyzer = PathwayAnalyzer()
            results = analyzer.analyze_file(input_file)
        else:
            results = engine.analyze_data(input_file)
            
        # Save results
        result_path = output_path / f"{Path(input_file).stem}_results.json"
        with open(result_path, 'w') as f:
            import json
            json.dump(results, f, indent=2)
            
        click.echo(f"Results saved to {result_path}")
        
    except Exception as e:
        click.echo(f"Error during analysis: {str(e)}", err=True)

@cli.command()
def status():
    """Check system status"""
    try:
        engine = KaleidoscopeEngine()
        status = engine.get_status()
        
        click.echo("\nKaleidoscope AI System Status:")
        click.echo("-" * 30)
        for key, value in status.items():
            click.echo(f"{key}: {value}")
            
    except Exception as e:
        click.echo(f"Error getting status: {str(e)}", err=True)

@cli.command()
@click.option('--clear-cache', is_flag=True, help='Clear system cache')
@click.option('--reset-nodes', is_flag=True, help='Reset all nodes')
def cleanup(clear_cache, reset_nodes):
    """Cleanup system resources"""
    try:
        engine = KaleidoscopeEngine()
        
        if clear_cache:
            engine.clear_cache()
            click.echo("Cache cleared")
            
        if reset_nodes:
            engine.reset_nodes()
            click.echo("Nodes reset")
            
        click.echo("Cleanup complete")
        
    except Exception as e:
        click.echo(f"Error during cleanup: {str(e)}", err=True)

@cli.command()
@click.option('--type', type=click.Choice(['unit', 'integration', 'all']), 
              default='all', help='Type of tests to run')
def test(type):
    """Run system tests"""
    import pytest
    
    if type == 'unit':
        pytest.main(['tests/unit'])
    elif type == 'integration':
        pytest.main(['tests/integration'])
    else:
        pytest.main(['tests'])

if __name__ == '__main__':
    cli()
