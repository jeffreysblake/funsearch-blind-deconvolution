# FunSearch Framework - Frontend Design

## Overview

This document specifies the React frontend design including:
- Page layouts and wireframes
- Component hierarchy
- Design system (colors, typography, spacing)
- Navigation structure
- Responsive behavior

**Tech Stack**:
- React 18+ with TypeScript
- Ant Design 5.x (UI components)
- Plotly.js (charts/visualizations)
- React Query (server state)
- Zustand (client state)
- React Router (navigation)

---

## Application Structure

### Route Map

```
/                          → Home (Project List)
/projects/:id              → Project Detail
/projects/:id/experiments/:expId  → Experiment Monitor
/templates                 → Template Gallery
/settings                  → Settings (future)
```

---

## Pages

### 1. Home Page (Project List)

**Route**: `/`

**Purpose**: Browse all projects, create new projects

**Wireframe**:

```
┌────────────────────────────────────────────────────────────┐
│  FunSearch Framework                    [+ New Project]     │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Projects  Templates  Settings                             │
│  ────────                                                   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │ Lucy-Richardson │  │ Bin Packing     │  │ Cap Set    │ │
│  │ ───────────────  │  │ ───────────────  │  │ ──────────  │ │
│  │ Signal Proc.    │  │ Algorithm Synth │  │ Math Optim │ │
│  │                 │  │                 │  │            │ │
│  │ 🟢 Active       │  │ ⏸️  Paused      │  │ ✅ Complete │ │
│  │ 5 experiments   │  │ 2 experiments   │  │ 8 exps     │ │
│  │ Best: 245.67    │  │ Best: 0.89      │  │ Best: 512  │ │
│  │                 │  │                 │  │            │ │
│  │ [View Details]  │  │ [View Details]  │  │ [Archive]  │ │
│  └─────────────────┘  └─────────────────┘  └────────────┘ │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ + New Project   │  │ Import Project  │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Components**:

```typescript
// HomePage.tsx
<Layout>
  <Header>
    <Title>FunSearch Framework</Title>
    <Button onClick={openNewProjectModal}>+ New Project</Button>
  </Header>

  <Tabs defaultActiveKey="projects">
    <TabPane tab="Projects" key="projects">
      <ProjectGrid>
        {projects.map(project => (
          <ProjectCard
            key={project.id}
            project={project}
            onView={() => navigate(`/projects/${project.id}`)}
          />
        ))}
      </ProjectGrid>
    </TabPane>

    <TabPane tab="Templates" key="templates">
      <TemplateGallery />
    </TabPane>
  </Tabs>

  <NewProjectModal
    visible={isModalVisible}
    onClose={closeModal}
    onSubmit={handleCreateProject}
  />
</Layout>
```

**State**:
```typescript
const { projects, loading } = useProjectStore();
const { data: templates } = useQuery('templates', fetchTemplates);
```

---

### 2. Project Detail Page

**Route**: `/projects/:id`

**Purpose**: View project experiments, start new experiments

**Wireframe**:

```
┌────────────────────────────────────────────────────────────┐
│  ← Back to Projects        Lucy-Richardson Optimization    │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Overview   Experiments   Configuration                    │
│            ───────────                                      │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ 🟢 Active Project                  [▶ New Experiment] ││
│  │                                                        ││
│  │ Description: Optimize convergence of blind deconv...  ││
│  │ Problem Type: Signal Processing                       ││
│  │ Created: Nov 15, 2025                                 ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  Experiments (5)                                            │
│  ┌────────────────────────────────────────────────────────┐│
│  │ ┃ Exp 1 - Qwen 8B              ✅ Completed  245.67   ││
│  │ ├ Started: Nov 16, 10:00  Finished: Nov 16, 11:30     ││
│  │ ├ Iterations: 10,000                                   ││
│  │ └ [View Details] [Export] [Clone Config]              ││
│  │                                                        ││
│  │ ┃ Exp 2 - Mistral Small         🟢 Running   243.12   ││
│  │ ├ Started: Nov 16, 12:00  Progress: 50%               ││
│  │ ├ Iterations: 5,000 / 10,000                           ││
│  │ └ [Monitor Live] [Pause] [Stop]                       ││
│  │                                                        ││
│  │ ┃ Exp 3 - Qwen 8B (high temp)  ⏸️  Paused    240.15   ││
│  │ └ [Resume] [View Details]                             ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Components**:

