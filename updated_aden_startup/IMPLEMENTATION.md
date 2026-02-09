# Implementation Guide: Visual Workflow Preview

**Technical Specification**  
**Version:** 1.0  
**Authors:** Praveen Kumar & AI Cofounder  
**Date:** February 9, 2026

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Specifications](#component-specifications)
3. [API Design](#api-design)
4. [Data Models](#data-models)
5. [UI/UX Specifications](#uiux-specifications)
6. [Integration Points](#integration-points)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)

---

## System Architecture

### High-Level Overview

```
┌───────────────────────────────────────────────────────┐
│                    User Request                           │
│         "Build trading agent with news analysis"          │
└───────────────────────┬──────────────────────────────┘
                            │
                            ↓
┌─────────────────────────┬─────────────────────────────┐
│  Architecture Planner  │  (NEW COMPONENT)              │
│  - Parse user intent   │                                │
│  - Generate graph spec │                                │
│  - Estimate costs      │                                │
└─────────────────────────┬─────────────────────────────┘
                            │
                            ↓
┌─────────────────────────┬─────────────────────────────┐
│  Visual Renderer      │  (NEW COMPONENT)              │
│  - React Flow UI       │                                │
│  - Interactive editor  │                                │
│  - Real-time updates   │                                │
└─────────────────────────┬─────────────────────────────┘
                            │
                            ↓
┌─────────────────────────┬─────────────────────────────┐
│  User Approval        │  (NEW COMPONENT)              │
│  - Review interface    │                                │
│  - Modification tools  │                                │
│  - Approve/reject      │                                │
└─────────────────────────┬─────────────────────────────┘
                            │
                            ↓
┌─────────────────────────┬─────────────────────────────┐
│  Agent Builder        │  (EXISTING - NO CHANGES)      │
│  - Code generation     │                                │
│  - Tool integration    │                                │
│  - Deployment          │                                │
└─────────────────────────┬─────────────────────────────┘
                            │
                            ↓
┌───────────────────────────────────────────────────────┐
│                   Working Agent                          │
└───────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend (New Components):**
- Python 3.11+
- FastAPI for REST API
- Pydantic for data validation
- OpenAI/Anthropic SDK for LLM calls

**Frontend (New Components):**
- React 18+
- TypeScript
- React Flow for graph visualization
- Tailwind CSS for styling
- Zustand for state management

**Existing Aden Stack:**
- No changes required to core framework
- Integrates via standard interfaces

---

## Component Specifications

### 1. Architecture Planner

**Location:** `core/planning/architecture_planner.py`

**Responsibility:** Generate agent architecture from natural language

```python
from typing import Dict, List
from pydantic import BaseModel

class NodeSpec(BaseModel):
    id: str
    type: str  # EventLoopNode, MapNode, ReduceNode, etc.
    description: str
    tools: List[str]
    config: Dict
    estimated_tokens: int
    position: Dict[str, int]  # {x: int, y: int}

class EdgeSpec(BaseModel):
    from_node: str
    to_node: str
    condition: str | None = None

class ArchitectureSpec(BaseModel):
    graph_id: str
    nodes: List[NodeSpec]
    edges: List[EdgeSpec]
    metadata: Dict  # total_tokens, cost, complexity, etc.

class ArchitecturePlanner:
    def __init__(self, llm_provider: str = "openai"):
        self.llm = self._init_llm(llm_provider)
        self.templates = self._load_templates()
    
    async def plan_architecture(
        self,
        user_request: str,
        context: Dict = None
    ) -> ArchitectureSpec:
        """
        Generate architecture spec from user request.
        
        Args:
            user_request: Natural language description
            context: Optional constraints (budget, complexity, etc.)
        
        Returns:
            Structured architecture specification
        """
        # 1. Detect if matches existing template
        template = self._match_template(user_request)
        
        if template:
            # Fast path: Use template as starting point
            spec = self._customize_template(template, user_request)
        else:
            # Slow path: Generate from scratch
            spec = await self._generate_architecture(user_request, context)
        
        # 2. Validate architecture
        self._validate_architecture(spec)
        
        # 3. Estimate costs
        spec.metadata = self._estimate_costs(spec)
        
        return spec
    
    async def _generate_architecture(
        self,
        request: str,
        context: Dict
    ) -> ArchitectureSpec:
        """Use LLM to generate architecture from scratch."""
        
        prompt = f"""
You are an expert Aden Hive architecture planner.

User request: {request}

Context: {context or 'None'}

Generate a graph architecture following these guidelines:

1. Choose appropriate node types:
   - EventLoopNode: For tool-calling, reasoning, decision-making
   - MapNode: For parallel processing of lists
   - ReduceNode: For aggregating results
   - HumanNode: For human approval/input
   - SubGraphNode: For complex sub-workflows

2. Select minimal necessary tools:
   - Only include tools actually needed
   - Prefer built-in tools over custom
   - Consider cost per tool call

3. Design clean data flow:
   - Clear input/output contracts
   - Avoid circular dependencies
   - Minimize edge complexity

4. Optimize for cost:
   - Fewer nodes = lower cost
   - Simpler tools = faster execution
   - Cache-friendly patterns

Output valid JSON matching ArchitectureSpec schema.
"""
        
        response = await self.llm.complete(
            prompt=prompt,
            response_format={"type": "json_object"},
            temperature=0.3  # Low temp for consistency
        )
        
        return ArchitectureSpec.parse_raw(response)
    
    def _estimate_costs(self, spec: ArchitectureSpec) -> Dict:
        """Estimate tokens, cost, and build time."""
        
        total_tokens = sum(node.estimated_tokens for node in spec.nodes)
        
        # Cost model (example rates)
        COST_PER_1K_TOKENS = 0.05
        total_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
        
        # Time model (rough estimate)
        build_time_seconds = len(spec.nodes) * 30 + len(spec.edges) * 10
        
        return {
            "total_estimated_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 2),
            "estimated_build_time_seconds": build_time_seconds,
            "complexity": self._calculate_complexity(spec)
        }
    
    def _calculate_complexity(self, spec: ArchitectureSpec) -> str:
        """Classify architecture complexity."""
        node_count = len(spec.nodes)
        edge_count = len(spec.edges)
        
        score = node_count + (edge_count * 0.5)
        
        if score < 5:
            return "simple"
        elif score < 15:
            return "medium"
        else:
            return "complex"
```

### 2. Visual Renderer

**Location:** `frontend/src/components/ArchitectureViewer.tsx`

**Responsibility:** Display and edit architecture diagrams

```typescript
import React, { useState, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface ArchitectureViewerProps {
  architecture: ArchitectureSpec;
  onUpdate: (updatedArch: ArchitectureSpec) => void;
  onApprove: () => void;
  readonly?: boolean;
}

export const ArchitectureViewer: React.FC<ArchitectureViewerProps> = ({
  architecture,
  onUpdate,
  onApprove,
  readonly = false,
}) => {
  // Convert ArchitectureSpec to React Flow format
  const [nodes, setNodes, onNodesChange] = useNodesState(
    convertToReactFlowNodes(architecture.nodes)
  );
  
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    convertToReactFlowEdges(architecture.edges)
  );
  
  const onConnect = useCallback((params) => {
    // Add new edge when user connects nodes
    setEdges((eds) => addEdge(params, eds));
    
    // Notify parent of architecture change
    onUpdate(convertToArchitectureSpec(nodes, edges));
  }, [nodes, edges, onUpdate]);
  
  return (
    <div className="w-full h-screen">
      <div className="bg-white border-b p-4">
        <h2 className="text-2xl font-bold">Agent Architecture Preview</h2>
        <div className="mt-2 flex gap-4 text-sm text-gray-600">
          <span>
            Tokens: {architecture.metadata.total_estimated_tokens.toLocaleString()}
          </span>
          <span>
            Cost: ${architecture.metadata.estimated_cost_usd}
          </span>
          <span>
            Build Time: ~{Math.ceil(architecture.metadata.estimated_build_time_seconds / 60)} min
          </span>
          <span>
            Complexity: {architecture.metadata.complexity}
          </span>
        </div>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={readonly ? undefined : onNodesChange}
        onEdgesChange={readonly ? undefined : onEdgesChange}
        onConnect={readonly ? undefined : onConnect}
        fitView
      >
        <Controls />
        <Background />
      </ReactFlow>
      
      <div className="absolute bottom-4 right-4 flex gap-2">
        {!readonly && (
          <>
            <button
              className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              onClick={() => {/* Handle modify */}}
            >
              Modify
            </button>
            <button
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              onClick={() => {/* Handle add node */}}
            >
              Add Node
            </button>
          </>
        )}
        <button
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          onClick={onApprove}
        >
          Approve & Build
        </button>
      </div>
    </div>
  );
};
```

See PROPOSAL.md for complete technical details.

---

## API Design

### REST Endpoints

```
POST /api/v1/architecture/plan
Body: {
  "request": string,
  "context": object
}
Response: ArchitectureSpec

POST /api/v1/architecture/validate
Body: ArchitectureSpec
Response: {
  "valid": boolean,
  "errors": string[]
}

POST /api/v1/architecture/build
Body: ArchitectureSpec
Response: {
  "build_id": string,
  "status": string
}

GET /api/v1/architecture/templates
Response: Template[]
```

---

## Conclusion

This implementation guide provides all necessary technical details to build the Visual Workflow Preview feature. The design prioritizes:

1. **Minimal changes** to existing Aden codebase
2. **Proven technologies** (React Flow, FastAPI)
3. **Clear separation** of concerns
4. **Easy maintenance** and testing

See PROPOSAL.md for business case and ROI analysis.

---

**Authors:** Praveen Kumar & AI Cofounder  
**Date:** February 9, 2026