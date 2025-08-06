import React, { useState } from 'react';
import {
  Form,
  Input,
  Select,
  InputNumber,
  Button,
  Card,
  Row,
  Col,
  Space,
  Divider,
  AutoComplete,
  message,
} from 'antd';
import { PlusOutlined, MinusCircleOutlined, SendOutlined } from '@ant-design/icons';
import { UserBackground } from '../services/api';

const { Option } = Select;
const { TextArea } = Input;

interface UserFormProps {
  onSubmit: (data: UserBackground) => void;
  loading?: boolean;
}

// 预定义选项
const UNIVERSITIES = [
  '北京大学', '清华大学', '复旦大学', '上海交通大学', '南京大学', '浙江大学',
  '中国科学技术大学', '哈尔滨工业大学', '西安交通大学', '北京邮电大学',
  '北京理工大学', '北京航空航天大学', '华中科技大学', '中山大学', '华南理工大学',
  '山东大学', '四川大学', '大连理工大学', '东南大学', '天津大学', '南开大学',
  '深圳大学', '华东师范大学', '同济大学', '厦门大学', '中南大学', '湖南大学',
];

const MAJORS = [
  '计算机科学与技术', '软件工程', '网络工程', '信息安全', '数据科学与大数据技术',
  '人工智能', '物联网工程', '电子信息工程', '通信工程', '电气工程及其自动化',
  '自动化', '电子科学与技术', '机械工程', '机械设计制造及其自动化',
  '金融学', '经济学', '国际经济与贸易', '工商管理', '市场营销', '会计学',
];

const COUNTRIES = [
  '美国', '英国', '加拿大', '澳大利亚', '新加坡', '香港', '德国', '法国', '日本', '韩国',
];

const TARGET_MAJORS = [
  '计算机科学', '数据科学', '人工智能', '软件工程', '电子工程', '机械工程',
  '金融', '商业分析', '管理学', '经济学',
];

