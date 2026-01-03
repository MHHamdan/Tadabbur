import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import { StoryGraph } from '../../lib/api';

interface StoryGraphViewProps {
  graph: StoryGraph;
  language: 'ar' | 'en';
}

export function StoryGraphView({ graph, language }: StoryGraphViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    // Convert graph data to Cytoscape format
    const elements = [
      // Nodes
      ...graph.nodes.map((node) => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          ...node.data,
        },
      })),
      // Edges
      ...graph.edges.map((edge, i) => ({
        data: {
          id: `edge-${i}`,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          label: edge.label,
        },
      })),
    ];

    // Initialize Cytoscape
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        // Story node (main)
        {
          selector: 'node[type="story"]',
          style: {
            'background-color': '#0ea5e9',
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#fff',
            'font-size': '14px',
            'font-weight': 'bold',
            width: 80,
            height: 80,
            shape: 'ellipse',
          },
        },
        // Segment nodes
        {
          selector: 'node[type="segment"]',
          style: {
            'background-color': '#f0f9ff',
            'border-color': '#38bdf8',
            'border-width': 2,
            label: 'data(label)',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            color: '#0369a1',
            'font-size': '12px',
            width: 60,
            height: 60,
            shape: 'round-rectangle',
          },
        },
        // Default edges
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#94a3b8',
            'target-arrow-color': '#94a3b8',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            label: 'data(label)',
            'font-size': '10px',
            color: '#64748b',
            'text-rotation': 'autorotate',
            'text-margin-y': -10,
          },
        },
        // Contains edges (story -> segment)
        {
          selector: 'edge[type="contains"]',
          style: {
            'line-color': '#cbd5e1',
            'target-arrow-color': '#cbd5e1',
            'line-style': 'dashed',
            label: '',
          },
        },
        // Continuation edges
        {
          selector: 'edge[type="continuation"]',
          style: {
            'line-color': '#22c55e',
            'target-arrow-color': '#22c55e',
          },
        },
        // Parallel edges
        {
          selector: 'edge[type="parallel"]',
          style: {
            'line-color': '#eab308',
            'target-arrow-color': '#eab308',
            'line-style': 'dashed',
          },
        },
        // Expansion edges
        {
          selector: 'edge[type="expansion"]',
          style: {
            'line-color': '#8b5cf6',
            'target-arrow-color': '#8b5cf6',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        animationDuration: 500,
        nodeRepulsion: function () {
          return 8000;
        },
        idealEdgeLength: function () {
          return 100;
        },
        edgeElasticity: function () {
          return 100;
        },
      },
      minZoom: 0.5,
      maxZoom: 2,
      wheelSensitivity: 0.3,
    });

    // Add event handlers
    cyRef.current.on('tap', 'node', (evt) => {
      const node = evt.target;
      console.log('Node clicked:', node.data());
    });

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graph]);

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-50">
      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow p-3 text-xs">
        <div className="font-medium mb-2">
          {language === 'ar' ? 'مفتاح الألوان' : 'Legend'}
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span>{language === 'ar' ? 'استمرار' : 'Continuation'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500 rounded" />
            <span>{language === 'ar' ? 'تشابه' : 'Parallel'}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-purple-500 rounded" />
            <span>{language === 'ar' ? 'توسع' : 'Expansion'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
