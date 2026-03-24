"""
工具模型
"""
from sqlalchemy import Column, Integer, String, JSON, Enum, DateTime, Index
from sqlalchemy.orm import relationship
from app.extensions import Base
from app.utils.datetime_utils import get_beijing_time
import json


class Tool(Base):
    """
    工具模型
    
    存储工具的配置信息，包括名称、描述、Schema、状态等
    """
    __tablename__ = 'tools'
    

    id = Column(Integer, primary_key=True, autoincrement=True, comment='工具ID')
    name = Column(String(30), nullable=False, index=True, comment='工具名称（允许重复）')
    description = Column(String(100), nullable=True, comment='工具描述')
    icon = Column(String(255), nullable=True, comment='工具图标URL')
    schema = Column(JSON, nullable=False, comment='工具Schema配置')
    status = Column(
        Enum('enabled', 'disabled', name='tool_status'),
        nullable=False,
        default='enabled',
        index=True,
        comment='工具状态: enabled-启用, disabled-停用'
    )
    creator = Column(String(50), nullable=True, comment='创建人')
    created_at = Column(DateTime, nullable=False, default=get_beijing_time, comment='创建时间（北京时间）')
    updated_at = Column(
        DateTime,
        nullable=False,
        default=get_beijing_time,
        onupdate=get_beijing_time,
        comment='更新时间（北京时间）'
    )
    categories = relationship(
        'ToolCategory',
        secondary='tool_category_associations',
        back_populates='tools',
        lazy='dynamic'
    )
    __table_args__ = (
        Index('idx_name_status', 'name', 'status'),
        {'comment': '工具配置表'}
    )
    
    def to_dict(self, include_schema=False):
        """
        转换为字典
        
        Args:
            include_schema: 是否包含完整的schema配置
            
        Returns:
            字典格式的工具信息
        """
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'status': self.status,
            'creator': self.creator,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        if include_schema:
            if isinstance(self.schema, str):
                try:
                    parsed = json.loads(self.schema)
                    data['schema'] = parsed if isinstance(parsed, dict) else self.schema
                except Exception:
                    data['schema'] = self.schema
            else:
                data['schema'] = self.schema if self.schema is not None else {}
        
        return data
    
    def is_enabled(self):
        """判断工具是否启用"""
        return self.status == 'enabled'
    
    def enable(self):
        """启用工具"""
        self.status = 'enabled'
    
    def disable(self):
        """停用工具"""
        self.status = 'disabled'
    
    def __repr__(self):
        return f'<Tool {self.id}: {self.name} ({self.status})>'