const UserForm: React.FC<UserFormProps> = ({ onSubmit, loading = false }) => {
  const [form] = Form.useForm();
  const [hasLanguageScore, setHasLanguageScore] = useState(false);
  const [hasGRE, setHasGRE] = useState(false);
  const [hasGMAT, setHasGMAT] = useState(false);

  const handleSubmit = (values: any) => {
    try {
      // 处理表单数据
      const formData: UserBackground = {
        undergraduate_university: values.undergraduate_university,
        undergraduate_major: values.undergraduate_major,
        gpa: values.gpa,
        gpa_scale: values.gpa_scale,
        graduation_year: values.graduation_year,
        target_countries: values.target_countries,
        target_majors: values.target_majors,
        target_degree_type: values.target_degree_type,
        research_experiences: values.research_experiences || [],
        internship_experiences: values.internship_experiences || [],
        other_experiences: values.other_experiences || [],
      };

      // 添加语言成绩
      if (hasLanguageScore && values.language_test_type && values.language_total_score) {
        formData.language_test_type = values.language_test_type;
        formData.language_total_score = values.language_total_score;
        formData.language_reading = values.language_reading;
        formData.language_listening = values.language_listening;
        formData.language_speaking = values.language_speaking;
        formData.language_writing = values.language_writing;
      }

      // 添加GRE成绩
      if (hasGRE && values.gre_total) {
        formData.gre_total = values.gre_total;
        formData.gre_verbal = values.gre_verbal;
        formData.gre_quantitative = values.gre_quantitative;
        formData.gre_writing = values.gre_writing;
      }

      // 添加GMAT成绩
      if (hasGMAT && values.gmat_total) {
        formData.gmat_total = values.gmat_total;
      }

      console.log('Form data:', formData);
      onSubmit(formData);
    } catch (error) {
      message.error('表单数据处理失败，请检查输入');
      console.error('Form submission error:', error);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '20px' }}>
      <Card title="留学定位与选校规划 - 个人信息填写">
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          scrollToFirstError
        >
          {/* 第一部分：学术背景 */}
          <Card type="inner" title="第一部分：学术背景" style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="本科院校"
                  name="undergraduate_university"
                  rules={[{ required: true, message: '请输入本科院校' }]}
                >
                  <AutoComplete
                    options={UNIVERSITIES.map(uni => ({ value: uni }))}
                    placeholder="请输入或选择本科院校"
                    filterOption={(inputValue, option) =>
                      option!.value.toUpperCase().indexOf(inputValue.toUpperCase()) !== -1
                    }
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="本科专业"
                  name="undergraduate_major"
                  rules={[{ required: true, message: '请输入本科专业' }]}
                >
                  <AutoComplete
                    options={MAJORS.map(major => ({ value: major }))}
                    placeholder="请输入或选择本科专业"
                    filterOption={(inputValue, option) =>
                      option!.value.toUpperCase().indexOf(inputValue.toUpperCase()) !== -1
                    }
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="GPA/均分"
                  name="gpa"
                  rules={[{ required: true, message: '请输入GPA或均分' }]}
                >
                  <InputNumber
                    min={0}
                    max={100}
                    step={0.1}
                    placeholder="如：3.8 或 88"
                    style={{ width: '100%' }}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="GPA制式"
                  name="gpa_scale"
                  rules={[{ required: true, message: '请选择GPA制式' }]}
                >
                  <Select placeholder="请选择制式">
                    <Option value="4.0">4.0制</Option>
                    <Option value="5.0">5.0制</Option>
                    <Option value="100">100分制</Option>
                  </Select>
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="毕业年份"
                  name="graduation_year"
                  rules={[{ required: true, message: '请选择毕业年份' }]}
                >
                  <Select placeholder="请选择毕业年份">
                    {Array.from({ length: 10 }, (_, i) => {
                      const year = new Date().getFullYear() + i - 5;
                      return <Option key={year} value={year}>{year}</Option>;
                    })}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

          {/* 第二部分：语言和标准化考试成绩 */}
          <Card type="inner" title="第二部分：语言和标准化考试成绩（选填）" style={{ marginBottom: 24 }}>
            <Form.Item label="语言考试成绩">
              <Button
                type={hasLanguageScore ? 'primary' : 'default'}
                onClick={() => setHasLanguageScore(!hasLanguageScore)}
              >
                {hasLanguageScore ? '已添加语言成绩' : '添加语言成绩'}
              </Button>
            </Form.Item>

            {hasLanguageScore && (
              <Row gutter={16}>
                <Col xs={24} sm={6}>
                  <Form.Item label="考试类型" name="language_test_type">
                    <Select placeholder="选择考试类型">
                      <Option value="TOEFL">TOEFL</Option>
                      <Option value="IELTS">IELTS</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={6}>
                  <Form.Item label="总分" name="language_total_score">
                    <InputNumber min={0} max={120} placeholder="总分" style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={3}>
                  <Form.Item label="阅读" name="language_reading">
                    <InputNumber min={0} max={30} placeholder="阅读" style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={3}>
                  <Form.Item label="听力" name="language_listening">
                    <InputNumber min={0} max={30} placeholder="听力" style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={3}>
                  <Form.Item label="口语" name="language_speaking">
                    <InputNumber min={0} max={30} placeholder="口语" style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={3}>
                  <Form.Item label="写作" name="language_writing">
                    <InputNumber min={0} max={30} placeholder="写作" style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
            )}

            <Row gutter={16}>
              <Col xs={24} sm={12}>
                <Form.Item label="GRE成绩">
                  <Button
                    type={hasGRE ? 'primary' : 'default'}
                    onClick={() => setHasGRE(!hasGRE)}
                  >
                    {hasGRE ? '已添加GRE成绩' : '添加GRE成绩'}
                  </Button>
                </Form.Item>
                {hasGRE && (
                  <Row gutter={8}>
                    <Col span={12}>
                      <Form.Item label="总分" name="gre_total">
                        <InputNumber min={260} max={340} placeholder="总分" style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item label="写作" name="gre_writing">
                        <InputNumber min={0} max={6} step={0.5} placeholder="写作" style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>
                )}
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item label="GMAT成绩">
                  <Button
                    type={hasGMAT ? 'primary' : 'default'}
                    onClick={() => setHasGMAT(!hasGMAT)}
                  >
                    {hasGMAT ? '已添加GMAT成绩' : '添加GMAT成绩'}
                  </Button>
                </Form.Item>
                {hasGMAT && (
                  <Form.Item label="总分" name="gmat_total">
                    <InputNumber min={200} max={800} placeholder="GMAT总分" style={{ width: '100%' }} />
                  </Form.Item>
                )}
              </Col>
            </Row>
          </Card>

          {/* 第三部分：申请意向 */}
          <Card type="inner" title="第三部分：申请意向" style={{ marginBottom: 24 }}>
            <Row gutter={16}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="目标国家/地区 (可多选)"
                  name="target_countries"
                  rules={[{ required: true, message: '请选择目标国家/地区' }]}
                >
                  <Select
                    mode="multiple"
                    placeholder="请选择目标国家/地区"
                    options={COUNTRIES.map(country => ({ label: country, value: country }))}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="目标专业方向 (可多选)"
                  name="target_majors"
                  rules={[{ required: true, message: '请选择目标专业方向' }]}
                >
                  <Select
                    mode="multiple"
                    placeholder="请选择目标专业方向"
                    options={TARGET_MAJORS.map(major => ({ label: major, value: major }))}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              label="目标学位类型"
              name="target_degree_type"
              rules={[{ required: true, message: '请选择目标学位类型' }]}
            >
              <Select placeholder="请选择学位类型">
                <Option value="Master">硕士 (Master)</Option>
                <Option value="PhD">博士 (PhD)</Option>
              </Select>
            </Form.Item>
          </Card>

          {/* 第四部分：实践背景 */}
          <Card type="inner" title="第四部分：实践背景（选填）" style={{ marginBottom: 24 }}>
            {/* 科研经历 */}
            <Form.Item label="科研经历">
              <Form.List name="research_experiences">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Card key={key} size="small" style={{ marginBottom: 8 }}>
                        <Row gutter={16}>
                          <Col xs={24} sm={8}>
                            <Form.Item
                              {...restField}
                              name={[name, 'name']}
                              label="项目名称"
                            >
                              <Input placeholder="项目名称" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={8}>
                            <Form.Item
                              {...restField}
                              name={[name, 'role']}
                              label="担任角色"
                            >
                              <Input placeholder="如：核心成员、负责人" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={6}>
                            <Form.Item
                              {...restField}
                              name={[name, 'description']}
                              label="项目描述"
                            >
                              <TextArea rows={2} placeholder="简要描述项目内容和成果" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={2}>
                            <MinusCircleOutlined onClick={() => remove(name)} />
                          </Col>
                        </Row>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加科研经历
                    </Button>
                  </>
                )}
              </Form.List>
            </Form.Item>

            <Divider />

            {/* 实习经历 */}
            <Form.Item label="实习/工作经历">
              <Form.List name="internship_experiences">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Card key={key} size="small" style={{ marginBottom: 8 }}>
                        <Row gutter={16}>
                          <Col xs={24} sm={8}>
                            <Form.Item
                              {...restField}
                              name={[name, 'company']}
                              label="公司名称"
                            >
                              <Input placeholder="公司名称" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={8}>
                            <Form.Item
                              {...restField}
                              name={[name, 'position']}
                              label="职位"
                            >
                              <Input placeholder="实习/工作职位" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={6}>
                            <Form.Item
                              {...restField}
                              name={[name, 'description']}
                              label="工作描述"
                            >
                              <TextArea rows={2} placeholder="简要描述工作内容和成果" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={2}>
                            <MinusCircleOutlined onClick={() => remove(name)} />
                          </Col>
                        </Row>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加实习/工作经历
                    </Button>
                  </>
                )}
              </Form.List>
            </Form.Item>

            <Divider />

            {/* 其他经历 */}
            <Form.Item label="其他经历（竞赛、活动等）">
              <Form.List name="other_experiences">
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(({ key, name, ...restField }) => (
                      <Card key={key} size="small" style={{ marginBottom: 8 }}>
                        <Row gutter={16}>
                          <Col xs={24} sm={10}>
                            <Form.Item
                              {...restField}
                              name={[name, 'name']}
                              label="活动名称"
                            >
                              <Input placeholder="竞赛、活动名称" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={12}>
                            <Form.Item
                              {...restField}
                              name={[name, 'description']}
                              label="描述"
                            >
                              <TextArea rows={2} placeholder="简要描述活动内容和收获" />
                            </Form.Item>
                          </Col>
                          <Col xs={24} sm={2}>
                            <MinusCircleOutlined onClick={() => remove(name)} />
                          </Col>
                        </Row>
                      </Card>
                    ))}
                    <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                      添加其他经历
                    </Button>
                  </>
                )}
              </Form.List>
            </Form.Item>
          </Card>

          {/* 提交按钮 */}
          <Form.Item>
            <Space size="large" style={{ width: '100%', justifyContent: 'center' }}>
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                icon={<SendOutlined />}
                loading={loading}
                disabled={loading}
              >
                {loading ? '正在分析中...' : '完成并开始分析'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default UserForm;