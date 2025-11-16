// Project detail page

import React from 'react';
import {
  Card,
  Button,
  Space,
  Tabs,
  Table,
  Tag,
  Progress,
  Typography,
  Spin,
  Empty,
} from 'antd';
import { ArrowLeftOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate, useParams } from 'react-router-dom';
import { projectsApi, experimentsApi } from '@/api';
import { getStatusColor } from '@/config/theme';
import type { Experiment } from '@/types';

const { Title, Text } = Typography;

const ProjectDetailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: experimentsData } = useQuery({
    queryKey: ['experiments', projectId],
    queryFn: () => experimentsApi.list(projectId!),
    enabled: !!projectId,
  });

  const experiments = experimentsData?.experiments || [];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading project..." />
      </div>
    );
  }

  if (!project) {
    return (
      <Card>
        <Empty description="Project not found" />
      </Card>
    );
  }

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Experiment) => (
        <Button
          type="link"
          onClick={() =>
            navigate(`/projects/${projectId}/experiments/${record.id}`)
          }
        >
          {name}
        </Button>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Model',
      key: 'model',
      render: (_: any, record: Experiment) => (
        <Tag>{record.config.llm.model}</Tag>
      ),
    },
    {
      title: 'Best Score',
      dataIndex: 'best_score',
      key: 'best_score',
      align: 'right' as const,
      render: (score: number | null) =>
        score !== null ? <Text strong>{score.toFixed(2)}</Text> : '-',
    },
    {
      title: 'Progress',
      key: 'progress',
      render: (_: any, record: Experiment) => {
        const percent =
          (record.iterations_completed / record.config.execution.max_iterations) *
          100;
        return (
          <Progress
            percent={Math.min(percent, 100)}
            size="small"
            status={record.status === 'failed' ? 'exception' : 'active'}
          />
        );
      },
    },
  ];

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
            onClick={() => navigate('/')}
          >
            Back to Projects
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            {project.name}
          </Title>
          <Tag color={getStatusColor(project.status)}>
            {project.status.toUpperCase()}
          </Tag>
        </Space>
        <Button type="primary" icon={<PlayCircleOutlined />} size="large">
          New Experiment
        </Button>
      </div>

      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>Description:</Text>{' '}
            <Text>{project.description || 'No description'}</Text>
          </div>
          <div>
            <Text strong>Problem Type:</Text> <Tag>{project.problem_type}</Tag>
          </div>
          <div>
            <Text strong>Experiments:</Text> {project.experiment_count}
          </div>
          {project.best_score !== null && (
            <div>
              <Text strong>Best Score:</Text>{' '}
              <Text strong style={{ fontSize: 18, color: '#52c41a' }}>
                {project.best_score.toFixed(2)}
              </Text>
            </div>
          )}
        </Space>
      </Card>

      <Tabs
        defaultActiveKey="experiments"
        items={[
          {
            key: 'experiments',
            label: 'Experiments',
            children: (
              <Card>
                {experiments.length === 0 ? (
                  <Empty
                    description="No experiments yet"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  >
                    <Button type="primary" icon={<PlayCircleOutlined />}>
                      Start First Experiment
                    </Button>
                  </Empty>
                ) : (
                  <Table
                    dataSource={experiments}
                    columns={columns}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                  />
                )}
              </Card>
            ),
          },
          {
            key: 'configuration',
            label: 'Configuration',
            children: (
              <Card>
                <Text type="secondary">Configuration details coming soon...</Text>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default ProjectDetailPage;
