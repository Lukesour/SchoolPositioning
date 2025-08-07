import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MajorDataProcessor:
    """专业数据处理类"""
    
    def __init__(self):
        self.invalid_entries = [
            "普通高等学校本科专业目录",
            "一、 《普通高等学校本科专业目录》 是高等教育工作的基",
            "设置和调整专业、实施人才培养、安排招生、授予学位、指",
            "是指学科基础比较成熟、社会需求相对稳定、布点数量相对",
            "四、专业目录所列专业，除已注明者外，均按所在学科",
            "门类授予相应的学位。对已注明了学位授予门类的专业，按",
            "照注明的学科门类授予相应的学位；可授两种（或以上）学",
            "位门类的专业，原则上由有关高等学校 在设置专业布点时 确",
            "年限由有关高等学校在设置专业布点时确定， 专业目录不再",
            "学科门类：经济学",
            "学科门类：哲学",
            "学科门类：法学",
            "学科门类：教育学",
            "学科门类：文学",
            "学科门类：历史学",
            "学科门类：理学",
            "学科门类：工学",
            "学科门类：农学",
            "学科门类：医学",
            "学科门类：管理学",
            "学科门类：艺术学"
        ]
    
    def clean_major_name(self, major_name: str) -> str:
        """
        清洗专业名称
        
        清洗规则：
        1. 移除无效前缀：清除专业名称字符串开头的所有单个大写字母
        2. 移除备注信息：清除专业名称末尾的括号及其内部的所有文字
        """
        if not major_name or not isinstance(major_name, str):
            return ""
        
        # 移除开头的单个大写字母前缀（如 T080901 中的 T，K  宗教学 中的 K）
        # 匹配开头的单个大写字母，后面可能跟着空格和数字
        cleaned = re.sub(r'^[A-Z]\s*\d*', '', major_name)
        
        # 移除开头的多个大写字母组合（如 TK   国际税收 中的 TK）
        cleaned = re.sub(r'^[A-Z]{2,}\s*', '', cleaned)
        
        # 进一步清理：移除开头的单个大写字母+多个空格的情况
        cleaned = re.sub(r'^[A-Z]\s{2,}', '', cleaned)
        
        # 如果正则替换后字符串为空，说明原字符串就是字母+数字的格式
        # 这种情况下，我们需要保留原始字符串
        if not cleaned.strip():
            cleaned = major_name
        
        # 移除末尾的括号及其内容（包括中文括号和英文括号）
        # 匹配末尾的括号，包括 () 和 （）
        cleaned = re.sub(r'[（(][^）)]*[）)]$', '', cleaned)
        
        # 移除末尾的括号（如果只有左括号或右括号）
        cleaned = re.sub(r'[（(][^）)]*$', '', cleaned)
        cleaned = re.sub(r'^[^（(]*[）)]', '', cleaned)
        
        # 清理多余的空格
        cleaned = cleaned.strip()
        
        return cleaned
    
    def is_valid_major(self, major_name: str) -> bool:
        """判断是否为有效的专业名称"""
        if not major_name or not isinstance(major_name, str):
            return False
        
        # 检查是否在无效条目列表中
        if major_name in self.invalid_entries:
            return False
        
        # 检查是否为空或只包含空格
        if not major_name.strip():
            return False
        
        # 检查是否包含明显的无效内容
        invalid_patterns = [
            r'^学科门类：',
            r'^年\d+月$',
            r'^[A-Z]\s*$',  # 单个大写字母
            r'^\d+$',  # 纯数字
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, major_name.strip()):
                return False
        
        return True
    
    def process_majors_data(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """
        处理专业数据
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            处理结果统计
        """
        try:
            # 读取原始数据
            with open(input_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            logger.info(f"读取到 {len(raw_data)} 条原始专业数据")
            
            # 清洗数据
            cleaned_majors = []
            removed_count = 0
            
            for item in raw_data:
                if isinstance(item, dict) and 'name' in item:
                    major_name = item.get('name', '')
                    cleaned_name = self.clean_major_name(major_name)
                    
                    if self.is_valid_major(cleaned_name):
                        cleaned_item = {
                            'code': item.get('code', ''),
                            'name': cleaned_name,
                            'category': item.get('category', ''),
                            'subcategory': item.get('subcategory', '')
                        }
                        cleaned_majors.append(cleaned_item)
                    else:
                        removed_count += 1
                        logger.debug(f"移除无效专业: {major_name}")
            
            # 去重（基于专业名称）
            unique_majors = []
            seen_names = set()
            
            for item in cleaned_majors:
                if item['name'] not in seen_names:
                    unique_majors.append(item)
                    seen_names.add(item['name'])
            
            # 保存清洗后的数据
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_majors, f, ensure_ascii=False, indent=2)
            
            # 生成统计信息
            stats = {
                'original_count': len(raw_data),
                'cleaned_count': len(cleaned_majors),
                'unique_count': len(unique_majors),
                'removed_count': removed_count,
                'duplicate_removed': len(cleaned_majors) - len(unique_majors)
            }
            
            logger.info(f"数据清洗完成:")
            logger.info(f"  原始数据: {stats['original_count']} 条")
            logger.info(f"  清洗后: {stats['cleaned_count']} 条")
            logger.info(f"  去重后: {stats['unique_count']} 条")
            logger.info(f"  移除无效: {stats['removed_count']} 条")
            logger.info(f"  移除重复: {stats['duplicate_removed']} 条")
            
            return stats
            
        except Exception as e:
            logger.error(f"处理专业数据时出错: {str(e)}")
            raise
    
    def generate_frontend_data(self, processed_majors_file: str, frontend_data_file: str):
        """
        生成前端数据文件，包含专业分类信息
        """
        try:
            # 读取清洗后的专业数据
            with open(processed_majors_file, 'r', encoding='utf-8') as f:
                processed_majors = json.load(f)
            
            # 读取现有的前端数据
            frontend_data = {}
            if Path(frontend_data_file).exists():
                with open(frontend_data_file, 'r', encoding='utf-8') as f:
                    frontend_data = json.load(f)
            
            # 提取专业名称列表
            major_names = [item['name'] for item in processed_majors if item['name']]
            
            # 定义专业分类
            major_categories = {
                "商科": ["不限", "金工金数", "金融", "商业分析", "经济", "会计", "市场营销", "信息系统", "管理", "人力资源管理", "供应链管理", "创业与创新", "房地产", "旅游酒店管理", "工商管理", "其他商科"],
                "社科": ["不限", "教育", "建筑", "法律", "社会学与社工", "国际关系", "哲学", "历史", "公共政策与事务", "艺术", "公共卫生", "心理学", "体育", "药学", "医学", "新闻", "影视", "文化", "媒体与传播", "新媒体", "媒介与社会", "科学传播", "策略传播", "媒体产业", "语言", "其他社科"],
                "工科": ["不限", "计算机", "电气电子", "数据科学", "机械工程", "材料", "化工", "生物工程", "土木工程", "工程管理", "环境工程", "工业工程", "能源", "航空工程", "地球科学", "交通运输", "海洋技术", "食品科学", "其他工科"],
                "理科": ["不限", "物理", "化学", "数学", "生物"]
            }
            
            # 更新前端数据
            frontend_data.update({
                'majors': major_names,
                'majors_by_category': major_categories,
                'target_majors': major_categories
            })
            
            # 保存更新后的前端数据
            with open(frontend_data_file, 'w', encoding='utf-8') as f:
                json.dump(frontend_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"前端数据文件已更新: {frontend_data_file}")
            logger.info(f"专业总数: {len(major_names)}")
            logger.info(f"专业分类数: {len(major_categories)}")
            
        except Exception as e:
            logger.error(f"生成前端数据时出错: {str(e)}")
            raise

def main():
    """主函数"""
    try:
        # 设置文件路径
        base_path = Path(__file__).parent.parent.parent
        input_file = base_path / "data" / "processed_majors.json"
        output_file = base_path / "data" / "cleaned_majors.json"
        frontend_data_file = base_path / "data" / "frontend_data.json"
        
        # 创建处理器
        processor = MajorDataProcessor()
        
        # 处理专业数据
        logger.info("开始处理专业数据...")
        stats = processor.process_majors_data(str(input_file), str(output_file))
        
        # 生成前端数据
        logger.info("开始生成前端数据...")
        processor.generate_frontend_data(str(output_file), str(frontend_data_file))
        
        logger.info("数据处理完成！")
        return stats
        
    except Exception as e:
        logger.error(f"数据处理失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 