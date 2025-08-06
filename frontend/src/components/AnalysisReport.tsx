import React, { useRef } from 'react';
import {
  Card,
  Row,
  Col,
  Tabs,
  Tag,
  Timeline,
  Button,
  Divider,
  Typography,
  Space,
  Alert,
  Collapse,
} from 'antd';
import {
  DownloadOutlined,
  TrophyOutlined,
  WarningOutlined,
  BookOutlined,
  UserOutlined,
  RocketOutlined,
  SafetyOutlined,
  AimOutlined,
} from '@ant-design/icons';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { AnalysisReport as AnalysisReportType } from '../services/api';

// 注册Chart.js组件
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

interface AnalysisReportProps {
  report: AnalysisReportType;
  onBack: () => void;
}

const AnalysisReport: React.FC<AnalysisReportProps> = ({ report, onBack }) => {
  const reportRef = useRef<HTMLDivElement>(null);

  // 雷达图数据（模拟数据，实际应该从报告中计算）
  const radarData = {
    labels: ['学术能力', '语言能力', '科研背景', '实习背景', '院校背景'],
    datasets: [
      {
        label: '综合竞争力',
        data: [75, 60, 45, 50, 80], // 这里应该根据实际数据计算
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
      },
    ],
  };

  const radarOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
        },
      },
    },
  };

  // 下载PDF功能
  const downloadPDF = async () => {
    if (!reportRef.current) return;

    try {
      const canvas = await html2canvas(reportRef.current, {
        useCORS: true,
        allowTaint: true,
        width: reportRef.current.scrollWidth * 2,
        height: reportRef.current.scrollHeight * 2,
      } as any);

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const imgWidth = 210;
      const pageHeight = 295;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;

      let position = 0;

      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      pdf.save('留学分析报告.pdf');
    } catch (error) {
      console.error('PDF生成失败:', error);
    }
  };

  const renderSchoolRecommendations = () => (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}>
        <Card
          title={
            <Space>
              <RocketOutlined style={{ color: '#ff4d4f' }} />
              冲刺院校 (Reach)
            </Space>
          }
          size="small"
        >
          {report.school_recommendations.reach.map((school, index) => (
            <Card key={index} type="inner" size="small" style={{ marginBottom: 8 }}>
              <Title level={5}>{school.university}</Title>
              <Text type="secondary">{school.program}</Text>
              <Paragraph style={{ marginTop: 8, fontSize: '12px' }}>
                {school.reason}
              </Paragraph>
            </Card>
          ))}
        </Card>
      </Col>

      <Col xs={24} lg={8}>
        <Card
          title={
            <Space>
              <AimOutlined style={{ color: '#1890ff' }} />
              匹配院校 (Target)
            </Space>
          }
          size="small"
        >
          {report.school_recommendations.target.map((school, index) => (
            <Card key={index} type="inner" size="small" style={{ marginBottom: 8 }}>
              <Title level={5}>{school.university}</Title>
              <Text type="secondary">{school.program}</Text>
              <Paragraph style={{ marginTop: 8, fontSize: '12px' }}>
                {school.reason}
              </Paragraph>
            </Card>
          ))}
        </Card>
      </Col>

      <Col xs={24} lg={8}>
        <Card
          title={
            <Space>
              <SafetyOutlined style={{ color: '#52c41a' }} />
              保底院校 (Safety)
            </Space>
          }
          size="small"
        >
          {report.school_recommendations.safety.map((school, index) => (
            <Card key={index} type="inner" size="small" style={{ marginBottom: 8 }}>
              <Title level={5}>{school.university}</Title>
              <Text type="secondary">{school.program}</Text>
              <Paragraph style={{ marginTop: 8, fontSize: '12px' }}>
                {school.reason}
              </Paragraph>
            </Card>
          ))}
        </Card>
      </Col>
    </Row>
  );

  const renderSimilarCases = () => (
    <Row gutter={[16, 16]}>
      {report.similar_cases.map((caseItem, index) => (
        <Col xs={24} lg={12} key={index}>
          <Card
            title={`案例 ${index + 1}: ${caseItem.admitted_university}`}
            size="small"
            extra={<Tag color="blue">{caseItem.admitted_program}</Tag>}
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>基本信息：</Text>
                <br />
                <Text>GPA: {caseItem.gpa} | 语言: {caseItem.language_score}</Text>
                {caseItem.language_test_type && (
                  <>
                    <br />
                    <Text>语言考试类型: <Tag color="blue">{caseItem.language_test_type}</Tag></Text>
                  </>
                )}
                <br />
                <Text type="secondary">{caseItem.undergraduate_info}</Text>
              </div>

              {caseItem.key_experiences && (
                <div>
                  <Text strong>主要经历：</Text>
                  <br />
                  <Text type="secondary">{caseItem.key_experiences}</Text>
                </div>
              )}

              <Collapse size="small">
                <Panel header="详细对比分析" key="1">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>GPA对比：</Text>
                      <Paragraph>{caseItem.comparison.gpa}</Paragraph>
                    </div>
                    <div>
                      <Text strong>院校对比：</Text>
                      <Paragraph>{caseItem.comparison.university}</Paragraph>
                    </div>
                    <div>
                      <Text strong>经历对比：</Text>
                      <Paragraph>{caseItem.comparison.experience}</Paragraph>
                    </div>
                    <div>
                      <Text strong>成功因素：</Text>
                      <Paragraph>{caseItem.success_factors}</Paragraph>
                    </div>
                    <div>
                      <Text strong>可借鉴经验：</Text>
                      <Paragraph>{caseItem.takeaways}</Paragraph>
                    </div>
                  </Space>
                </Panel>
              </Collapse>
            </Space>
          </Card>
        </Col>
      ))}
    </Row>
  );

  const renderBackgroundImprovement = () => {
    if (!report.background_improvement) {
      return <Alert message="背景提升建议暂时无法生成" type="info" />;
    }

    return (
      <Space direction="vertical" style={{ width: '100%' }}>
        <Timeline>
          {report.background_improvement.action_plan.map((plan, index) => (
            <Timeline.Item key={index}>
              <Card size="small">
                <Title level={5}>{plan.timeframe}</Title>
                <Paragraph>
                  <Text strong>行动计划：</Text>
                  {plan.action}
                </Paragraph>
                <Paragraph>
                  <Text strong>预期目标：</Text>
                  {plan.goal}
                </Paragraph>
              </Card>
            </Timeline.Item>
          ))}
        </Timeline>

        <Divider />

        <Card title="总体策略建议" size="small">
          <Paragraph>{report.background_improvement.strategy_summary}</Paragraph>
        </Card>
      </Space>
    );
  };

  const tabItems = [
    {
      key: '1',
      label: (
        <Space>
          <UserOutlined />
          竞争力评估
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Card title="综合竞争力雷达图" size="small">
              <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Radar data={radarData} options={radarOptions} />
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Card
                title={
                  <Space>
                    <TrophyOutlined style={{ color: '#52c41a' }} />
                    核心优势
                  </Space>
                }
                size="small"
              >
                <Paragraph>{report.competitiveness.strengths}</Paragraph>
              </Card>

              <Card
                title={
                  <Space>
                    <WarningOutlined style={{ color: '#faad14' }} />
                    主要短板
                  </Space>
                }
                size="small"
              >
                <Paragraph>{report.competitiveness.weaknesses}</Paragraph>
              </Card>
            </Space>
          </Col>
          <Col xs={24}>
            <Card title="综合评价" size="small">
              <Paragraph>{report.competitiveness.summary}</Paragraph>
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: '2',
      label: (
        <Space>
          <BookOutlined />
          选校建议
        </Space>
      ),
      children: (
        <Space direction="vertical" style={{ width: '100%' }}>
          {renderSchoolRecommendations()}
          <Divider />
          <Card title="案例透视" size="small">
            <Paragraph>{report.school_recommendations.case_insights}</Paragraph>
          </Card>
        </Space>
      ),
    },
    {
      key: '3',
      label: (
        <Space>
          <UserOutlined />
          相似案例
        </Space>
      ),
      children: renderSimilarCases(),
    },
    {
      key: '4',
      label: (
        <Space>
          <RocketOutlined />
          背景提升
        </Space>
      ),
      children: renderBackgroundImprovement(),
    },
  ];

  return (
    <div style={{ maxWidth: 1400, margin: '0 auto', padding: '20px' }}>
      <div ref={reportRef}>
        <Card
          title="留学定位与选校规划分析报告"
          extra={
            <Space>
              <Button type="primary" icon={<DownloadOutlined />} onClick={downloadPDF}>
                下载PDF报告
              </Button>
              <Button onClick={onBack}>返回修改</Button>
            </Space>
          }
        >
          <Tabs items={tabItems} size="large" />
        </Card>
      </div>
    </div>
  );
};

export default AnalysisReport;