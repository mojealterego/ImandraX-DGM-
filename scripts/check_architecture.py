"""Static dependency closure: every module assigned, acyclic imports, offline core."""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path


def check(root: Path) -> dict:
    policy = json.loads((root/'architecture/boundaries.json').read_text())
    errors, layers = [], {}
    for layer, names in policy['layers'].items():
        for name in names:
            if name in layers:
                errors.append(f'duplicate module: {name}')
            layers[name] = layer
    sources = {p.stem: p for p in (root/'src/imandrax_dgm').glob('*.py')}
    for name in sorted(set(sources) ^ set(layers)):
        errors.append(f'unclassified or missing module: {name}')
    graph = {name: set() for name in sources}
    for name, path in sources.items():
        layer = layers.get(name)
        if layer is None:
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            imported, local = [], []
            if isinstance(node, ast.Import):
                imported = [a.name for a in node.names]
                local = [a.name.split('.')[1] for a in node.names
                         if a.name.startswith('imandrax_dgm.')]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    local = [node.module.split('.')[0]] if node.module else [a.name for a in node.names]
                elif node.module == 'imandrax_dgm':
                    local = [a.name for a in node.names]
                elif node.module and node.module.startswith('imandrax_dgm.'):
                    local = [node.module.split('.')[1]]
                elif node.module:
                    imported = [node.module]
            for dependency in local:
                graph[name].add(dependency)
                if layers.get(dependency) not in policy['allowed_dependencies'][layer]:
                    errors.append(f'forbidden dependency: {name} -> {dependency}')
            if layer != 'adapter':
                for dependency in imported:
                    if dependency.split('.')[0] in policy['forbidden_core_imports']:
                        errors.append(f'nonportable core import: {name} -> {dependency}')
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ('eval', 'exec', '__import__'):
                        errors.append(f'dynamic core execution: {name}')
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'os' and (node.func.attr in ('system', 'popen', 'fork') or
                                                         node.func.attr.startswith(('exec', 'spawn'))):
                            errors.append(f'process execution in core: {name}')
    visited, visiting = set(), set()
    def visit(name):
        if name in visiting:
            errors.append(f'dependency cycle: {name}')
            return
        if name in visited:
            return
        visiting.add(name)
        for dependency in sorted(graph.get(name, ())):
            visit(dependency)
        visiting.remove(name)
        visited.add(name)
    for name in sorted(graph):
        visit(name)
    return {'status': 'ARCHITECTURE_CHECK_PASS' if not errors else 'ARCHITECTURE_CHECK_FAIL',
            'modules': len(sources), 'errors': sorted(set(errors)),
            'scope': 'STATIC_BOUNDARIES_NOT_NATIVE_PLATFORM_CERTIFICATION',
            'installer_builds': policy['installer_builds']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = check(args.root)
    print(json.dumps(report, indent=2))
    return 0 if not report['errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
