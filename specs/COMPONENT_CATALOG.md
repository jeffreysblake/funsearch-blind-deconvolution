# FunSearch Framework - Component Catalog

## Overview

Complete catalog of all React components with props, states, and usage examples.

---

## Layout Components

### AppLayout

**Purpose**: Main application layout with navigation

```typescript
interface AppLayoutProps {
  children: React.ReactNode;
}

function AppLayout({ children }: AppLayoutProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <Logo />
        <MainMenu />
      </Sider>

      <AntLayout>
        <Header>
          <TopBar />
        </Header>

        <Content style={{ padding: 24 }}>
          {children}
        </Content>

        <Footer style={{ textAlign: 'center' }}>
          FunSearch Framework ©2025
        </Footer>
      </AntLayout>
    </AntLayout>
  );
}
```

---

### MainMenu

```typescript
function MainMenu() {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Projects'
    },
    {
      key: '/templates',
      icon: <AppstoreOutlined />,
      label: 'Templates'
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings'
    }
  ];

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[location.pathname]}
      items={menuItems}
      onClick={({ key }) => navigate(key)}
    />
  );
}
```

---

## Project Components

### ProjectCard

```typescript
interface ProjectCardProps {
  project: Project;
  onView: () => void;
  onArchive?: () => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onView,
  onArchive
}) => {
  return (
    <Card
      hoverable
      style={{ height: '100%' }}
      onClick={onView}
      actions={[
        <Button type="link" icon={<EyeOutlined />} key="view">
          View
        </Button>,
        ...(onArchive ? [
          <Popconfirm
            key="archive"
            title="Archive this project?"
            onConfirm={(e) => {
              e?.stopPropagation();
              onArchive();
            }}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => e.stopPropagation()}
            >
              Archive
            </Button>
          </Popconfirm>
        ] : [])
      ]}
    >
      <Card.Meta
        avatar={<Avatar icon={getProblemTypeIcon(project.problem_type)} />}
        title={
          <Space>
            <Text strong>{project.name}</Text>
            <StatusBadge status={project.status} />
          </Space>
        }
        description={
          <Text ellipsis={{ rows: 2 }} type="secondary">
            {project.description || 'No description'}
          </Text>
        }
      />

      <Divider style={{ margin: '12px 0' }} />

      <Space direction="vertical" style={{ width: '100%' }}>
        <Row gutter={16}>
          <Col span={12}>
            <Statistic
              title="Experiments"
              value={project.experiment_count}
              prefix={<ExperimentOutlined />}
              valueStyle={{ fontSize: 16 }}
            />
          </Col>
          <Col span={12}>
            {project.best_score !== null && (
              <Statistic
                title="Best Score"
                value={project.best_score}
                precision={2}
                prefix={<TrophyOutlined />}
                valueStyle={{ fontSize: 16 }}
              />
            )}
          </Col>
        </Row>

        <Text type="secondary" style={{ fontSize: 12 }}>
          Updated: {formatRelativeTime(project.updated_at)}
        </Text>
      </Space>
    </Card>
  );
};
```

---

### ProjectGrid

```typescript
interface ProjectGridProps {
  projects: Project[];
  loading?: boolean;
  onViewProject: (id: string) => void;
  onArchiveProject?: (id: string) => void;
}

const ProjectGrid: React.FC<ProjectGridProps> = ({
  projects,
  loading,
  onViewProject,
  onArchiveProject
}) => {
  if (loading) {
    return (
      <Row gutter={[16, 16]}>
        {Array.from({ length: 6 }).map((_, i) => (
          <Col xs={24} sm={12} lg={8} key={i}>
            <Card loading />
          </Col>
        ))}
      </Row>
    );
  }

  if (projects.length === 0) {
    return (
      <Empty
        description="No projects yet"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <Button type="primary">Create Your First Project</Button>
      </Empty>
    );
  }

  return (
    <Row gutter={[16, 16]}>
      {projects.map((project) => (
        <Col xs={24} sm={12} lg={8} key={project.id}>
          <ProjectCard
            project={project}
            onView={() => onViewProject(project.id)}
            onArchive={
              onArchiveProject
                ? () => onArchiveProject(project.id)
                : undefined
            }
          />
        </Col>
      ))}
    </Row>
  );
};
```

---

## Experiment Components

### ExperimentList