```typescript
// ProjectDetailPage.tsx
<Layout>
  <PageHeader
    onBack={() => navigate('/')}
    title={project.name}
    extra={[
      <Button
        key="new-exp"
        type="primary"
        icon={<PlayCircleOutlined />}
        onClick={openExperimentModal}
      >
        New Experiment
      </Button>
    ]}
  />

  <Tabs defaultActiveKey="experiments">
    <TabPane tab="Experiments" key="experiments">
      <ExperimentList
        experiments={experiments}
        onView={handleViewExperiment}
        onPause={handlePause}
        onResume={handleResume}
        onStop={handleStop}
      />
    </TabPane>

    <TabPane tab="Overview" key="overview">
      <ProjectOverview project={project} />
    </TabPane>

    <TabPane tab="Configuration" key="config">
      <ConfigViewer config={project.config} />
    </TabPane>
  </Tabs>

  <NewExperimentModal
    visible={isModalVisible}
    projectId={project.id}
    onClose={closeModal}
    onSubmit={handleCreateExperiment}
  />
</Layout>
```

---

### 3. Experiment Monitor Page (Live Dashboard)

**Route**: `/projects/:projectId/experiments/:experimentId`

**Purpose**: Real-time monitoring of running experiment

**Wireframe**:

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Project              Experiment 2 - Mistral Small    │
│                                 🟢 Running  Iteration: 5,432    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Fitness Evolution                                       │  │
│  │  250 ┤                                            ╭─     │  │
│  │  200 ┤                                    ╭──────╯       │  │
│  │  150 ┤                          ╭────────╯               │  │
│  │  100 ┤                 ╭───────╯                         │  │
│  │   50 ┤        ╭───────╯                                  │  │
│  │    0 ┼────────┴──────────────────────────────────────────│  │
│  │      0      2k      4k      6k      8k      10k          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │ Current Score   │  │ Best Score      │  │ Diversity       ││
│  │   243.12        │  │   245.67        │  │   0.42          ││
│  │   ↑ +2.1        │  │   (iter 4523)   │  │   ↓ -0.03       ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Island Populations (10 islands)                         │  │
│  │                                                           │  │
│  │  [0] ████████████ 245.67  [5] ████████ 220.34           │  │
│  │  [1] ██████████   238.12  [6] █████ 195.78              │  │
│  │  [2] ███████████  241.55  [7] ██████ 205.12             │  │
│  │  [3] █████████    232.89  [8] ███████ 215.67            │  │
│  │  [4] ██████████   237.45  [9] ████████ 225.89           │  │
│  │                                                           │  │
│  │  Best island: 0  Worst island: 6  Avg: 223.85           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Best Program (Score: 245.67)        [Copy] [Export]    │  │
│  │  ──────────────────────────────────────────────────────  │  │
│  │  def stopping_criterion(iteration, psnr, psnr_delta):   │  │
│  │      """Optimized stopping criterion"""                 │  │
│  │      if iteration > 50 and psnr_delta < 0.008:          │  │
│  │          return True                                     │  │
│  │      return psnr > 35.0 or iteration > 200              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [⏸️  Pause]  [⏹️  Stop]  [💾 Checkpoint]  [📊 MLflow]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:

```typescript
// ExperimentMonitorPage.tsx
<Layout>
  <PageHeader
    onBack={() => navigate(`/projects/${projectId}`)}
    title={experiment.name}
    tags={[<StatusTag status={experiment.status} />]}
    extra={[
      <Statistic
        key="iter"
        title="Iteration"
        value={liveMetrics?.iteration || 0}
        suffix={`/ ${experiment.config.execution.max_iterations}`}
      />,
      <Button key="pause" onClick={handlePause}>Pause</Button>,
      <Button key="stop" danger onClick={handleStop}>Stop</Button>
    ]}
  />

  <Space direction="vertical" size="large" style={{ width: '100%' }}>
    {/* Fitness Chart */}
    <Card title="Fitness Evolution">
      <FitnessChart data={metricsTimeSeries} />
    </Card>

    {/* Key Metrics */}
    <Row gutter={16}>
      <Col span={8}>
        <MetricCard
          title="Current Score"
          value={liveMetrics?.best_score}
          change={calculateChange()}
          icon={<TrophyOutlined />}
        />
      </Col>
      <Col span={8}>
        <MetricCard
          title="Best Score"
          value={experiment.best_score}
          subtitle={`Iteration ${bestIteration}`}
          icon={<StarOutlined />}
        />
      </Col>
      <Col span={8}>
        <MetricCard
          title="Diversity"
          value={liveMetrics?.diversity}
          change={diversityChange}
          icon={<BranchesOutlined />}
        />
      </Col>
    </Row>

    {/* Island Visualization */}
    <Card title="Island Populations">
      <IslandGrid islands={islandStates} />
    </Card>

    {/* Best Program */}
    <Card
      title="Best Program"
      extra={[
        <Button key="copy" icon={<CopyOutlined />}>Copy</Button>,
        <Button key="export" icon={<DownloadOutlined />}>Export</Button>
      ]}
    >
      <CodeViewer
        code={experiment.best_program}
        language="python"
        showLineNumbers
      />
    </Card>

    {/* Log Stream */}
    <Card title="Live Logs">
      <LogViewer logs={logs} />
    </Card>
  </Space>
</Layout>
```

