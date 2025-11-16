// Home page - Project list

import React from 'react';
import { Card, Row, Col, Button, Empty, Spin, Statistic, Tag, Typography, Space } from 'antd';
import { PlusOutlined, ExperimentOutlined, TrophyOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { projectsApi } from '@/api';
import { getStatusColor } from '@/config/theme';
import type { Project } from '@/types';

const { Title, Text } = Typography;

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  });

  const projects = data?.projects || [];

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="Loading projects..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <Empty
          description="Failed to load projects"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="primary" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Empty>
      </Card>
    );
  }

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
        <Title level={2} style={{ margin: 0 }}>
          Projects
        </Title>
        <Button type="primary" icon={<PlusOutlined />} size="large">
          New Project
        </Button>
      </div>

      {projects.length === 0 ? (
        <Card>
          <Empty
            description="No projects yet"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" icon={<PlusOutlined />}>
              Create Your First Project
            </Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {projects.map((project: Project) => (
            <Col xs={24} sm={12} lg={8} key={project.id}>
              <Card
                hoverable
                onClick={() => navigate(`/projects/${project.id}`)}
                style={{ height: '100%' }}
              >
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <div>
                    <Title level={4} style={{ marginBottom: 8 }}>
                      {project.name}
                    </Title>
                    <Tag color={getStatusColor(project.status)}>
                      {project.status.toUpperCase()}
                    </Tag>
                  </div>

                  <Text type="secondary" ellipsis>
                    {project.description || 'No description'}
                  </Text>

                  <div>
                    <Tag>{project.problem_type}</Tag>
                  </div>

                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic
                        title="Experiments"
                        value={project.experiment_count}
                        prefix={<ExperimentOutlined />}
                        valueStyle={{ fontSize: 18 }}
                      />
                    </Col>
                    <Col span={12}>
                      {project.best_score !== null ? (
                        <Statistic
                          title="Best Score"
                          value={project.best_score}
                          precision={2}
                          prefix={<TrophyOutlined />}
                          valueStyle={{ fontSize: 18 }}
                        />
                      ) : (
                        <Statistic
                          title="Best Score"
                          value="-"
                          valueStyle={{ fontSize: 18 }}
                        />
                      )}
                    </Col>
                  </Row>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default HomePage;