```typescript
interface ExperimentListProps {
  experiments: Experiment[];
  onView: (id: string) => void;
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
  onStop?: (id: string) => void;
}

const ExperimentList: React.FC<ExperimentListProps> = ({
  experiments,
  onView,
  onPause,
  onResume,
  onStop
}) => {
  const columns: ColumnsType<Experiment> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <Space>
          <StatusIcon status={record.status} />
          <Button type="link" onClick={() => onView(record.id)}>
            {name}
          </Button>
        </Space>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <StatusTag status={status} />
    },
    {
      title: 'Model',
      dataIndex: ['config', 'llm', 'model'],
      key: 'model',
      render: (model) => <Tag>{model}</Tag>
    },
    {
      title: 'Best Score',
      dataIndex: 'best_score',
      key: 'best_score',
      align: 'right',
      render: (score) =>
        score !== null ? (
          <Text strong>{score.toFixed(2)}</Text>
        ) : (
          <Text type="secondary">-</Text>
        )
    },
    {
      title: 'Progress',
      key: 'progress',
      render: (_, record) => (
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <Progress
            percent={getProgressPercent(record)}
            size="small"
            status={getProgressStatus(record.status)}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.iterations_completed.toLocaleString()} /{' '}
            {record.config.execution.max_iterations.toLocaleString()}
          </Text>
        </Space>
      )
    },
    {
      title: 'Duration',
      key: 'duration',
      render: (_, record) => (
        <Text type="secondary">
          {formatDuration(record.started_at, record.completed_at)}
        </Text>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <ExperimentActions
          experiment={record}
          onPause={onPause}
          onResume={onResume}
          onStop={onStop}
          onView={onView}
        />
      )
    }
  ];

  return (
    <Table
      dataSource={experiments}
      columns={columns}
      rowKey="id"
      pagination={{ pageSize: 10 }}
    />
  );
};
```

---

### ExperimentActions

```typescript
interface ExperimentActionsProps {
  experiment: Experiment;
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
  onStop?: (id: string) => void;
  onView?: (id: string) => void;
}

const ExperimentActions: React.FC<ExperimentActionsProps> = ({
  experiment,
  onPause,
  onResume,
  onStop,
  onView
}) => {
  const items: MenuProps['items'] = [];

  if (onView) {
    items.push({
      key: 'view',
      icon: <EyeOutlined />,
      label: 'View Details',
      onClick: () => onView(experiment.id)
    });
  }

  if (experiment.status === 'running' && onPause) {
    items.push({
      key: 'pause',
      icon: <PauseOutlined />,
      label: 'Pause',
      onClick: () => onPause(experiment.id)
    });
  }

  if (experiment.status === 'paused' && onResume) {
    items.push({
      key: 'resume',
      icon: <PlayCircleOutlined />,
      label: 'Resume',
      onClick: () => onResume(experiment.id)
    });
  }

  if (
    (experiment.status === 'running' || experiment.status === 'paused') &&
    onStop
  ) {
    items.push({
      key: 'stop',
      icon: <StopOutlined />,
      label: 'Stop',
      danger: true,
      onClick: () => {
        Modal.confirm({
          title: 'Stop Experiment?',
          content: 'This action cannot be undone.',
          okText: 'Stop',
          okType: 'danger',
          onOk: () => onStop(experiment.id)
        });
      }
    });
  }

  return (
    <Dropdown menu={{ items }} trigger={['click']}>
      <Button icon={<MoreOutlined />} />
    </Dropdown>
  );
};
```

---

## Chart Components

### FitnessChart

```typescript
interface FitnessChartProps {
  data: MetricsTimeSeries;
  height?: number;
  showDiversity?: boolean;
}

const FitnessChart: React.FC<FitnessChartProps> = ({
  data,
  height = 400,
  showDiversity = false
}) => {
  const traces: Plotly.Data[] = [
    {
      x: data.iterations,
      y: data.best_score,
      type: 'scatter',
      mode: 'lines',
      name: 'Best Score',
      line: {
        color: colors.success,
        width: 2
      },
      hovertemplate: 'Iteration: %{x}<br>Best Score: %{y:.2f}<extra></extra>'
    },
    {
      x: data.iterations,
      y: data.avg_score,
      type: 'scatter',
      mode: 'lines',
      name: 'Avg Score',
      line: {
        color: colors.primary,
        width: 2,
        dash: 'dot'
      },
      hovertemplate: 'Iteration: %{x}<br>Avg Score: %{y:.2f}<extra></extra>'
    }
  ];

  if (showDiversity) {
    traces.push({
      x: data.iterations,
      y: data.diversity,
      type: 'scatter',
      mode: 'lines',
      name: 'Diversity',
      yaxis: 'y2',
      line: {
        color: colors.warning,
        width: 2
      },
      hovertemplate: 'Iteration: %{x}<br>Diversity: %{y:.2f}<extra></extra>'
    });
  }

  const layout: Partial<Plotly.Layout> = {
    height,
    xaxis: {
      title: 'Iteration',
      showgrid: true,
      zeroline: false
    },
    yaxis: {
      title: 'Fitness Score',
      showgrid: true,
      zeroline: false
    },
    ...(showDiversity && {
      yaxis2: {
        title: 'Diversity',
        overlaying: 'y',
        side: 'right',
        range: [0, 1]
      }
    }),
    showlegend: true,
    legend: {
      x: 0,
      y: 1,
      orientation: 'h'
    },
    hovermode: 'x unified',
    margin: { t: 20, r: 50, b: 50, l: 60 }
  };

  const config: Partial<Plotly.Config> = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d']
  };

  return <Plot data={traces} layout={layout} config={config} style={{ width: '100%' }} />;
};
```