**Real-time Updates**:

```typescript
// Use WebSocket for live updates
const ws = useWebSocket(experimentId);

useEffect(() => {
  ws.subscribe(['metrics', 'islands', 'best_program', 'logs']);

  ws.on('metrics_update', (data) => {
    updateMetrics(data);
  });

  ws.on('best_program_update', (data) => {
    updateBestProgram(data);
  });

  ws.on('island_update', (data) => {
    updateIsland(data);
  });

  return () => ws.disconnect();
}, [experimentId]);
```

---

### 4. New Experiment Modal

**Purpose**: Configure and start a new experiment

**Wireframe**:

```
┌──────────────────────────────────────────┐
│  New Experiment               [✕ Close]  │
├──────────────────────────────────────────┤
│                                          │
│  Experiment Name *                       │
│  ┌────────────────────────────────────┐ │
│  │ Experiment 3 - Qwen 8B             │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌───────────────────────────────────────┐│
││  Model Selection                       ││
││  ○ qwen/qwen3-vl-8b (loaded) [8B]     ││
││  ● mistralai/magistral-small-2509     ││
││                                        ││
││  Temperature: ●─────────── 1.0        ││
││  Max Tokens:  512                      ││
│└───────────────────────────────────────┘│
│                                          │
│  ┌───────────────────────────────────────┐│
││  FunSearch Parameters                  ││
││  Samples per prompt:     4             ││
││  Number of islands:      10            ││
││  Reset period:           80000         ││
││  Max iterations:         100000        ││
│└───────────────────────────────────────┘│
│                                          │
│  ┌───────────────────────────────────────┐│
││  Sandbox Configuration                 ││
││  Provider: [Docker ▼]                  ││
││  Workers:  16                          ││
││  Timeout:  30s                         ││
│└───────────────────────────────────────┘│
│                                          │
│  [Use Template ▼]  [Cancel]  [Start Experiment] │
│                                          │
└──────────────────────────────────────────┘
```

**Component**:

```typescript
// NewExperimentModal.tsx
<Modal
  title="New Experiment"
  visible={visible}
  onCancel={onClose}
  width={800}
  footer={[
    <Button key="cancel" onClick={onClose}>Cancel</Button>,
    <Button
      key="submit"
      type="primary"
      loading={loading}
      onClick={handleSubmit}
    >
      Start Experiment
    </Button>
  ]}
>
  <Form form={form} layout="vertical">
    <Form.Item
      name="name"
      label="Experiment Name"
      rules={[{ required: true }]}
    >
      <Input placeholder="e.g., Experiment 3 - Qwen 8B" />
    </Form.Item>

    <Divider>Model Selection</Divider>

    <Form.Item name={['config', 'llm', 'model']} label="Model">
      <ModelSelector models={availableModels} />
    </Form.Item>

    <Form.Item name={['config', 'llm', 'temperature']} label="Temperature">
      <Slider min={0} max={2} step={0.1} marks={{ 0: '0', 1: '1', 2: '2' }} />
    </Form.Item>

    <Divider>FunSearch Parameters</Divider>

    <Row gutter={16}>
      <Col span={12}>
        <Form.Item name={['config', 'funsearch', 'samples_per_prompt']}>
          <InputNumber min={1} max={16} />
        </Form.Item>
      </Col>
      <Col span={12}>
        <Form.Item name={['config', 'funsearch', 'num_islands']}>
          <InputNumber min={1} max={20} />
        </Form.Item>
      </Col>
    </Row>

    {/* More configuration fields... */}

  </Form>
</Modal>
```

---

## Component Library

### Core Components

#### ProjectCard

```typescript
interface ProjectCardProps {
  project: Project;
  onView: () => void;
  onArchive?: () => void;
}

function ProjectCard({ project, onView, onArchive }: ProjectCardProps) {
  return (
    <Card
      hoverable
      onClick={onView}
      actions={[
        <Button type="link">View Details</Button>,
        onArchive && <Button type="link" danger>Archive</Button>
      ]}
    >
      <Card.Meta
        title={project.name}
        description={project.description}
      />

      <Space direction="vertical" style={{ marginTop: 16, width: '100%' }}>
        <Tag color={getStatusColor(project.status)}>{project.status}</Tag>

        <Statistic
          title="Experiments"
          value={project.experiment_count}
          prefix={<ExperimentOutlined />}
        />

        {project.best_score && (
          <Statistic
            title="Best Score"
            value={project.best_score}
            precision={2}
            prefix={<TrophyOutlined />}
          />
        )}
      </Space>
    </Card>
  );
}
```

