// Sidebar navigation menu

import React from 'react';
import { Menu } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  AppstoreOutlined,
  SettingOutlined,
} from '@ant-design/icons';

const MainMenu: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Projects',
    },
    {
      key: '/templates',
      icon: <AppstoreOutlined />,
      label: 'Templates',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      disabled: true, // Coming soon
    },
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
};

export default MainMenu;