---

### IslandHeatmap

```typescript
interface IslandHeatmapProps {
  islands: IslandState[];
  metric: 'best_score' | 'avg_score' | 'diversity';
}

const IslandHeatmap: React.FC<IslandHeatmapProps> = ({ islands, metric }) => {
  const numIslands = islands.length;
  const values = islands.map((island) => island[metric]);

  const data: Plotly.Data[] = [
    {
      z: [values],
      type: 'heatmap',
      colorscale: 'Viridis',
      showscale: true,
      hovertemplate:
        'Island %{x}<br>' +
        `${metric}: %{z:.2f}` +
        '<extra></extra>'
    }
  ];

  const layout: Partial<Plotly.Layout> = {
    height: 150,
    xaxis: {
      title: 'Island',
      tickvals: Array.from({ length: numIslands }, (_, i) => i),
      showgrid: false
    },
    yaxis: {
      showticklabels: false,
      showgrid: false
    },
    margin: { t: 20, r: 100, b: 50, l: 50 }
  };

  return <Plot data={data} layout={layout} style={{ width: '100%' }} />;
};
```

---

## Metric Components

### MetricCard

```typescript
interface MetricCardProps {
  title: string;
  value: number | null | undefined;
  change?: number;
  subtitle?: string;
  icon?: React.ReactNode;
  precision?: number;
  suffix?: string;
  prefix?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  subtitle,
  icon,
  precision = 2,
  suffix,
  prefix
}) => {
  const getTrendIcon = (change: number) => {
    if (change > 0) return <ArrowUpOutlined style={{ color: colors.success }} />;
    if (change < 0) return <ArrowDownOutlined style={{ color: colors.error }} />;
    return null;
  };

  return (
    <Card>
      <Statistic
        title={title}
        value={value ?? '-'}
        precision={value !== null ? precision : 0}
        suffix={suffix}
        prefix={
          <Space>
            {icon}
            {prefix}
          </Space>
        }
        valueStyle={{ fontSize: 24 }}
      />

      {change !== undefined && (
        <Space style={{ marginTop: 8 }}>
          {getTrendIcon(change)}
          <Text type={change >= 0 ? 'success' : 'danger'}>
            {Math.abs(change).toFixed(precision)}
          </Text>
        </Space>
      )}

      {subtitle && (
        <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 8 }}>
          {subtitle}
        </Text>
      )}
    </Card>
  );
};
```

---

### StatusTag

```typescript
interface StatusTagProps {
  status: ExperimentStatus | ProjectStatus;
}

const StatusTag: React.FC<StatusTagProps> = ({ status }) => {
  const config = {
    running: { color: 'success', icon: <SyncOutlined spin /> },
    completed: { color: 'default', icon: <CheckCircleOutlined /> },
    paused: { color: 'warning', icon: <PauseCircleOutlined /> },
    failed: { color: 'error', icon: <CloseCircleOutlined /> },
    stopped: { color: 'default', icon: <StopOutlined /> },
    pending: { color: 'processing', icon: <ClockCircleOutlined /> },
    active: { color: 'success', icon: <CheckCircleOutlined /> },
    draft: { color: 'default', icon: <EditOutlined /> },
    archived: { color: 'default', icon: <InboxOutlined /> }
  };

  const { color, icon } = config[status] || {};

  return (
    <Tag color={color} icon={icon}>
      {status.toUpperCase()}
    </Tag>
  );
};
```

---

## Form Components

### ModelSelector

```typescript
interface ModelSelectorProps {
  models: ModelInfo[];
  value?: string;
  onChange?: (value: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  value,
  onChange
}) => {
  return (
    <Radio.Group value={value} onChange={(e) => onChange?.(e.target.value)}>
      <Space direction="vertical" style={{ width: '100%' }}>
        {models.map((model) => (
          <Radio key={model.id} value={model.id}>
            <Space>
              <Text strong>{model.name}</Text>
              {model.size && <Tag>{model.size}</Tag>}
              {model.loaded && <Badge status="success" text="Loaded" />}
            </Space>
          </Radio>
        ))}
      </Space>
    </Radio.Group>
  );
};
```