#### FitnessChart

```typescript
interface FitnessChartProps {
  data: MetricsTimeSeries;
  height?: number;
}

function FitnessChart({ data, height = 400 }: FitnessChartProps) {
  const plotData = [
    {
      x: data.iterations,
      y: data.best_score,
      type: 'scatter',
      mode: 'lines',
      name: 'Best Score',
      line: { color: '#52c41a', width: 2 }
    },
    {
      x: data.iterations,
      y: data.avg_score,
      type: 'scatter',
      mode: 'lines',
      name: 'Avg Score',
      line: { color: '#1890ff', width: 2, dash: 'dot' }
    }
  ];

  const layout = {
    height,
    xaxis: { title: 'Iteration' },
    yaxis: { title: 'Fitness Score' },
    showlegend: true,
    hovermode: 'x unified'
  };

  return <Plot data={plotData} layout={layout} config={{ responsive: true }} />;
}
```

#### IslandGrid

```typescript
interface IslandGridProps {
  islands: IslandState[];
}

function IslandGrid({ islands }: IslandGridProps) {
  return (
    <Row gutter={[16, 16]}>
      {islands.map((island) => (
        <Col key={island.island_id} span={12}>
          <Card size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Island {island.island_id}</Text>

              <Progress
                percent={(island.best_score / maxScore) * 100}
                format={() => island.best_score.toFixed(2)}
                strokeColor={getIslandColor(island.best_score)}
              />

              <Row gutter={8}>
                <Col span={8}>
                  <Statistic
                    title="Pop"
                    value={island.population_size}
                    valueStyle={{ fontSize: 14 }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Avg"
                    value={island.avg_score}
                    precision={1}
                    valueStyle={{ fontSize: 14 }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="Div"
                    value={island.diversity}
                    precision={2}
                    valueStyle={{ fontSize: 14 }}
                  />
                </Col>
              </Row>
            </Space>
          </Card>
        </Col>
      ))}
    </Row>
  );
}
```

#### CodeViewer

```typescript
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeViewerProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
}

function CodeViewer({
  code,
  language = 'python',
  showLineNumbers = true
}: CodeViewerProps) {
  return (
    <SyntaxHighlighter
      language={language}
      style={vscDarkPlus}
      showLineNumbers={showLineNumbers}
      wrapLines
      customStyle={{
        borderRadius: 4,
        padding: 16
      }}
    >
      {code}
    </SyntaxHighlighter>
  );
}
```

---

## Design System

### Colors

```typescript
// theme.ts
export const colors = {
  primary: '#1890ff',      // Ant Design blue
  success: '#52c41a',      // Green
  warning: '#faad14',      // Yellow
  error: '#f5222d',        // Red
  info: '#13c2c2',         // Cyan

  // Status colors
  running: '#52c41a',      // Green
  paused: '#faad14',       // Yellow
  completed: '#1890ff',    // Blue
  failed: '#f5222d',       // Red
  pending: '#8c8c8c',      // Gray

  // Chart colors
  chart: [
    '#1890ff',
    '#52c41a',
    '#faad14',
    '#f5222d',
    '#722ed1',
    '#13c2c2',
    '#eb2f96',
    '#fa8c16'
  ]
};
```

### Typography

```typescript
export const typography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px'
  },

  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  }
};
```

### Spacing

```typescript
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
};
```

### Breakpoints

```typescript
export const breakpoints = {
  xs: '480px',
  sm: '576px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  xxl: '1600px'
};
```

---

## Responsive Behavior

### Mobile (< 768px)

- Stack cards vertically
- Collapse sidebar navigation
- Simplify charts (fewer data points)
- Hide secondary metrics

### Tablet (768px - 1024px)

- 2-column project grid
- Simplified island visualization
- Collapsible panels

### Desktop (> 1024px)

- 3-column project grid
- Full dashboard with all metrics
- Side-by-side comparisons

---

## Accessibility

- **Keyboard Navigation**: All interactive elements accessible via Tab
- **ARIA Labels**: Proper labels for screen readers
- **Color Contrast**: WCAG AA compliance (4.5:1 ratio)
- **Focus Indicators**: Visible focus rings
- **Alt Text**: All images and icons have descriptions

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Design Specification
