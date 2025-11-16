// Experiment monitor page - Real-time monitoring

import React from 'react';
import {
  Card,
  Button,
  Space,
  Statistic,
  Row,
  Col,
  Tag,
  Typography,
  Spin,
  Empty,
} from 'antd';
import {
  ArrowLeftOutlined,
  TrophyOutlined,
  StarOutlined,
  BranchesOutlined,
  PauseOutlined,
  StopOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { experimentsApi } from '@/api';
import { getStatusColor } from '@/config/theme';

const { Title, Text } = Typography;

const ExperimentMonitorPage: React.FC = () => {
  const { projectId, experimentId } = useParams<{
    projectId: string;
    experimentId: string;
  }>();
  const navigate = useNavigate();

  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', experimentId],
    queryFn: () => experimentsApi.get(experimentId!),
    enabled: !!experimentId,
    refetchInterval: 5000, // Refetch every 5 seconds for running experiments
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading experiment..." />
      </div>
    );
  }

  if (!experiment) {
    return (
      <Card>
        <Empty description="Experiment not found" />
      </Card>
    );
  }

  const progress =
    (experiment.iterations_completed / experiment.config.execution.max_iterations) *
    100;

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 24,
        }}
      >
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/projects/${projectId}`)}
          >
            Back to Project
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            {experiment.name}
          </Title>
          <Tag color={getStatusColor(experiment.status)}>
            {experiment.status.toUpperCase()}
          </Tag>
        </Space>
        <Space>
          {experiment.status === 'running' && (
            <>
              <Button icon={<PauseOutlined />}>Pause</Button>
              <Button danger icon={<StopOutlined />}>
                Stop
              </Button>
            </>
          )}
        </Space>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Model:</Text> <Tag>{experiment.config.llm.model}</Tag>
          </div>
          <div>
            <Text strong>Progress:</Text> {experiment.iterations_completed} /{' '}
            {experiment.config.execution.max_iterations} iterations ({progress.toFixed(1)}%)
          </div>
        </Space>
      </Card>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Current Score"
              value={experiment.current_score ?? '-'}
              precision={2}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Best Score"
              value={experiment.best_score ?? '-'}
              precision={2}
              prefix={<StarOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="Islands"
              value={experiment.config.funsearch.num_islands}
              prefix={<BranchesOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Fitness Evolution" style={{ marginBottom: 24 }}>
        <div
          style={{
            height: 400,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#fafafa',
            borderRadius: 4,
          }}
        >
          <Text type="secondary">
            Chart will be displayed here (Plotly.js integration)
          </Text>
        </div>
      </Card>

      <Card title="Island States" style={{ marginBottom: 24 }}>
        <div
          style={{
            height: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#fafafa',
            borderRadius: 4,
          }}
        >
          <Text type="secondary">Island visualization will be displayed here</Text>
        </div>
      </Card>

      {experiment.best_program && (
        <Card title="Best Program">
          <pre
            style={{
              background: '#f5f5f5',
              padding: 16,
              borderRadius: 4,
              overflow: 'auto',
            }}
          >
            <code>{experiment.best_program}</code>
          </pre>
        </Card>
      )}
    </div>
  );
};

export default ExperimentMonitorPage;