---

### ConfigEditor

```typescript
interface ConfigEditorProps {
  config: ExperimentConfig;
  onChange: (config: ExperimentConfig) => void;
}

const ConfigEditor: React.FC<ConfigEditorProps> = ({ config, onChange }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue(config);
  }, [config, form]);

  const handleValuesChange = (changedValues: any, allValues: any) => {
    onChange(allValues);
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onValuesChange={handleValuesChange}
      initialValues={config}
    >
      <Collapse defaultActiveKey={['llm', 'funsearch']}>
        <Collapse.Panel header="LLM Configuration" key="llm">
          <Form.Item name={['llm', 'model']} label="Model">
            <Input />
          </Form.Item>

          <Form.Item name={['llm', 'temperature']} label="Temperature">
            <Slider min={0} max={2} step={0.1} />
          </Form.Item>

          <Form.Item name={['llm', 'max_tokens']} label="Max Tokens">
            <InputNumber min={50} max={4096} />
          </Form.Item>
        </Collapse.Panel>

        <Collapse.Panel header="FunSearch Parameters" key="funsearch">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name={['funsearch', 'samples_per_prompt']}
                label="Samples per Prompt"
              >
                <InputNumber min={1} max={16} />
              </Form.Item>
            </Col>

            <Col span={12}>
              <Form.Item name={['funsearch', 'num_islands']} label="Number of Islands">
                <InputNumber min={1} max={20} />
              </Form.Item>
            </Col>
          </Row>

          {/* More fields... */}
        </Collapse.Panel>

        <Collapse.Panel header="Execution Settings" key="execution">
          <Form.Item name={['execution', 'max_iterations']} label="Max Iterations">
            <InputNumber min={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name={['execution', 'checkpoint_interval']}
            label="Checkpoint Interval"
          >
            <InputNumber min={100} />
          </Form.Item>
        </Collapse.Panel>
      </Collapse>
    </Form>
  );
};
```

---

## Utility Components

### LoadingSpinner

```typescript
interface LoadingSpinnerProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  tip = 'Loading...',
  size = 'default'
}) => {
  return (
    <div style={{ textAlign: 'center', padding: 48 }}>
      <Spin size={size} tip={tip} />
    </div>
  );
};
```

---

### ErrorAlert

```typescript
interface ErrorAlertProps {
  error: Error | string;
  onRetry?: () => void;
  closable?: boolean;
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  closable = true
}) => {
  const message = typeof error === 'string' ? error : error.message;

  return (
    <Alert
      type="error"
      message="Error"
      description={message}
      showIcon
      closable={closable}
      action={
        onRetry && (
          <Button size="small" onClick={onRetry}>
            Retry
          </Button>
        )
      }
    />
  );
};
```

---

## Hooks

### useWebSocket

```typescript
function useWebSocket(experimentId: string) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const callbacksRef = useRef<Map<string, Set<Function>>>(new Map());

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:7351/ws/experiments/${experimentId}`
    );

    ws.onopen = () => {
      setIsConnected(true);
      ws.send(JSON.stringify({
        type: 'subscribe',
        channels: ['metrics', 'islands', 'best_program', 'logs']
      }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      const callbacks = callbacksRef.current.get(message.type);
      if (callbacks) {
        callbacks.forEach((callback) => callback(message));
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [experimentId]);

  const on = useCallback((messageType: string, callback: Function) => {
    if (!callbacksRef.current.has(messageType)) {
      callbacksRef.current.set(messageType, new Set());
    }
    callbacksRef.current.get(messageType)!.add(callback);
  }, []);

  const off = useCallback((messageType: string, callback: Function) => {
    const callbacks = callbacksRef.current.get(messageType);
    if (callbacks) {
      callbacks.delete(callback);
    }
  }, []);

  return { isConnected, on, off };
}
```

---

### useExperimentMonitor

```typescript
function useExperimentMonitor(experimentId: string) {
  const { data: experiment, refetch } = useQuery(
    ['experiment', experimentId],
    () => api.getExperiment(experimentId)
  );

  const [liveMetrics, setLiveMetrics] = useState<MetricPoint[]>([]);
  const ws = useWebSocket(experimentId);

  useEffect(() => {
    ws.on('metrics_update', (message: WSMetricsUpdate) => {
      setLiveMetrics((prev) => [...prev, message.data].slice(-1000));
    });

    ws.on('status_change', () => {
      refetch();
    });

    return () => {
      ws.off('metrics_update', () => {});
      ws.off('status_change', () => {});
    };
  }, [ws, refetch]);

  return {
    experiment,
    liveMetrics,
    isConnected: ws.isConnected
  };
}
```

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Component Specification
